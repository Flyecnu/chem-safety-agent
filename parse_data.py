"""从 data.txt 中提取 JSON 数组，转为 JSONL 格式的知识库文件"""
import json
import re
import sys

def parse_data_txt(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 用正则匹配所有 JSON 数组 [...]
    pattern = re.compile(r'\[\s*\{.*?\}\s*\]', re.DOTALL)
    arrays = pattern.findall(text)

    records = []
    seen = set()
    for arr_str in arrays:
        try:
            arr = json.loads(arr_str)
            for item in arr:
                if "tag" in item and "content" in item:
                    # 去重：用 content 的前80字符作为 key
                    key = item["content"][:80]
                    if key not in seen:
                        seen.add(key)
                        records.append(item)
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON 解析失败: {e}", file=sys.stderr)

    with open(output_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"共提取 {len(records)} 条规则，写入 {output_path}")

if __name__ == "__main__":
    parse_data_txt(
        "/data/zhw/demo/chem_safety/data.txt",
        "/data/zhw/demo/chem_safety/chemical_safety_agent/data/safety_knowledge.jsonl"
    )
