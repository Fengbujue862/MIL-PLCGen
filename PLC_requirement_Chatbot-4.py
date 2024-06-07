import os
import warnings
from autogen import ConversableAgent
from autogen import  UserProxyAgent
import  chardet

warnings.filterwarnings('ignore')
os.environ["OPENAI_API_KEY"] = "" #input your api_key
OPENAI_API_KEY= "" #input your api_key
coder = ConversableAgent(
    "coder",
    system_message="你是一位计算机形式验证以及建模领域专家级程序员，拥有多年的编程经验和丰富的模型设计验证技术。你熟练掌握各种CLT/LTL以及SMV工具，能够根据实际需求设计CTL语句或SMV模型",
    llm_config={"config_list": [{"model": "gpt-4-1106-preview", "temperature": 0.3, "api_key": os.environ.get("OPENAI_API_KEY")}]},
    human_input_mode="NEVER",  
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
coder.reset()

req_temp = "请注意，以下是精化前的原始需求文件以及根据其生成的patterns约束文件，帮我分析可能的错误，并且协助修改。遵循以下步骤生成：分析精化前的需求和对应的patterns等信息来检查patterns约束设计错误，下面是相关文件，请参考模板或需求生成相关文件并保存\n"

raw_requirement_prompt = get_prompt_from_file("requirment.txt") # code requirement
patterns_prompt2 = get_prompt_from_file("patterns_p1_design.txt") # the pattern design
patterns_file = get_prompt_from_file("pattern_id_explain.txt")  # the formal pattern

response = user_proxy.initiate_chat(coder, message=req_temp+"\n原始需求：\n"+raw_requirement_prompt+"\nPatterns文件:\n"+patterns_prompt2+"\nPatterns设计格式:\n"+patterns_file)



