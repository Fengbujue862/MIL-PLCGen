# coding=utf-8
import subprocess
import warnings
from chromadb.utils import embedding_functions
from autogen import AssistantAgent, UserProxyAgent
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.tools.tavily_search import TavilySearchResults
from langchain.chains.conversation.memory import ConversationBufferMemory
from tavily import TavilyClient
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,ServiceContext,StorageContext
from llama_index.core import Document
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.llms.openai import OpenAI
from llama_index.core import load_index_from_storage
import autogen
import shutil
import openai
import os

os.environ["OPENAI_API_KEY"] = ""#input your api_key
openai.api_key = "" #input your api_key
llm = OpenAI(model="gpt-4-0125-preview", temperature=0.3)
warnings.filterwarnings('ignore')
api_key="" #input your api_key
openai.api_key = api_key


plcverif = "D:\plcverif_cli\eclipsec.exe"
req_pattern = ''
params1 = ''
params3 = ''
params4 = ''
state = 0
error_mes = ''
#外部prompt读入函数
def get_prompt_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_line(string,int):
    lines = string.split("\n")
    line = lines[int]
    return line

def get_code(json_data,name):
    res = ''
    for item in json_data:
        try:
            if item.get('name') == name:
                res = res + item.get('content')
        except:
            res = res + ""
    return res


#autogen配置部分
config_list = [{'model': 'gpt-4-0125-preview', 'api_key': ''},]#input your api_key
llm_config={
    "seed": 42,  #为缓存做的配置
    "config_list": config_list,
}

plccoder = AssistantAgent(
    name="Coder",
    system_message="你是一位专业的PLC程序员，拥有多年的编程经验。你熟练掌握各种PLC编程语言和工具，能够根据实际需求设计、开发和优化PLC程序。",
    llm_config=llm_config,
)
plcexpert = AssistantAgent(
    name="PLCExpert",
    system_message="你是一位在PLC和计算机领域拥有丰富经验的专家。你善于运用后退提问和思维树等分析方法来深入理解问题并找到解决方案。",
    llm_config=llm_config,
)
plcbugany = AssistantAgent(
    name="PLCBug_analyse",
    system_message="你是一位在PLC和计算机领域拥有丰富经验的专家。你善于利用编译器的错误信息或用户提供的反例判断代码的错误类型，针对每个错误信息分析引起错误的原因,不要给出代码",
    llm_config=llm_config,
)
plcdebug = AssistantAgent(
    name="PLCDebug",
    system_message="你是一位在PLC和计算机领域拥有丰富经验的专家。你善于利用PLCBug_analyse的输出，编译器的错误信息或用户提供的反例对代码进行修复。最终输出修正后的ST代码",
    llm_config=llm_config,
)
user_proxy = UserProxyAgent(
    name="user_proxy",
    system_message="A human admin.",  # 系统消息是用户给代理的角色
    code_execution_config={"last_n_messages":2, "work_dir":"groupchat","use_docker": False},
    human_input_mode="ALWAYS"
)

groupchat = autogen.GroupChat(agents=[user_proxy,plcexpert,plccoder], messages=[], max_round=100) # 群聊 最大的chat轮次
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)  #管理员，可以与之交互
#autogen配置结束


case = input("input case name：\n")
plc_req = get_prompt_from_file(os.path.join('PLC_requirement', case+'.txt'))
st_code = get_prompt_from_file(os.path.join('jinghua_st_design', case+'.txt'))
#usecase_design = get_prompt_from_file(os.path.join('jinghua_PLC_requirement', case+'.txt')) #the Refinement requirement for code  this is for m4 method 
# 获取模板文件内容

file_path_plc = 'st_rules.txt'
plc_prompt = get_prompt_from_file(file_path_plc)
conform = 'y'


type = '4'
if conform == 'y':
    while type != '0':
        type = input("END input 0,syntax error input 1,counterexample input 2\n")
        if type == '1':
            fixchat = autogen.GroupChat(agents=[user_proxy,plcbugany,plcdebug], messages=[],max_round=100)  # 群聊 最大的chat轮次
            bugmanager = autogen.GroupChatManager(groupchat=fixchat, llm_config=llm_config)  # 管理员，可以与之交互
            print('input syntax error:\n')
            arr = []
            while True:
                s = input()
                if s == '':
                    break
                arr.append(s)
            syntax_error = ' '.join(arr)
            ST_debug = user_proxy.initiate_chat(
                    bugmanager,
                    message='请注意，遵循以下步骤修复ST代码:PLCBug_analyse分析语法错误原因(仅分析错误原因,不要生成ST代码)-PLCDebug根据错误原因修改代码.\n'
                    'syntax error:'+syntax_error
                    +'\nPLC requirement:' + plc_req
                    +'\nPLC ST code:\n' +st_code+
                    '\nonly return the fixed ST code')
            ST_code = get_code(ST_debug.chat_history, 'PLCDebug')
            print(ST_code)
            with open('source.scl', 'w') as f:
                f.write(ST_code)
            conform = input("代码已更新，请确定py文件同目录下source.scl文件内容,无误后输入y\n")
        elif type == '2':
            fixchat = autogen.GroupChat(agents=[user_proxy,plcbugany,plcdebug], messages=[],max_round=100)  # 群聊 最大的chat轮次
            bugmanager = autogen.GroupChatManager(groupchat=fixchat, llm_config=llm_config)  # 管理员，可以与之交互
            print('input Counterexample:\n')
            arr = []
            while True:
                s = input()
                if s == '':
                    break
                arr.append(s)
            Counterexample = ' '.join(arr)
            ST_debug = user_proxy.initiate_chat(
                    bugmanager,message='请注意，参考用例,遵循以下步骤修复ST代码:PLCBug_analyse分析逻辑错误原因(仅分析错误原因,不要生成ST代码)-PLCDebug根据错误原因修改代码'
                    'Using Counterexample to fix code errors.\n'
                    'Counterexample:'+Counterexample
                    +'\nPLC requirement:' + plc_req
                    +'\nPLC ST code:\n' +st_code+
                    #'\nUse Case:\n' + usecase_design + #this is for m4 , uncomment it if you want use m4 method
                    '\nonly return the fixed ST code')
            ST_code = get_code(ST_debug.chat_history, 'PLCDebug')
            print(ST_code)
            with open('source.scl', 'w') as f:
                f.write(ST_code)
            print(ST_debug)
            conform = input("代码已更新，请确定py文件同目录下source.scl文件内容,无误后输入y\n")
        elif type == '0':
            print('代码生成完毕')
            exit(0)
else:
    print('用户主动退出')
    exit(0)
