# coding=utf-8
from chromadb.utils import embedding_functions
from autogen import AssistantAgent, UserProxyAgent
import autogen
import shutil
import openai
import os

os.environ["TAVILY_API_KEY"] = "" #input your api_key
os.environ["OPENAI_API_KEY"] = "" #input your api_key
openai.api_key = "" #input your api_key

def get_code(json_data,name):
    res = ''
    for item in json_data:
        try:
            if item.get('name') == name:
                res = res + item.get('content')
        except:
            res = res + ""
    return res
#外部prompt读入函数
def get_prompt_from_file(file_path):
    with open(file_path, 'r', encoding='UTF-8') as file:
        return file.read()

def read_line(string,int):
    lines = string.split("\n")
    line = lines[int]
    return line

#autogen配置部分
config_list = [{'model': 'gpt-4-turbo-preview', 'api_key': ''},] #input your api_key
llm_config={
    "seed": 42,  
    "config_list": config_list,
    "temperature": 0.3,
}

smvbugany = AssistantAgent(
    name="SMVBug_analyse",
    system_message="你是一位在SMV和形式验证领域拥有丰富经验的专家。你善于利用用户提供的反例分析引起错误的原因。你只会给出如何修改SMV模型的建议，但不会给出SMV代码。",
    llm_config=llm_config,
)
smvdebug = AssistantAgent(
    name="SMVDebug",
    system_message="你是一位在SMV和形式验证领域拥有丰富经验的专家。你善于利用错误分析的结果和用户提供的反例对SMV模型进行修改。修改SMV模型使得其符合CTL约束，保证生成的SMV语法正确，修改过程中注意初始状态和是否符合约束，不要使用不存在的函数",
    llm_config=llm_config,
)
user_proxy = UserProxyAgent(
    name="user_proxy",
    system_message="A human admin.",  # 系统消息是用户给代理的角色
    code_execution_config={"last_n_messages":2, "work_dir":"groupchat","use_docker": False},
    human_input_mode="ALWAYS"
)

case = input("input case name：\n")
plc_req = get_prompt_from_file(os.path.join('PLC_requirement', case+'.txt'))  #the requirement for code  replace the name with the workdir you use
smv_model = get_prompt_from_file(os.path.join('pattern_SMV_design', case+'.txt'))  #the SMV model 
# usecase_design = get_prompt_from_file(os.path.join('jinghua_PLC_requirement', case+'.txt'))  #the Refinement requirement for code  this is for m4 method 


print('input Counterexample:\n')  #input the Counterexample by nusmv
arr = []
while True:
    s = input()
    if s == '':
        break
    arr.append(s)
Counterexample = ' '.join(arr)

fixchat = autogen.GroupChat(agents=[user_proxy,smvbugany,smvdebug], messages=[],max_round=100)  # 群聊 最大的chat轮次
bugmanager = autogen.GroupChatManager(groupchat=fixchat, llm_config=llm_config)  # 管理员，可以与之交互

SMV_debug = user_proxy.initiate_chat(
        bugmanager,message='遵循以下步骤修复SMV模型:SMVBug_analyse分析引起错误的原因(仅给出分析结果，不要修改SMV)-SMVDebug根据反例和分析结果修改SMV模型(返回完整的SMV模型)\n'
        'Counterexample:'+Counterexample
        +'\nSMV requirement:' + plc_req
        # +'use_case'+usecase_design   #this is for the m4 method,  uncomment it if you want use m4 method
        +'\nSMV code:\n' +smv_model)
ST_code = get_code(SMV_debug.chat_history, 'SMVDebug')
print(ST_code)
with open('SMV_design.txt', 'w') as f:
    f.write(ST_code)




