# 化学安全审查智能体 Demo

基于 **RAG + RDKit + LLM** 的化学合成方案安全审查系统

---

## 📋 项目简介

本项目是**含能材料研发**中**"安全规则与黑名单"**任务的 Demo 实现，旨在通过人工智能技术自动识别化学合成方案中的安全隐患。

### 核心功能

1. **方案审查** - 输入合成方案描述，系统自动检索安全规则并生成审查报告
2. **结构扫描** - 输入分子 SMILES，检测危险基团（硝基、叠氮、过氧键等）

### 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| **LLM** | InternLM (OpenAI 兼容接口) | 安全审查推理 |
| **RAG** | LangChain + ChromaDB | 知识库检索 |
| **Embedding** | BGE-small-zh-v1.5 | 中文语义向量化 |
| **化学分析** | RDKit | 分子结构分析 |
| **前端** | Streamlit | Web 交互界面 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Conda 环境：`/data/zhw/conda_envs/zhw_p`（已配置）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
# 方法 1: 使用启动脚本
./run.sh

# 方法 2: 直接运行
/data/zhw/conda_envs/zhw_p/bin/streamlit run app.py --server.port 8501
```

### 访问地址

- 本机：http://localhost:8501
- 局域网：http://10.1.40.60:8501

---

## 📂 项目结构

```
chemical_safety_agent/
├── data/
│   └── safety_knowledge.jsonl      # 94条安全规则知识库
├── src/
│   ├── chem_tools.py               # RDKit 分子结构分析
│   ├── rag_engine.py               # RAG 检索引擎
│   └── safety_agent.py             # LLM 安全审查智能体
├── app.py                          # Streamlit 主程序
├── .env                            # 环境配置（未提交）
├── requirements.txt                # 依赖列表
├── run.sh                          # 启动脚本
├── quick_test.py                   # 快速测试脚本
└── parse_data.py                   # 数据解析脚本
```

---

## 🔬 使用示例

### Web 界面操作

1. 打开浏览器访问 http://localhost:8501
2. 点击预设示例（如 "TNT 硝化方案"）
3. 点击"🔍 开始审查"按钮
4. 查看详细的安全审查报告

### Python 脚本调用

```python
from src.safety_agent import review_plan

# 审查合成方案
report = review_plan(
    user_input="计划在60℃密闭反应釜中进行硝化反应...",
    smiles="Cc1c(cc(cc1[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-]"
)

print(report)
```

### 命令行测试

```bash
# 快速测试所有功能
python quick_test.py
```

---

## 📊 知识库统计

- **规则总数：** 94 条
- **数据来源：** 文献、SDS、专利、工艺规范
- **覆盖类别：**
  - 含能高危物质（TNT、TATP、雷酸汞等）
  - 极不稳定结构（过氧化物、叠氮化物）
  - 工艺红线（硝化反应、氧化剂、格氏试剂等）
  - 结构警示（多硝基、偕二硝基、硝酸酯等）
  - 法规合规（易制爆化学品管制）

---

## 🛠️ 核心模块说明

### 1. RDKit 结构分析器 (`src/chem_tools.py`)

检测 9 类危险基团：
- 硝基 (-NO2)
- 叠氮基 (-N3)
- 过氧键 (-O-O-)
- 硝酸酯 (-ONO2)
- 硝胺 (N-NO2)
- 重氮基 (-N2+)
- 异氰酸酯 (-NCO)
- 肼基 (-NHNH-)
- 偕二硝基 (C(NO2)2)

计算指标：
- 分子式、分子量
- 氧平衡估算
- (C+O)/N 比值（叠氮稳定性）

### 2. RAG 检索引擎 (`src/rag_engine.py`)

- **向量化模型：** BGE-small-zh-v1.5
- **向量数据库：** ChromaDB
- **检索策略：** Top-K 语义相似度召回

工作流程：
1. 知识库 JSONL → 向量化 → ChromaDB 持久化
2. 用户查询 → 向量化 → 相似度检索 → 返回 Top-K 规则

### 3. LLM 安全审查智能体 (`src/safety_agent.py`)

综合处理流程：
1. RDKit 分析分子结构
2. RAG 检索相关安全规则
3. 拼装 Prompt 发送给 LLM
4. 生成结构化审查报告

输出格式：
- 🔴 红牌拦截 / 🟡 黄牌警告 / 🟢 绿色通过
- 违规分析（引用知识库原文）
- 安全建议

---

## 🔧 配置说明

### .env 文件配置

创建 `.env` 文件并配置以下参数：

```bash
# LLM API 配置
OPENAI_API_BASE=https://chat.intern-ai.org.cn/api/v1
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=intern-latest

# Embedding 模型
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

---

## 📈 后续优化方向

### 数据规模扩大（2026年6月交付目标）

- [ ] 扩展到 ≥10,000 条反应实例/模板
- [ ] 构建含能分子结构库（≥100,000 条）
- [ ] 整合更多文献、专利、SDS 数据

### 功能增强

- [ ] 反应模板自动抽取
- [ ] 结构片段库（motif 识别）
- [ ] 分子相似度搜索
- [ ] 批量审查接口

### 性能优化

- [ ] 切换到 GPU embedding
- [ ] 缓存热点检索结果
- [ ] 异步 LLM 调用

---

## 📄 许可证

本项目为内部研发 Demo，仅供研究使用。

---

## 👥 开发者

**项目负责人：** 宏伟
**任务：** 安全规则与黑名单（文献与知识挖掘智能体）
**时间：** 2026年6月交付第一版本

---

## 📞 联系方式

如有问题或建议，请联系项目负责人。
