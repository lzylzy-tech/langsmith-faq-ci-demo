"""每次 PR 都执行：本地静态检查，无 API Key、无大模型费用。"""
import pytest
from langsmith import testing as t

from app import load_system_prompt


@pytest.mark.langsmith
def test_critical_refund_policy_is_present():
    prompt = load_system_prompt()
    t.log_inputs({"rule": "退款到账时间和申请期限"})
    t.log_reference_outputs({"contains": ["7天", "3个工作日"]})
    t.log_outputs({"prompt": prompt})
    assert "7天" in prompt, "退款申请期限被删改了"
    assert "3个工作日" in prompt, "退款到账时间被删改了"


@pytest.mark.langsmith
def test_unknown_question_rule_is_present():
    prompt = load_system_prompt()
    t.log_inputs({"rule": "未知问题不能编造"})
    t.log_reference_outputs({"should_forbid_fabrication": True})
    t.log_outputs({"prompt": prompt})
    assert "不能编造" in prompt
    assert "不知道" in prompt or "无法确认" in prompt
