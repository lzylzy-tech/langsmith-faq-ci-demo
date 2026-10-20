# 第6课：LangSmith + pytest + GitHub Actions

## 先决条件

- 已有 `faq-regression-v1` Dataset，包含在第4课人工审核的一条问题 `退款多久到账？`，参考答案含 `3个工作日`。
- 到该 Dataset 的 Examples 页面，把仅有这一条样例的版本标记为 `ci-regression-v1`。如果已有额外样例，请先创建符合要求的单例版本，或自行扩展评分逻辑。
- 在 GitHub Repo 的 `Settings → Secrets and variables → Actions` 新建 Secrets：`LANGSMITH_API_KEY`, `OPENAI_API_KEY`。

## 本地准备

```bash
python -m pip install -r requirements.txt
```

在本地放置 `.env` 文件（不要提交 Git）：

```
LANGSMITH_API_KEY=...
OPENAI_API_KEY=...
```

## 快速测试：无模型费用

macOS/Linux:

```bash
LANGSMITH_TEST_TRACKING=false python -m pytest -q tests/test_prompt.py
```

Windows PowerShell:

```powershell
$env:LANGSMITH_TEST_TRACKING='false'
python -m pytest -q tests/test_prompt.py
```

把 `prompts/faq_system.txt` 中 `3个工作日` 改为 `5个工作日` 再运行，测试应失败。改回后测试应通过。

## 真实回归测试：需要两种 API Key 和模型额度

```bash
python -m pytest -q tests/test_live_regression.py
```

它会读取 `faq-regression-v1` 的 `ci-regression-v1` 冻结版本，产生一次 LangSmith 实验，并检查关键事实。只有一条题，用于教学。语义复杂的任务应扩充题库和升级评分器。

## 推送到 GitHub

将所有文件上传到你自己的 Repository。Workflow 监听 Prompt/代码/测试/工作流的提交和 PR；快速测试始终运行，真实回归在可信的同仓库 PR、main push 和手动触发时运行，外部 fork PR 会跳过真实评估。

CI 失败的红色 ❌ 代表测试不达标或运行错误；在 Repositories → Settings → Branches/Rulesets 中设置分支保护，让可信 PR 必须通过检查，才可合并。

安全提示：不要把 `.env` 上传到 Git，不要在 untrusted fork PR 或 `pull_request_target` 上运行携带 Secrets 的代码。`@pytest.mark.langsmith` 默认创建/更新测试套件的数据集，与 `faq-regression-v1` 是不同用途；现有回归集由 `Client.evaluate()` 使用。
