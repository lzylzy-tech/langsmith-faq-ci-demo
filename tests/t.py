"""只有可信 CI 执行：读取已有 LangSmith 冻结数据集，调用真实 LLM。"""
import os
import re

from dotenv import load_dotenv
from langsmith import Client

# from app import answer

load_dotenv()

DATASET_NAME = "faq-regression-v1"
DATASET_VERSION = "ci-regression-v2"
EXPECTED_QUESTION = "退款多久到账？"
def test_real_llm_regression_on_frozen_dataset():
    assert os.getenv("LANGSMITH_API_KEY"), "缺少 LANGSMITH_API_KEY"
    assert os.getenv("OPENAI_API_KEY"), "缺少 OPENAI_API_KEY"
    client = Client()
    examples = list(client.list_examples(dataset_name=DATASET_NAME, as_of=DATASET_VERSION))
    print(examples)
test_real_llm_regression_on_frozen_dataset()