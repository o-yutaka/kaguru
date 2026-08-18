from __future__ import annotations

import csv
import io
import json
import subprocess
from pathlib import Path

ROOT = Path("artifacts/kaggriculture_scout")
ROOT.mkdir(parents=True, exist_ok=True)


def run(*args: str) -> str:
    p = subprocess.run(args, check=True, text=True, capture_output=True)
    return p.stdout


def save(name: str, text: str) -> None:
    (ROOT / name).write_text(text, encoding="utf-8")


leader = run("kaggle", "competitions", "leaderboard", "kaggriculture", "--show", "--csv", "-q")
save("leaderboard.csv", leader)

rows = list(csv.DictReader(io.StringIO(leader)))
for row in rows:
    for k in list(row):
        if k and k.startswith("\\ufeff"):
            row[k.lstrip("\\ufeff")] = row.pop(k)

rows_sorted = sorted(
    rows,
    key=lambda r: float(str(r.get("Score", r.get("score", "-inf"))).replace(",", ""))
    if str(r.get("Score", r.get("score", ""))).strip()
    else float("-inf"),
    reverse=True,
)

save("top20.json", json.dumps(rows_sorted[:20], ensure_ascii=False, indent=2))

try:
    topics = run("kaggle", "competitions", "topics", "list", "kaggriculture", "--sort-by", "top", "--page-size", "100", "-v", "-q")
except subprocess.CalledProcessError:
    topics = run("kaggle", "competitions", "topics", "list", "kaggriculture", "--sort-by", "recent", "--page-size", "100", "-v", "-q")
save("topics.csv", topics)

subs = run("kaggle", "competitions", "submissions", "kaggriculture", "-v", "-q")
save("my_submissions.csv", subs)

manifest = {
    "competition": "kaggriculture",
    "leaderboard_rows": len(rows),
    "top20_rows": len(rows_sorted[:20]),
    "artifacts": ["leaderboard.csv", "top20.json", "topics.csv", "my_submissions.csv"],
}
(ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(manifest, ensure_ascii=False))
