"""
化学安全审查智能体 Demo - Streamlit 启动入口
提供方案审查和结构扫描两个 Tab 页面
"""
import streamlit as st
import sys
import os

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from src.rag_engine import build_vector_db, get_rule_count
from src.chem_tools import ChemAnalyzer
from src.safety_agent import review_plan

# ========== 页面配置 ==========
st.set_page_config(
    page_title="化学安全审查智能体",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 化学安全审查智能体 Demo")
st.caption("基于 RAG + RDKit + LLM 的化学合成方案安全审查系统")

# ========== 侧边栏：知识库状态 ==========
with st.sidebar:
    st.header("📚 知识库状态")
    rule_count = get_rule_count()
    if rule_count > 0:
        st.success(f"已加载 **{rule_count}** 条安全规则")
    else:
        st.warning("知识库尚未构建")

    if st.button("🔄 重建知识库", use_container_width=True):
        with st.spinner("正在构建向量数据库..."):
            build_vector_db()
        st.success("知识库重建完成！")
        st.rerun()

    st.divider()
    st.header("ℹ️ 关于")
    st.markdown("""
    **技术栈：**
    - LLM: InternLM (OpenAI 兼容接口)
    - RAG: LangChain + ChromaDB
    - 化学分析: RDKit
    - Embedding: BGE-small-zh

    **数据来源：** 化学安全规则知识库
    """)

# ========== 主区域：Tab 页面 ==========
tab1, tab2 = st.tabs(["📋 方案审查", "🔬 结构扫描"])

# ---------- Tab 1: 方案审查 ----------
with tab1:
    st.subheader("合成方案安全审查")
    st.markdown("输入你的合成路线或工艺方案，系统将自动检索相关安全规则并生成审查报告。")

    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.text_area(
            "合成方案描述",
            height=150,
            placeholder="例如：计划在高温密闭条件下，使用混酸对甲苯进行三硝基化，制备TNT..."
        )
    with col2:
        smiles_input = st.text_input(
            "目标分子 SMILES（可选）",
            placeholder="例如：Cc1c(cc(cc1[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-]"
        )

    # 预设示例
    st.markdown("**快速示例：**")
    example_cols = st.columns(3)
    with example_cols[0]:
        if st.button("TNT 硝化方案", use_container_width=True):
            st.session_state["example_input"] = "计划在60℃密闭反应釜中，使用发烟硝酸和浓硫酸的混酸体系，对甲苯进行硝化反应，目标产物为2,4,6-三硝基甲苯(TNT)。"
            st.session_state["example_smiles"] = "Cc1c(cc(cc1[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-]"
            st.rerun()
    with example_cols[1]:
        if st.button("TATP 过氧化物", use_container_width=True):
            st.session_state["example_input"] = "使用丙酮和双氧水在酸催化条件下合成三过氧化三丙酮(TATP)。"
            st.session_state["example_smiles"] = "CC1(OOC(C)(OO1)C)C"
            st.rerun()
    with example_cols[2]:
        if st.button("格氏反应放大", use_container_width=True):
            st.session_state["example_input"] = "计划一次性将10kg溴苯加入含300g镁屑的THF溶液中，制备苯基格氏试剂，反应温度控制在回流条件。"
            st.session_state["example_smiles"] = ""
            st.rerun()

    # 如果有示例数据，填入
    if "example_input" in st.session_state:
        user_input = st.session_state.pop("example_input")
        smiles_input = st.session_state.pop("example_smiles", "")

    if st.button("🔍 开始审查", type="primary", use_container_width=True):
        if not user_input.strip():
            st.error("请输入合成方案描述")
        elif rule_count == 0:
            st.error("请先在侧边栏点击「重建知识库」构建向量数据库")
        else:
            with st.spinner("正在进行安全审查（RAG检索 + 结构分析 + LLM推理）..."):
                report = review_plan(
                    user_input=user_input,
                    smiles=smiles_input if smiles_input.strip() else None
                )
            st.divider()
            st.subheader("📝 安全审查报告")
            st.markdown(report)

# ---------- Tab 2: 结构扫描 ----------
with tab2:
    st.subheader("分子结构安全扫描")
    st.markdown("输入分子的 SMILES 字符串，系统将使用 RDKit 进行结构分析，识别潜在危险基团。")

    smiles_scan = st.text_input(
        "输入 SMILES",
        placeholder="例如：Cc1c(cc(cc1[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-]"
    )

    # 常见示例分子
    st.markdown("**常见含能分子示例：**")
    mol_cols = st.columns(4)
    example_mols = {
        "TNT": "Cc1c(cc(cc1[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-]",
        "RDX": "O=[N+]([O-])N1CN([N+](=O)[O-])CN([N+](=O)[O-])C1",
        "硝化甘油": "[O-][N+](=O)OCC(CO[N+](=O)[O-])O[N+](=O)[O-]",
        "苦味酸": "Oc1c(cc(cc1[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-]",
    }
    for i, (name, smi) in enumerate(example_mols.items()):
        with mol_cols[i]:
            if st.button(name, use_container_width=True):
                st.session_state["scan_smiles"] = smi
                st.rerun()

    if "scan_smiles" in st.session_state:
        smiles_scan = st.session_state.pop("scan_smiles")

    if st.button("🔬 扫描结构", type="primary", use_container_width=True, key="scan_btn"):
        if not smiles_scan.strip():
            st.error("请输入 SMILES")
        else:
            analyzer = ChemAnalyzer()

            if not analyzer.validate_smiles(smiles_scan):
                st.error(f"无效的 SMILES: `{smiles_scan}`，请检查输入格式。")
            else:
                result = analyzer.analyze(smiles_scan)

                # 分两列显示：左边分子图，右边分析结果
                col_img, col_info = st.columns([1, 2])

                with col_img:
                    st.markdown("**分子结构**")
                    img_bytes = analyzer.mol_to_image_bytes(smiles_scan, size=(400, 350))
                    if img_bytes:
                        st.image(img_bytes, use_container_width=True)

                with col_info:
                    st.markdown(f"**分子式:** `{result['mol_formula']}`")
                    st.markdown(f"**分子量:** `{result['mol_weight']}`")

                    st.divider()
                    st.markdown("**危险基团检测结果：**")
                    for name, count in result["details"].items():
                        if isinstance(count, int):
                            if count > 0:
                                st.markdown(f"- 🔴 **{name}**: {count} 个")
                            else:
                                st.markdown(f"- 🟢 {name}: 0")
                        else:
                            st.markdown(f"- 📊 {name}: {count}")

                # 警告信息
                if result["warnings"]:
                    st.divider()
                    st.error("⚠️ 结构安全警告")
                    for w in result["warnings"]:
                        st.warning(w)
                else:
                    st.success("✅ 未检测到已知高危结构特征")
