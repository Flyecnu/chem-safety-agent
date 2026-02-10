"""
化学结构分析工具箱 - 基于 RDKit
用于分子结构安全性扫描：硝基计数、叠氮基检测、过氧键检测等
"""
from typing import Optional
from rdkit import Chem
from rdkit.Chem import Descriptors, Draw, rdMolDescriptors
from io import BytesIO


class ChemAnalyzer:
    """分子结构安全分析器"""

    # SMARTS 模式定义
    PATTERNS = {
        "硝基 (-NO2)": "[N+](=O)[O-]",
        "叠氮基 (-N3)": "[N-]=[N+]=[N-]",         # 有机叠氮
        "过氧键 (-O-O-)": "[O]-[O]",
        "硝酸酯 (-ONO2)": "[O][N+](=O)[O-]",
        "硝胺 (N-NO2)": "[N][N+](=O)[O-]",
        "重氮基 (-N2+)": "[N+]#N",
        "异氰酸酯 (-NCO)": "[N]=[C]=[O]",
        "肼基 (-NHNH-)": "[NH]-[NH]",
        "偕二硝基 (C(NO2)2)": "[C]([N+](=O)[O-])[N+](=O)[O-]",
    }

    def validate_smiles(self, smiles: str) -> bool:
        """校验 SMILES 是否为有效分子"""
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None

    def analyze(self, smiles: str) -> dict:
        """
        对 SMILES 进行结构安全扫描
        返回包含各类警示信息的字典
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {
                "valid": False,
                "error": f"无效的 SMILES: {smiles}",
                "summary": "输入的 SMILES 字符串无法被解析为有效分子，请检查格式。"
            }

        results = {
            "valid": True,
            "smiles": smiles,
            "mol_formula": rdMolDescriptors.CalcMolFormula(mol),
            "mol_weight": round(Descriptors.MolWt(mol), 2),
            "warnings": [],
            "details": {},
        }

        # 扫描各类危险基团
        for name, smarts in self.PATTERNS.items():
            pattern = Chem.MolFromSmarts(smarts)
            if pattern is None:
                continue
            matches = mol.GetSubstructMatches(pattern)
            count = len(matches)
            results["details"][name] = count
            if count > 0:
                results["warnings"].append(f"检测到 {count} 个{name}")

        # 多硝基高能分子判定
        nitro_count = results["details"].get("硝基 (-NO2)", 0)
        if nitro_count >= 3:
            results["warnings"].append(
                f"⚠ 高含能分子警告：含有 {nitro_count} 个硝基，属于高含能材料，操作等级为高危"
            )

        # 叠氮稳定性评估：(C+O)/N 比值
        atom_counts = {}
        for atom in mol.GetAtoms():
            sym = atom.GetSymbol()
            atom_counts[sym] = atom_counts.get(sym, 0) + 1
        c_count = atom_counts.get("C", 0)
        o_count = atom_counts.get("O", 0)
        n_count = atom_counts.get("N", 0)
        if n_count > 0:
            ratio = (c_count + o_count) / n_count
            results["details"]["(C+O)/N 比值"] = round(ratio, 2)
            if ratio < 3 and results["details"].get("叠氮基 (-N3)", 0) > 0:
                results["warnings"].append(
                    f"⚠ 极度危险：(C+O)/N = {ratio:.2f} < 3，叠氮化物极不稳定"
                )

        # 氧平衡估算（简化版：基于 CHNO 分子）
        h_count = atom_counts.get("H", 0)
        if all(sym in ("C", "H", "O", "N", "F", "Cl") for sym in atom_counts.keys()):
            ob = ((o_count - 2 * c_count - h_count / 2) / Descriptors.MolWt(mol)) * 1600
            results["details"]["氧平衡 (OB%)"] = round(ob, 1)

        # 生成摘要
        results["summary"] = self._make_summary(results)
        return results

    def _make_summary(self, results: dict) -> str:
        """生成结构扫描摘要文本"""
        if not results["valid"]:
            return results.get("error", "分析失败")

        lines = [
            f"分子式: {results['mol_formula']}，分子量: {results['mol_weight']}",
        ]
        if results["warnings"]:
            lines.append("--- 结构警示 ---")
            for w in results["warnings"]:
                lines.append(f"  • {w}")
        else:
            lines.append("未检测到已知高危结构特征。")

        # 补充氧平衡信息
        ob = results["details"].get("氧平衡 (OB%)")
        if ob is not None:
            lines.append(f"氧平衡: {ob}%")

        return "\n".join(lines)

    def mol_to_image_bytes(self, smiles: str, size: tuple = (350, 300)) -> Optional[bytes]:
        """将 SMILES 渲染为 PNG 图片字节流"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        img = Draw.MolToImage(mol, size=size)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
