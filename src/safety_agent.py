"""
安全审查智能体 - 基于 LLM + RAG + RDKit
综合检索到的规则和分子结构分析结果，生成化学安全审查报告
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from .chem_tools import ChemAnalyzer
from .rag_engine import get_retriever

# 加载环境变量
load_dotenv()

# System Prompt
SYSTEM_PROMPT = """你是一个化工安全专家。请根据【检索到的知识库规则】和【分子结构分析结果】，审查用户的合成方案。

你的职责：
1. 仔细分析检索到的每一条规则，判断是否与用户的方案相关
2. 结合分子结构分析结果（如硝基数量、叠氮基团、过氧键等），评估风险等级
3. 如果发现违规或高风险，必须直接给出判定：
   - 🔴 红牌拦截：存在严重安全隐患，必须立即停止
   - 🟡 黄牌警告：存在潜在风险，需要采取额外防护措施
   - 🟢 绿色通过：未发现明显安全问题
4. 必须引用知识库原文作为依据
5. 给出具体的安全建议

请用中文回复，格式化输出审查报告。"""


def _get_llm() -> ChatOpenAI:
    """获取 LLM 实例（InternLM / OpenAI 兼容接口）"""
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL", "intern-latest"),
        openai_api_base=os.getenv("OPENAI_API_BASE", "https://chat.intern-ai.org.cn/api/v1"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        temperature=0,
        max_tokens=2048,
    )


def review_plan(user_input: str, smiles: str = None) -> str:
    """
    综合审查入口：
    1. 用 RDKit 分析分子结构（如果有 SMILES）
    2. 用 RAG 检索相关安全规则
    3. 拼装 Prompt 发给 LLM 生成审查报告

    Args:
        user_input: 用户的合成方案描述
        smiles: 可选的目标分子 SMILES

    Returns:
        LLM 的安全审查报告
    """
    # ---- 1. 结构分析 ----
    structure_info = ""
    if smiles:
        analyzer = ChemAnalyzer()
        result = analyzer.analyze(smiles)
        structure_info = f"\n【分子结构分析结果】\n{result['summary']}\n"

    # ---- 2. RAG 检索 ----
    retriever = get_retriever(k=5)
    # 用用户输入 + SMILES（如有）做检索
    query = user_input
    if smiles:
        query += f" (分子SMILES: {smiles})"
    docs = retriever.invoke(query)

    retrieved_rules = "\n".join(
        [f"规则{i+1}: {doc.page_content}" for i, doc in enumerate(docs)]
    )

    # ---- 3. 拼装 Prompt ----
    user_message = f"""
## 用户提交的合成方案

{user_input}

{structure_info}

## 检索到的知识库规则

{retrieved_rules}

---
请根据以上信息，生成安全审查报告。
"""

    # ---- 4. 调用 LLM ----
    llm = _get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]
    response = llm.invoke(messages)
    return response.content
