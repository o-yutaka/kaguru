from __future__ import annotations
import csv, json, math, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean, median

ROOT = Path("artifacts/kaggriculture_black")
ROOT.mkdir(parents=True, exist_ok=True)

PRODUCTS = ["WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","FERTILIZER"]
ANIMALS = ["GOOSE","COW","SHEEP"]
SEEDS = [42, 1000, 1050, 1100, 1200, 1500, 2026, 300257]

USER_LEADERBOARD_SNAPSHOT = [
    {"rank":1,"team":"カワシギ","score":3185.2},
    {"rank":2,"team":"Thomas Tschinkel","score":3155.2},
    {"rank":3,"team":"tetsuya","score":3037.7},
    {"rank":20,"team":"boatlee","score":2880.8},
    {"rank":None,"team":"self Phase3 v1","score":895.6},
    {"rank":None,"team":"self V17 best","score":910.6},
]

SOURCE_MANIFEST = [
    {"class":"OFFICIAL","url":"https://github.com/Kaggle/kaggle-environments/tree/master/kaggle_environments/envs/kaggriculture","finding":"720 turns, 2 players, public farms, dynamic market, market order cap, official environment contract."},
    {"class":"PUBLIC_CODE","url":"https://github.com/GzmCR/Kaggriculture","finding":"Rule-based agent uses market price/demand/inventory/cash/season timing; history and experiments are preserved for reproducibility."},
    {"class":"PUBLIC_CODE","url":"https://github.com/deepeshumrao/kaggriculture-agent","finding":"Market-first ordering and nearest high-value tile / Manhattan movement; emphasizes action-economy under 720 turns."},
    {"class":"USER_OBSERVED","url":"https://www.kaggle.com/competitions/kaggriculture/leaderboard","finding":"2026-08-18 observed snapshot: top scores 3185.2 / 3155.2 / 3037.7; own 895.6 and V17 910.6."},
]


def run(cmd: str):
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def kaggle_cli_snapshot():
    cmds = {
        "leaderboard":"kaggle competitions leaderboard kaggriculture -s -p 500 --csv",
        "submissions":"kaggle competitions submissions kaggriculture --csv",
        "files":"kaggle competitions files kaggriculture",
    }
    out = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(run, c): k for k,c in cmds.items()}
        for f in as_completed(futs): out[futs[f]] = f.result()
    return out


def parse_csv_text(text: str):
    text = text.lstrip("\ufeff")
    try:
        return list(csv.DictReader(text.splitlines()))
    except Exception:
        return []


def normalize_leaderboard(rows):
    clean = []
    for r in rows:
        score = r.get("Score") or r.get("score")
        try: score = float(score)
        except Exception: continue
        rank = r.get("Rank") or r.get("rank")
        try: rank = int(rank)
        except Exception: rank = None
        clean.append({"rank":rank,"team":r.get("TeamName") or r.get("teamName") or r.get("Team") or r.get("team"),"score":score})
    return sorted(clean, key=lambda x: x["score"], reverse=True)


def opp_signature(farm: dict):
    return {
        "money": farm.get("money"),
        "hands": farm.get("farmHands", farm.get("hands")),
        "unlocked": farm.get("unlockedQuadrants", farm.get("unlocked_quadrants")),
        "tiles": len(farm.get("tiles", [])) if isinstance(farm.get("tiles"), list) else None,
    }


def manhattan(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


def pressure_from_public_farm(farm: dict):
    """Conservative public-only supply proxy. Never reads private shed/inventory."""
    pressure = {p:0.0 for p in PRODUCTS}
    tiles = farm.get("tiles", [])
    if not isinstance(tiles, list): return pressure
    for t in tiles:
        if not isinstance(t, dict): continue
        obj = str(t.get("object") or t.get("type") or t.get("crop") or "").upper()
        growth = float(t.get("growth", 0) or 0)
        stage = float(t.get("stage", 0) or 0)
        q = 1.0 + min(2.0, max(0.0, growth + stage) * 0.25)
        if "WHEAT" in obj: pressure["WHEAT"] += q
        elif "CARROT" in obj: pressure["CARROT"] += q
        elif "TOMATO" in obj: pressure["TOMATO"] += q
        elif "STRAWBERRY" in obj: pressure["STRAWBERRY"] += q
        elif "MELON" in obj: pressure["MELON"] += q
        elif "FERTILIZER" in obj: pressure["FERTILIZER"] += q
        elif "COW" in obj: pressure["MILK"] = pressure.get("MILK",0) + q
        elif "SHEEP" in obj: pressure["WOOL"] = pressure.get("WOOL",0) + q
    return pressure


def evidence(claim, cls, source, status, note=None):
    return {"claim":claim,"source_class":cls,"source":source,"status":status,"note":note}


def build_manifest():
    payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "competition":"kaggriculture",
        "source_manifest":SOURCE_MANIFEST,
        "user_leaderboard_snapshot":USER_LEADERBOARD_SNAPSHOT,
        "seeds":SEEDS,
        "gates":{
            "production_freeze":True,
            "opponent_reads_public_farm_only":True,
            "cash_and_ladder_separate":True,
            "single_replay_promotion":False,
            "paired_ab_required":True,
        }
    }
    (ROOT/"research_manifest.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    return payload


def execute_collection():
    results = kaggle_cli_snapshot()
    manifest = build_manifest()
    if "leaderboard" in results:
        (ROOT/"leaderboard_raw.txt").write_text(results["leaderboard"]["stdout"],encoding="utf-8")
        rows = normalize_leaderboard(parse_csv_text(results["leaderboard"]["stdout"]))
        (ROOT/"leaderboard_normalized.json").write_text(json.dumps(rows[:500],ensure_ascii=False,indent=2),encoding="utf-8")
    if "submissions" in results:
        (ROOT/"submissions_raw.txt").write_text(results["submissions"]["stdout"],encoding="utf-8")
    if "files" in results:
        (ROOT/"competition_files.txt").write_text(results["files"]["stdout"],encoding="utf-8")
    return results, manifest


if __name__ == "__main__":
    results, manifest = execute_collection()
    print(json.dumps({k:v["returncode"] for k,v in results.items()}, ensure_ascii=False))
    print("artifacts:", ROOT.resolve())
