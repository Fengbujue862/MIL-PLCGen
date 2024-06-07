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
llm = OpenAI(model="gpt-4-1106-preview", temperature=0.1)
warnings.filterwarnings('ignore')
api_key="" #input your api_key
openai.api_key = api_key

folder_path = './plcverif_file'
pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))

def build_sentence_window_index(
    documents,
    llm,
    embed_model="local:BAAI/bge-large-en-v1.5",
    sentence_window_size=3,
    save_dir="plcverif_index",
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
    llm=OpenAI(model="gpt-4-1106-preview", temperature=0.1),
    save_dir="plcverif_index",
)
query_engine = get_sentence_window_query_engine(index, similarity_top_k=6)


# 定义查询
def get_prompt_from_file(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()



code_file = get_prompt_from_file("llm_output.txt")
usecase_file = get_prompt_from_file("PLC_design.txt")
patterns_requirement = get_prompt_from_file("pattern_id_explain.txt")
requirement_file = get_prompt_from_file("requirment.txt")
verif_file = get_prompt_from_file("verification_design.txt")
patterns_design_example = get_prompt_from_file("patterns_design_example.txt")
query_str1 = "英文回答，请根据你的知识库对于plcverif的理解以及结合实际得到的精化需求的用例，要求设计出符合plcverif语法且涵盖整个需求精化文件中的简要说明以及全部用例设计（不可遗漏每一个用例的事件流中的全部信息，包括基本流、备选流以及特殊需求；且都要注意结合前置与后置条件的限制，要求基本流、备选流以及特殊需求都存在一个对应的pattern输出，每个变量名单独定义的同时考虑互斥问题【如关灯，开灯即作为互斥变量】，填空完成给定文件中每一个patterns里的{1}，{2}等部分。）分支的用于形式化检验patterns实例，并且注意，必须是参考收到的精化后的需求以及patterns生成要求给出，先识别patterns的类型再给出，可以有重复类型的patterns，但务必将每个用例都要转成patterns。以下是精化后需求："+ usecase_file + "patterns生成要求：" + patterns_requirement + "patterns生成参考模板："+ patterns_design_example
query_str2 = "英文回答，请根据你的知识库对于plcverif的理解以及结合实际得到的原始需求的用例，要求设计出符合plcverif语法且涵盖整个原始需求文件中的约束，填空完成给定文件中每一个patterns里的{1}，{2}等部分。并且注意，必须是参考收到的原始需求以及patterns的生成要求给出，先识别patterns的类型再给出，数量需要和原始约束数目一致，不能随意增加，且务必将每个用例都要转成patterns。以下是原始需求：" + requirement_file + "patterns生成要求：" + patterns_requirement + "patterns生成参考模板："+ patterns_design_example

response = query_engine.query(query_str1)
#agent.reset()
# 打印查询结果
print(response)
with open('patterns_p1_design.txt', 'w') as f:
    f.write(str(response))