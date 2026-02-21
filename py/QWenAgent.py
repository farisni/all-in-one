# interactive_agent.py
import os
from langchain_community.chat_models import ChatTongyi
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage

os.environ["DASHSCOPE_API_KEY"] = "sk-32e888379b684dccb6ba1d540aab4284"

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"{location} is sunny and 25°C."



# 初始化
llm = ChatTongyi(model="qwen-plus", temperature=0)
tools = [get_weather]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful travel assistant. Only use the tool when asked about weather."),
    MessagesPlaceholder("chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])

agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)

# 🧠 手动管理对话历史（这就是 memory）
chat_history = []

print("🌤️ 旅行助手已启动！输入 'quit' 退出。\n")

while True:
    try:
        # 获取用户输入
        user_input = input("👤 > ").strip()
        if not user_input or user_input.lower() in ["quit", "exit", "q"]:
            print("👋 再见！")
            break

        # 调用 Agent
        result = executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })

        # 更新历史
        chat_history.extend([
            HumanMessage(content=user_input),
            AIMessage(content=result["output"])
        ])

        # 输出 AI 回复
        print(f"🤖 {result['output']}\n")

    except KeyboardInterrupt:
        print("\n👋 被中断，再见！")
        break
    except Exception as e:
        print(f"❌ 错误: {e}\n")