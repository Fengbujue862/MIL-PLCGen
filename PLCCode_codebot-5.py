import os
import warnings
from autogen import ConversableAgent
from autogen import  UserProxyAgent
import  chardet

warnings.filterwarnings('ignore')
os.environ["OPENAI_API_KEY"] = "" #input your api_key
OPENAI_API_KEY= "" #input your api_key
Coder = ConversableAgent(
    "coder",
    system_message="You are a professional PLC programmer with years of programming experience. Also proficient in various PLC programming languages and tools, and are capable of designing, developing, and optimizing PLC programs according to actual requirements.",
    llm_config={"config_list": [{"model": "gpt-4-1106-preview", "temperature": 0.3, "api_key": os.environ.get("OPENAI_API_KEY")}]},
    human_input_mode="NEVER",  
)
user_proxy = UserProxyAgent(
    name="user_proxy",
    system_message="A human admin.",
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
req_temp = ("Please note that the following are separate requirements. Follow the steps below to generate the code: "
            "observe the original requirements, check and analyze the requirements and constraints–design and then generate ST code, "
            "write the code based on the refined requirements and the corresponding CTL or LTL constraints design documents,"
            " and strictly adhere to the rules of the syntax file. "
            "Here are the relevant files, please refer to the template or requirements to generate the related files and save them.\n")
usecase_prompt = get_prompt_from_file("PLC_design.txt") # the Refinement requiremnt
raw_requirement_prompt = get_prompt_from_file("requirment.txt") # the origin requirement
plc_prompt = get_prompt_from_file("st_rules.txt")
ctl_prompt = get_prompt_from_file("ctl_design1.txt")
#response1 = user_proxy.initiate_chat(elysia, message=req_temp+"\n原始需求：\n"+raw_requirement_prompt+"\nUSE_CASE的RAG提示：\n"+usecase_prompt+"\n约束设计：\n"+ctl_prompt+"\n语法文件：\n"+plc_prompt)
response2= user_proxy.initiate_chat(Coder, message=req_temp+"requirment file：\n"+raw_requirement_prompt+"\nCTL/LTL designs file：\n"+ctl_prompt+"\n syntax file：\n"+plc_prompt)
Coder.reset()
user_proxy.reset()

