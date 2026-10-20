"""第6课：把 Prompt 存成文件，以便通过 Git 追踪修改。"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
# llm = init_chat_model(f"openai:{MODEL_NAME}")
# 加载环境变量
load_dotenv()
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "faq_system.txt"
MODEL_NAME=os.getenv("MODEL_NAME")

def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def answer(inputs: dict) -> dict:
    """真实 LLM 目标函数；仅在 live CI 测试中调用。"""
    prompt = ChatPromptTemplate.from_messages(
        [("system", load_system_prompt()), ("human", "{question}")]
    )
    # model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"))
    model = init_chat_model(f"openai:{MODEL_NAME}")
    chain = prompt | model | StrOutputParser()
    return {"answer": chain.invoke({"question": inputs["question"]})}
