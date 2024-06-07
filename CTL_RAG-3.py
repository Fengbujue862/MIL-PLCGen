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
llm = OpenAI(model="gpt-4-1106-preview", temperature=0.3)
warnings.filterwarnings('ignore')
api_key="" #input your api_key
openai.api_key = api_key

ctl_folder_path = './ctl_file'
ctl_pdf_files = glob.glob(os.path.join(ctl_folder_path, '*.pdf'))
ctl_documents = SimpleDirectoryReader(input_files=ctl_pdf_files).load_data()
ctl_document = Document(text="\n\n".join([doc.text for doc in ctl_documents]))
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
    embed_model="local:BAAI/bge-large-en-v1.5",
    sentence_window_size=3,
    save_dir="ctl_index",
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


ctl_index = build_sentence_window_index(
    [ctl_document],
    llm=OpenAI(model="gpt-4-1106-preview", temperature=0.1),
    save_dir="ctl_index",
)
ctl_query_engine = get_sentence_window_query_engine(ctl_index, similarity_top_k=6)
# 定义查询


usecase_design = get_prompt_from_file('PLC_design.txt')
ctl_output = get_prompt_from_file('ctl_output_formal.txt')
raw_requirement = get_prompt_from_file("requirment.txt")
verif_prompt = get_prompt_from_file("verification_design.txt")
patterns_file = get_prompt_from_file("patterns_p1_design.txt")

ctl_str0 = "不要用中文，注意变量设计符合规范，请根据精化后需求进行分析后仅输出基于其用例的约束（注意将每个用例的事件流总结，包括基本流和备选流，并且结合用例场景和各种条件都整合成一个独立约束）对应的CTL/LTL（一个约束对应一个CTL/LTL,语法需要符合SMV模型检验），并且每条CTL/LTL之前标明对应的约束类型:"+'CTL设计原则(先判断需要用到哪些，再输出需要的约束类型):'+verif_prompt+"精化后的需求："+usecase_design
ctl_str = "请根据原始的需求输出基于其本身的约束进行适当分析,原始需求文本中的每一个约束都要有一个CTL或LTL的形式（用验证smv模型的CTL/LTL语句来实现，不要用别的符号），不要中文回答:"+"原始需求："+raw_requirement+"CTL设计原则(先判断约束的类型，再给出对应的CTL或LTL范式)："+verif_prompt
ctl_str1 = "不要用中文，且变量设计符合规范，一个事件流若包含多个事件则必须拆分，变量也必须尽量拆分，不做合并处理，请根据CTL/LTL知识库以及patterns文件中的内容设计的性质规约例如：{1},{2}等，注意不能有遗漏，每个变量名称单独定义的同时考虑互斥问题【如关灯，开灯即作为互斥变量】，一条patterns的对应一条CTL，注意最后结果仅含CTL范式以及对应patterns的类型（记得一定要去掉最前面的“EoC”或“PLC_END”,'PLC_START',等关键词；记得用尽量强的约束描述。如AG,AX，AF等，视情况决定，不要用GBK格式）：" + "patterns文件" + patterns_file + "格式文件："+ ctl_output
user_input = input("请输入0或1来选择查询字符串（0为ctl_str0，1为ctl_str1）：")
if user_input == '0':
    query_str = ctl_str0
    file_name = 'ctl_design0.txt'
elif user_input == '1':
    query_str = ctl_str1
    file_name = 'ctl_design1.txt'
else:
    print("无效输入，请输入0或1。")
    exit()

# Use the query engine to execute the query
response = ctl_query_engine.query(query_str)

# Print the query results
print(response)

# Save the response to a file based on the user's choice
with open(file_name, 'w') as f:
    f.write(str(response))