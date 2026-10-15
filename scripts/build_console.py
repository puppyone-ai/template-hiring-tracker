#!/usr/bin/env python3
"""Validate the three CSV tables and render the current table, using stdlib only."""

import argparse
import csv
from datetime import date
from html import escape
from pathlib import Path
import re
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "序号", "候选人ID", "姓名", "岗位", "学校", "来源", "入库时间",
    "当前阶段", "人工结论", "AI建议", "岗位ID", "候选人目录", "最后更新",
)
STAGES = {
    "待确认", "新收到", "待初筛", "待约一面", "一面", "待约二面", "二面",
    "待约三面", "三面", "待决策", "Offer沟通", "待入职", "已入职",
    "暂停", "已结束", "已归档",
}
DECISIONS = {"", "继续推进", "pass", "淘汰", "候选人退出", "Offer拒绝", "Offer接受", "已入职"}
ARCHIVE_DECISIONS = {"pass", "淘汰", "候选人退出", "Offer拒绝"}
TABLES = (
    ("00-console/候选人总表.csv", "02-candidates"),
    ("90-archive/候选人归档表.csv", "90-archive"),
    ("91-hired/已入职表.csv", "91-hired"),
)
OUTPUT = ROOT / "00-console/候选人总表.html"


def fail(message):
    raise ValueError(message)


def role_index():
    roles = {}
    for card in sorted((ROOT / "01-roles").glob("*/岗位卡.md")):
        text = card.read_text(encoding="utf-8")
        role_id = re.search(r"^\| 岗位ID \| ([^|]+) \|$", text, re.M)
        name = re.search(r"^\| 岗位名称 \| ([^|]+) \|$", text, re.M)
        if not role_id or not name:
            fail(f"{card.relative_to(ROOT)}: 岗位卡缺少 ID 或名称")
        key = role_id[1].strip()
        if not re.fullmatch(r"J-\d{6}-[A-Z0-9]+", key) or key in roles:
            fail(f"{card.relative_to(ROOT)}: 岗位 ID 格式错误或重复")
        if not card.parent.name.startswith(key + "-"):
            fail(f"{card.relative_to(ROOT)}: 目录与岗位 ID 不一致")
        for required in ("JD.md", "筛选标准.md"):
            if not (card.parent / required).is_file():
                fail(f"{card.parent.relative_to(ROOT)}: 缺少 {required}")
        roles[key] = name[1].strip()
    return roles


def load_tables():
    roles = role_index()
    seen_ids, seen_paths = set(), set()
    tables = []
    for relative, bucket in TABLES:
        rows = []
        with (ROOT / relative).open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != list(FIELDS):
                fail(f"{relative}: 表头或列顺序错误")
            for row in reader:
                if not any(value for value in row.values()):
                    continue
                if set(row) != set(FIELDS) or any(v is None for v in row.values()):
                    fail(f"{relative}: 第 {reader.line_num} 行字段数错误")
                for key, value in row.items():
                    if value != value.strip():
                        fail(f"{relative}: 第 {reader.line_num} 行 {key} 有首尾空白")
                cid, job_id = row["候选人ID"], row["岗位ID"]
                if not re.fullmatch(r"C-\d{6}-\d{3}", cid) or cid in seen_ids:
                    fail(f"{relative}: 候选人 ID 格式错误或跨表重复")
                if row["序号"] != str(len(rows) + 1):
                    fail(f"{relative}: 序号不连续")
                if roles.get(job_id) != row["岗位"]:
                    fail(f"{relative}: 岗位 ID 与岗位名称不匹配")
                for field in ("入库时间", "最后更新"):
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[field]):
                        fail(f"{relative}: {field} 必须为 YYYY-MM-DD")
                    date.fromisoformat(row[field])
                if row["入库时间"] > row["最后更新"]:
                    fail(f"{relative}: 最后更新早于入库时间")
                stage, decision = row["当前阶段"], row["人工结论"]
                if stage not in STAGES or decision not in DECISIONS:
                    fail(f"{relative}: 阶段或结论不是受控值")
                if row["AI建议"] and not row["AI建议"].startswith("AI建议："):
                    fail(f"{relative}: AI 建议缺少标识")
                if bucket == "02-candidates" and (
                    stage in {"已归档", "已入职"} or decision in ARCHIVE_DECISIONS | {"已入职"}
                ):
                    fail(f"{relative}: 当前表混入结束记录")
                if bucket == "90-archive" and (stage != "已归档" or decision not in ARCHIVE_DECISIONS):
                    fail(f"{relative}: 归档状态或结论错误")
                if bucket == "91-hired" and (stage != "已入职" or decision != "已入职"):
                    fail(f"{relative}: 已入职状态或结论错误")
                path = Path(row["候选人目录"])
                depth = 3 if bucket == "02-candidates" else 2
                if path.is_absolute() or ".." in path.parts or len(path.parts) != depth:
                    fail(f"{relative}: 候选人目录不是约定的相对路径")
                if path.parts[0] != bucket or (depth == 3 and path.parts[1] != row["岗位"]):
                    fail(f"{relative}: 候选人目录分区或岗位错误")
                if path.name not in {row["姓名"], row["姓名"] + "-" + cid}:
                    fail(f"{relative}: 候选人目录与姓名不一致")
                folder = (ROOT / path).resolve()
                if not folder.is_relative_to(ROOT) or folder in seen_paths:
                    fail(f"{relative}: 候选人目录越界或重复")
                card = folder / "候选人卡.md"
                if not card.is_file() or cid not in card.read_text(encoding="utf-8"):
                    fail(f"{relative}: 缺少候选人卡或卡内 ID 不匹配")
                seen_ids.add(cid)
                seen_paths.add(folder)
                rows.append(row)
        if rows != sorted(rows, key=lambda r: (r["岗位ID"], r["候选人ID"])):
            fail(f"{relative}: 未按岗位 ID、候选人 ID 排序")
        tables.append(rows)
    for _, bucket in TABLES:
        for card in (ROOT / bucket).rglob("候选人卡.md"):
            if card.parent.resolve() not in seen_paths:
                fail(f"{card.relative_to(ROOT)}: 候选人目录未登记到表中")
    return tables


