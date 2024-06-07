import warnings
import os
import chardet
import glob
import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,ServiceContext,StorageContext
from llama_index.core import Document
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.llms.openai import OpenAI
from llama_index.core import load_index_from_storage
llm = OpenAI(model="gpt-4-0125-preview", temperature=0.2)
warnings.filterwarnings('ignore')
api_key="" #input your api_key
openai.api_key = api_key

folder_path = 'D:/pipeline_script/smv_file' #replace with the SMV_file
# 使用glob模式匹配文件夹中的所有PDF文件
pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
# 使用SimpleDirectoryReader读取所有PDF文件
documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))

def get_prompt_from_file(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()
def build_sentence_window_index(
    documents,
    llm,
    embed_model="local:BAAI/bge-small-en-v1.5",
    sentence_window_size=3,
    save_dir="usecase_index",
):
    # 创建句子窗口的node parser
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=sentence_window_size,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    sentence_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
        node_parser=node_parser,
    )
    if not os.path.exists(save_dir):
        sentence_index = VectorStoreIndex.from_documents(
            documents, service_context=sentence_context
        )
        sentence_index.storage_context.persist(persist_dir=save_dir)
    else:
        sentence_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=save_dir),
            service_context=sentence_context,
        )

    return sentence_index


def get_sentence_window_query_engine(
    sentence_index, similarity_top_k=6, rerank_top_n=2
):
    # define postprocessors
    postproc = MetadataReplacementPostProcessor(target_metadata_key="window")
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
    )

    sentence_window_engine = sentence_index.as_query_engine(
        similarity_top_k=similarity_top_k, node_postprocessors=[postproc, rerank]
    )
    return sentence_window_engine

index = build_sentence_window_index(
    [document],
    llm=OpenAI(model="gpt-4-0125-preview", temperature=0.3),
    save_dir="smv_index",
)
query_engine = get_sentence_window_query_engine(index, similarity_top_k=6)
# 定义查询

case = input("input case name：\n")

plc_req = get_prompt_from_file(os.path.join('PLC_requirement', case+'.txt'))  #the requirement for code  replace the name with the workdir you use
# usecase_design = get_prompt_from_file(os.path.join('usecase_design', case))  #the Refinement requirement for code  this is for m4 method 
ctl_design = get_prompt_from_file(os.path.join('patterns_ctl_design', case+'.txt'))  #the CTL for case

query_str = "请根据下面的需求和CTL约束，参考知识库生成符合CTL约束的完整的SMV模型(SMV模型要注意语法正确),\n"+"需求:"+ plc_req+'CTL:'+ctl_design  #this is the m3 query_str
# query_str = "请根据下面的需求以及其用例和CTL约束，参考知识库生成符合CTL约束的完整的SMV模型(SMV模型要注意语法正确),\n"+"需求:"+ plc_req+"用例设计:"+usecase_design+'CTL:'+str(ctl_response)  #this is the m4 query, uncomment it and comment m3 query if you want use m4 method
# 使用查询引擎执行查询
response = query_engine.query(query_str)

# 打印查询结果
print(response)
with open(os.path.join('pattern_SMV_design', case+'.txt'), 'w') as f:  #replace with the output workdir
    f.write(str(response))
