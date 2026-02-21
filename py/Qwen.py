from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage
import sys

# 初始化 Qwen 模型（默认使用 qwen-max）
chat = ChatTongyi(
    model="qwen-max",          # 可选: qwen-plus, qwen-turbo, qwen-max
    dashscope_api_key="sk-32e888379b684dccb6ba1d540aab4284",  # 替换为你的 API Key
    streaming=True  # 启用流式输出
)

print("欢迎使用 Qwen AI 对话系统！")
print("输入 'exit'、'quit' 或 'q' 退出程序\n")

# 持续对话循环
while True:
    # 读取用户输入 ，回车键结束
    user_input = input("你: ")
    
    # 检查退出命令
    if user_input.lower() in ['exit', 'quit', 'q']:
        print("再见！")
        break
    
    # 如果输入为空，跳过
    if not user_input.strip():
        continue
    
    try:
        # 打印 AI 前缀
        print("AI: ", end='', flush=True)
        
        # 使用流式输出，逐字显示
        for chunk in chat.stream([HumanMessage(content=user_input)]):
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end='', flush=True)
                sys.stdout.flush()
        # 换行
        print("\n")
    except Exception as e:
        print(f"\n错误: {e}\n")