def render(rows):
    parts = []
    previous = None
    for row in rows:
        if row["岗位ID"] != previous:
            if previous is not None:
                parts.append('<tr class="spacer" aria-hidden="true"><td colspan="13"></td></tr>')
            previous = row["岗位ID"]
        cells = []
        for field in FIELDS:
            value = escape(row[field] or "—")
            if field == "候选人目录":
                target = "../" + quote(row[field] + "/候选人卡.md", safe="/")
                value = f'<a href="{target}">查看候选人卡</a>'
            cells.append(f"<td>{value}</td>")
        parts.append("<tr>" + "".join(cells) + "</tr>")
    if not rows:
        parts.append('<tr><td colspan="13">暂无当前候选人</td></tr>')
    headers = "".join(f'<th scope="col">{escape(field)}</th>' for field in FIELDS)
    body = "\n".join(parts)
    groups = len({row["岗位ID"] for row in rows})
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>候选人总表 · Recruit Template Version</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;padding:40px 24px;background:#f5f6f8;color:#1d2939;font:15px/1.6 system-ui,sans-serif}}
main{{max-width:1600px;margin:auto}}h1{{font-size:28px;margin:0 0 8px}}a{{color:#2452a1;text-underline-offset:3px}}
.notice{{padding:14px 18px;border:1px solid #dfc97b;background:#fff9e9;border-radius:8px;margin:20px 0}}
.meta{{color:#475467}}.table-wrap{{overflow-x:auto;border:1px solid #d0d5dd;border-radius:8px;background:white}}
table{{width:100%;border-collapse:collapse;text-align:left}}caption{{text-align:left;padding:16px;font-weight:600}}
th,td{{padding:12px 14px;border-bottom:1px solid #eaecf0;vertical-align:top;min-width:110px}}
th{{background:#f0f3f8;white-space:nowrap}}td:nth-child(10){{min-width:260px}}td:nth-child(2),td:nth-child(11){{white-space:nowrap}}
.spacer td{{padding:5px;background:#f5f6f8}}footer{{margin-top:20px;color:#475467}}
@media(max-width:640px){{body{{padding:24px 12px}}h1{{font-size:24px}}}}
</style>
</head>
<body><main>
<p class="meta">Recruit Template Version · 本地浏览版</p>
<h1>候选人总表</h1>
<p class="notice">公开模板中的记录全部为虚构示例，与真实人员无对应关系。在私有副本填入真实资料后，请勿公开发布此页面。</p>
<p><a href="%E5%80%99%E9%80%89%E4%BA%BA%E6%80%BB%E8%A1%A8.csv">CSV 状态来源</a> · <a href="%E6%8B%9B%E8%81%98%E5%BE%85%E5%8A%9E.md">招聘待办</a> · <a href="../README.md">使用说明</a></p>
<p class="meta">当前候选人 {len(rows)} 人 · 岗位 {groups} 个。归档与已入职记录不计入当前表。</p>
<div class="table-wrap"><table>
<caption>当前在招候选人（按岗位分组）</caption>
<thead><tr>{headers}</tr></thead>
<tbody>
{body}
</tbody></table></div>
<footer>本页由 CSV 生成，不在 HTML 中直接维护状态。更新 CSV 后运行 <code>python3 scripts/build_console.py</code>。</footer>
</main></body></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without writing; fail if HTML is stale")
    args = parser.parse_args()
    try:
        tables = load_tables()
        expected = render(tables[0])
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
                fail("HTML 缺失或已过期，请运行 python3 scripts/build_console.py")
        else:
            OUTPUT.write_text(expected, encoding="utf-8")
        counts = ", ".join(str(len(table)) for table in tables)
        print(f"OK: current/archive/hired = {counts}; CSV, directories and HTML are consistent.")
    except (ValueError, OSError, csv.Error) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
