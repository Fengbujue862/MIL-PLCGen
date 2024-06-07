import os
import warnings
from autogen import ConversableAgent
from autogen import  UserProxyAgent
import  chardet

warnings.filterwarnings('ignore')
os.environ["OPENAI_API_KEY"] = ""  #input your api_key
OPENAI_API_KEY= ""  #input your api_key
elysia = ConversableAgent(
    "coder",
    system_message="你是一位专业的PLC程序员，拥有多年的编程经验。你熟练掌握各种PLC编程语言和工具，能够根据实际需求设计、开发和优化PLC程序",
    llm_config={"config_list": [{"model": "gpt-4-1106-preview", "temperature": 0.3, "api_key": os.environ.get("OPENAI_API_KEY")}]},
    human_input_mode="NEVER",  #  ask for human input.
)
user_proxy = UserProxyAgent(
    name="user_proxy",
    system_message="A human admin.",  # 系统消息是用户给代理的角色
    code_execution_config={"last_n_messages":2, "use_docker": False},
    human_input_mode="ALWAYS"
)
#获取代码
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
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()

def read_line(string,int):
    lines = string.split("\n")
    line = lines[int]
    return line
#prompt设置
case = input("input case name：\n")
raw_requirement_prompt = get_prompt_from_file(os.path.join('PLC_requirement', case+'.txt'))  #the requirement for code  replace the name with the workdir you use
# plc_req = get_prompt_from_file(os.path.join('jinghua_PLC_requirement', case+'.txt'))  #the Refinement requirement for code  this is for m4 method 
smv_model = get_prompt_from_file(os.path.join('pattern_SMV_design', case+'.txt'))   #the SMV model for code
plc_prompt = get_prompt_from_file("st_errors.txt")  #prompt for syntax
req_temp = "遵循以下步骤生成ST代码：根据需求，参考SMV模型(仅作为参考)生成ST代码，要遵守语法文件的语法规则限制，下面是相关文件，请参考模板或需求生成相关文件并保存\n"  #this is the m3 req_temp
# req_temp = "遵循以下步骤生成ST代码：根据原始需求以及USE_CASE设计，参考SMV模型(仅作为参考)生成ST代码，要遵守语法文件的语法规则限制，下面是相关文件，请参考模板或需求生成相关文件并保存\n"  #this is the m4 req_temp  uncomment it and comment m3 query if you want use m4 method

response1 = user_proxy.initiate_chat(elysia, message=req_temp+"\n需求：\n"+raw_requirement_prompt+"\nSMV模型：\n"+smv_model+"\n语法文件：\n"+plc_prompt)
ST_code=get_code(response1.chat_history, 'elysia')
print(ST_code)
elysia.reset()
user_proxy.reset()

