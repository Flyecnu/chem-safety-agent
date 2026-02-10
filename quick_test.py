#!/usr/bin/env python3
"""
快速测试 - 分步演示三大模块
"""
import sys
sys.path.insert(0, '/data/zhw/demo/chem_safety/chemical_safety_agent')

print("=" * 70)
print("🧪 化学安全审查智能体 - 快速测试")
print("=" * 70)

# ============ 测试 1: RDKit 结构分析 ============
print("\n【测试 1】RDKit 分子结构分析")
print("-" * 70)

from src.chem_tools import ChemAnalyzer
analyzer = ChemAnalyzer()

# 分析 TNT
tnt_smiles = 'Cc1c(cc(cc1[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-]'
result = analyzer.analyze(tnt_smiles)

print(f"输入 SMILES: {tnt_smiles}")
print(f"分子式: {result['mol_formula']}")
print(f"分子量: {result['mol_weight']}")
print(f"硝基数量: {result['details']['硝基 (-NO2)']}")
print(f"氧平衡: {result['details'].get('氧平衡 (OB%)', 'N/A')}%")
print(f"警告数: {len(result['warnings'])}")
if result['warnings']:
    print("警告内容:")
    for w in result['warnings']:
        print(f"  ⚠️  {w}")

# ============ 测试 2: RAG 检索 ============
print("\n【测试 2】RAG 知识库检索")
print("-" * 70)

from src.rag_engine import get_retriever, get_rule_count

print(f"知识库总规则数: {get_rule_count()}")

retriever = get_retriever(k=3)
docs = retriever.invoke("TNT 三硝基甲苯")

print(f"检索 query: 'TNT 三硝基甲苯'")
print(f"召回结果数: {len(docs)}")
print("\nTop-3 规则:")
for i, doc in enumerate(docs, 1):
    content = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
    print(f"\n  [{i}] {content}")

# ============ 测试 3: 完整审查流程（简化输出）============
print("\n【测试 3】完整审查流程（调用 LLM）")
print("-" * 70)

from src.safety_agent import review_plan

print("正在审查方案：硝化甘油合成...")
report = review_plan(
    user_input="使用浓硝酸和浓硫酸的混酸对甘油进行硝化，制备硝化甘油。",
    smiles="[O-][N+](=O)OCC(CO[N+](=O)[O-])O[N+](=O)[O-]"
)

# 只显示前500字符
print(f"\n审查报告（前500字符）:\n{report[:500]}...")

print("\n" + "=" * 70)
print("✅ 测试完成！所有模块工作正常。")
print("=" * 70)
print("\n访问 Web 界面获得完整体验: http://localhost:8501")
