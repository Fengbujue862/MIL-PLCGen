import warnings
import os
import chardet
import glob
import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, StorageContext
from llama_index.core import Document
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.llms.openai import OpenAI
from llama_index.core import load_index_from_storage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent

llm = OpenAI(model="gpt-4-1106-preview", temperature=0.3)
warnings.filterwarnings('ignore')
api_key = "" #input your api_key
openai.api_key = api_key

folder_path = './use_case file'
pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))


def build_sentence_window_index(
        documents,
        llm,
        embed_model="local:BAAI/bge-large-en-v1.5",
        sentence_window_size=4,
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
    llm=OpenAI(model="gpt-4-1106-preview", temperature=0.1),
    save_dir="usecase_index",
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


plc_req = get_prompt_from_file("requirment.txt")
use_case_req = get_prompt_from_file("use_case.txt")
#error_req = get_prompt_from_file("error.txt")
# design_file = get_prompt_from_file("PLC_design.txt")
query_str = "Please provide me with a detailed requirements analysis and use case design based on the following issue requirements. Remember not to give me code; instead, conduct a standard, comprehensive use case analysis based solely on the knowledge base, considering all scenarios (including basic flow and alternative flow) with clear initial values and interaction methods. Appropriate expansion is allowed as long as the original requirements are fully met："+plc_req+"Use case standard："+use_case_req


response = query_engine.query(query_str)

# 打印查询结果
print(response)
with open('PLC_design.txt', 'w') as f:
    f.write(str(response))
