"""只有可信 CI 执行：读取已有 LangSmith 冻结数据集，调用真实 LLM。"""
import os
import re

from dotenv import load_dotenv
from langsmith import Client

from app import answer

load_dotenv()

DATASET_NAME = "faq-regression-v1"
DATASET_VERSION = "ci-regression-v2"
EXPECTED_QUESTION = "退款多久到账？"


def grade_critical_policy(inputs, outputs, reference_outputs):
    """明确检查本课唯一的核心事实，不做脆弱的整句 Exact Match。"""
    question = inputs["question"]
    expected = reference_outputs["answer"]
    actual = outputs.get("answer", "")
    if question != EXPECTED_QUESTION or "3个工作日" not in expected:
        raise ValueError("出现未审核或不适用于此评分器的样例，先停下检查数据集")
    text = re.sub(r"\s+", "", actual)
    correct = ("3个工作日" in text or "三个工作日" in text)
    wrong = ("5个工作日" in text or "五个工作日" in text)
    return {"key": "critical_policy", "score": int(correct and not wrong)}


def test_real_llm_regression_on_frozen_dataset():
    assert os.getenv("LANGSMITH_API_KEY"), "缺少 LANGSMITH_API_KEY"
    assert os.getenv("OPENAI_API_KEY"), "缺少 OPENAI_API_KEY"
    client = Client()
    examples = list(client.list_examples(dataset_name=DATASET_NAME, as_of=DATASET_VERSION))
    assert len(examples) == 1, "练习要求冻结版本正好包含1条人工审核的退款到账样例"
    assert examples[0].inputs.get("question") == EXPECTED_QUESTION
    assert "3个工作日" in examples[0].outputs.get("answer", "")

    results = client.evaluate(
        answer,
        data=examples,
        evaluators=[grade_critical_policy],
        experiment_prefix="github-actions-faq-regression",
        metadata={
            "revision": os.getenv("GITHUB_SHA", "local"),
            "dataset_version": DATASET_VERSION,
        },
        max_concurrency=1,
        blocking=True,
    )
    rows = list(results)
    assert len(rows) == len(examples), "运行样例数量不符，不能放行"

    failures = []
    for row in rows:
        scores = [
            item.score
            for item in row["evaluation_results"]["results"]
            if item.key == "critical_policy"
        ]
        assert len(scores) == 1 and scores[0] is not None, "缺少有效评分，不能放行"
        if scores[0] != 1:
            failures.append({
                "question": row["example"].inputs.get("question"),
                "output": row["run"].outputs,
                "score": scores[0],
            })

    assert not failures, f"发现回归错误：{failures}"
