"""
RAG 引擎 - 基于 LangChain + ChromaDB
负责向量化知识库、持久化存储和语义检索
"""
import json
import os
from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "safety_knowledge.jsonl"
VECTOR_DB_DIR = str(PROJECT_ROOT / "vector_db")


def _get_embeddings() -> HuggingFaceEmbeddings:
    """获取 Embedding 模型实例（本地中文模型）"""
    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def load_jsonl(path: str = None) -> list[Document]:
    """读取 JSONL 知识库文件，转为 LangChain Document 列表"""
    path = path or str(DATA_PATH)
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            tag = item.get("tag", "未分类")
            content = item.get("content", "")
            # 把 tag 放入 metadata，content 作为页面内容
            doc = Document(
                page_content=f"[{tag}] {content}",
                metadata={"tag": tag, "source": f"safety_knowledge.jsonl:line_{i+1}"},
            )
            docs.append(doc)
    return docs


def build_vector_db(jsonl_path: str = None) -> Chroma:
    """
    构建向量数据库：读取 JSONL -> 向量化 -> 持久化到 vector_db/ 目录
    返回 Chroma 实例
    """
    docs = load_jsonl(jsonl_path)
    embeddings = _get_embeddings()

    # 清理旧数据再重建
    db = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR,
        collection_name="safety_rules",
    )
    print(f"[RAG] 已构建向量库，共 {len(docs)} 条规则，存储于 {VECTOR_DB_DIR}")
    return db


def get_retriever(k: int = 3):
    """
    加载本地向量库并返回检索器
    k: 每次召回最相关的 k 条
    """
    embeddings = _get_embeddings()
    db = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings,
        collection_name="safety_rules",
    )
    return db.as_retriever(search_kwargs={"k": k})


def get_rule_count() -> int:
    """获取知识库中的规则条数"""
    try:
        embeddings = _get_embeddings()
        db = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings,
            collection_name="safety_rules",
        )
        return db._collection.count()
    except Exception:
        return 0
