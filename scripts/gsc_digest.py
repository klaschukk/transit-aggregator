"""
Weekly SEO digest — turns two GSC snapshots into a markdown report.

Reads the two most recent snapshots from data/gsc/*.json, diffs them,
writes docs/00_strategy/weekly-seo-YYYY-MM-DD.md, and optionally fires
a compressed summary to Telegram (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID).

The diff logic is pure — see compute_diff() / build_markdown() — so the
interesting parts are covered by tests/test_gsc_digest.py.

Exit codes:
    0 — digest written (or cleanly skipped with no data)
    4 — no snapshot files present
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import date
from pathlib import Path

log = logging.getLogger("gsc_digest")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "gsc"
OUT_DIR = PROJECT_ROOT / "docs" / "00_strategy"

POSITION_DROP_ALERT = 3.0      # places
CLICKS_DROP_ALERT = 0.20       # 20%
CTR_LOW_THRESHOLD = 0.01       # 1%
HIGH_IMPRESSIONS = 500         # "many impressions" for suggested actions


def _by_key(rows: list[dict], key: str) -> dict[str, dict]:
    return {r[key]: r for r in rows if r.get(key)}


def compute_diff(current: dict, previous: dict | None) -> dict:
    """Compare current week's queries/pages to last week's.

    Pure function. Returns a dict consumed by build_markdown(). If
    `previous` is None we still emit a diff block — everything shows up
    as "new" but nothing is flagged as dropped.
    """
    cur_q = _by_key(current.get("queries_7d", []), "query")
    prev_q = _by_key((previous or {}).get("queries_7d", []), "query")
    cur_p = _by_key(current.get("pages_7d", []), "page")
    prev_p = _by_key((previous or {}).get("pages_7d", []), "page")

    new_queries = sorted(
        (cur_q[q] for q in cur_q.keys() - prev_q.keys()),
        key=lambda r: r["clicks"], reverse=True,
    )
    dropped_queries = sorted(
        (prev_q[q] for q in prev_q.keys() - cur_q.keys()),
        key=lambda r: r["clicks"], reverse=True,
    )

    position_drops = []
    click_gains = []
    click_losses = []
    for q, cur in cur_q.items():
        if q not in prev_q:
            continue
        prev = prev_q[q]
        pos_delta = cur["position"] - prev["position"]   # positive = worse
        if pos_delta >= POSITION_DROP_ALERT:
            position_drops.append({
                "query": q, "prev_pos": prev["position"],
                "cur_pos": cur["position"], "delta": pos_delta,
                "impressions": cur["impressions"],
            })
        click_delta = cur["clicks"] - prev["clicks"]
        if prev["clicks"] >= 5 and click_delta <= -max(1, prev["clicks"] * CLICKS_DROP_ALERT):
            click_losses.append({
                "query": q, "prev_clicks": prev["clicks"],
                "cur_clicks": cur["clicks"], "delta": click_delta,
            })
        if click_delta >= max(1, prev["clicks"] * 0.25):
            click_gains.append({
                "query": q, "prev_clicks": prev["clicks"],
                "cur_clicks": cur["clicks"], "delta": click_delta,
            })

    position_drops.sort(key=lambda r: r["delta"], reverse=True)
    click_losses.sort(key=lambda r: r["delta"])
    click_gains.sort(key=lambda r: r["delta"], reverse=True)

    page_click_drops = []
    for page, cur in cur_p.items():
        if page not in prev_p:
            continue
        prev = prev_p[page]
        if prev["clicks"] >= 10:
            delta = cur["clicks"] - prev["clicks"]
            pct = delta / prev["clicks"]
            if pct <= -CLICKS_DROP_ALERT:
                page_click_drops.append({
                    "page": page, "prev_clicks": prev["clicks"],
                    "cur_clicks": cur["clicks"], "pct": pct,
                })
    page_click_drops.sort(key=lambda r: r["pct"])

    cur_idx = current.get("indexation", {}) or {}
    prev_idx = (previous or {}).get("indexation", {}) or {}
    indexation_delta = (
        cur_idx.get("pages_with_impressions_7d", 0)
        - prev_idx.get("pages_with_impressions_7d", 0)
    )

    cur_t = current.get("totals_7d", {}) or {}
    prev_t = (previous or {}).get("totals_7d", {}) or {}

    def _pct(cur_v, prev_v):
        if not prev_v:
            return None
        return (cur_v - prev_v) / prev_v

    return {
        "new_queries": new_queries[:10],
        "dropped_queries": dropped_queries[:10],
        "position_drops": position_drops[:10],
        "click_gains": click_gains[:5],
        "click_losses": click_losses[:5],
        "page_click_drops": page_click_drops[:5],
        "indexation_delta": indexation_delta,
        "totals_pct": {
            "clicks": _pct(cur_t.get("clicks", 0), prev_t.get("clicks", 0)),
            "impressions": _pct(cur_t.get("impressions", 0),
                                prev_t.get("impressions", 0)),
            "position": (cur_t.get("position", 0.0)
                         - prev_t.get("position", 0.0)) or None,
        },
    }


def suggest_actions(current: dict) -> list[str]:
    """Heuristic recommendations from the current snapshot (pure)."""
    actions: list[str] = []
    queries = current.get("queries_7d", []) or []
    pages = current.get("pages_7d", []) or []

    low_ctr = [
        q for q in queries
        if q["impressions"] >= HIGH_IMPRESSIONS
        and q["ctr"] < CTR_LOW_THRESHOLD
        and q["position"] <= 10
    ]
    for q in sorted(low_ctr, key=lambda r: r["impressions"], reverse=True)[:3]:
        actions.append(
            f"Title/meta rewrite: query '{q['query']}' — "
            f"{q['impressions']} impressions, CTR {q['ctr']:.1%}, "
            f"pos {q['position']:.1f}"
        )

    near_miss = [q for q in queries if 10 < q["position"] <= 20
                 and q["impressions"] >= HIGH_IMPRESSIONS]
    for q in sorted(near_miss, key=lambda r: r["impressions"], reverse=True)[:3]:
        actions.append(
            f"Near page-2: '{q['query']}' at pos {q['position']:.1f} "
            f"({q['impressions']} impressions) — add content depth"
        )

    thin_pages = [p for p in pages
                  if p["impressions"] >= 200 and p["ctr"] < CTR_LOW_THRESHOLD]
    for p in sorted(thin_pages, key=lambda r: r["impressions"],
                    reverse=True)[:2]:
        actions.append(
            f"Thin SERP snippet: {p['page']} — "
            f"{p['impressions']} impressions, CTR {p['ctr']:.1%}"
        )

    return actions


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{v:+.1%}"


def _fmt_pos_delta(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{v:+.1f}"


def build_markdown(current: dict, diff: dict, actions: list[str],
                   as_of: str) -> str:
    totals = current.get("totals_7d", {}) or {}
    pct = diff.get("totals_pct", {}) or {}
    lines: list[str] = []
    lines.append(f"# SEO Weekly — {as_of}")
    lines.append("")
    lines.append(
        f"**Headline:** {totals.get('clicks', 0)} clicks "
        f"({_fmt_pct(pct.get('clicks'))}), "
        f"{totals.get('impressions', 0)} impressions "
        f"({_fmt_pct(pct.get('impressions'))}), "
        f"avg pos {totals.get('position', 0.0):.1f} "
        f"({_fmt_pos_delta(pct.get('position'))})"
    )
    lines.append("")

    lines.append("## Biggest wins")
    if diff["click_gains"]:
        for row in diff["click_gains"]:
            lines.append(
                f"- **{row['query']}** — clicks "
                f"{row['prev_clicks']} → {row['cur_clicks']} "
                f"({row['delta']:+d})"
            )
    else:
        lines.append("_No week-over-week click gainers._")
    lines.append("")

    lines.append("## Biggest drops")
    if diff["position_drops"] or diff["click_losses"]:
        for row in diff["position_drops"]:
            flag = " :warning:" if row["delta"] >= POSITION_DROP_ALERT else ""
            lines.append(
                f"- **{row['query']}** — pos {row['prev_pos']:.1f} → "
                f"{row['cur_pos']:.1f} ({row['delta']:+.1f}){flag}"
            )
        for row in diff["click_losses"]:
            lines.append(
                f"- **{row['query']}** — clicks "
                f"{row['prev_clicks']} → {row['cur_clicks']} "
                f"({row['delta']:+d})"
            )
    else:
        lines.append("_Nothing dropped significantly. Nice._")
    lines.append("")

    lines.append("## New in top 50")
    if diff["new_queries"]:
        for row in diff["new_queries"]:
            lines.append(
                f"- **{row['query']}** — {row['clicks']} clicks, "
                f"{row['impressions']} impressions, pos "
                f"{row['position']:.1f}"
            )
    else:
        lines.append("_No new entrants this week._")
    lines.append("")

    lines.append("## Dropped out of top 50")
    if diff["dropped_queries"]:
        for row in diff["dropped_queries"]:
            lines.append(
                f"- **{row['query']}** — had {row['clicks']} clicks / "
                f"{row['impressions']} impressions last week"
            )
    else:
        lines.append("_No drop-outs._")
    lines.append("")

    idx = current.get("indexation", {}) or {}
    lines.append("## Indexation")
    lines.append(
        f"- Pages receiving impressions (7d): "
        f"**{idx.get('pages_with_impressions_7d', 0)}** "
        f"({diff['indexation_delta']:+d} wk/wk)"
    )
    lines.append(
        f"- Pages receiving impressions (28d): "
        f"**{idx.get('pages_with_impressions_28d', 0)}**"
    )
    if idx.get("note"):
        lines.append(f"- _{idx['note']}_")
    lines.append("")

    lines.append("## Top 10 pages this week")
    pages = (current.get("pages_7d", []) or [])[:10]
    if pages:
        for p in pages:
            lines.append(
                f"- `{p['page']}` — {p['clicks']} clicks / "
                f"{p['impressions']} impressions, CTR {p['ctr']:.1%}, "
                f"pos {p['position']:.1f}"
            )
    else:
        lines.append("_No page-level data._")
    lines.append("")

    devices = current.get("devices_7d", []) or []
    countries = current.get("countries_7d", []) or []
    if devices or countries:
        lines.append("## Breakdown")
        if devices:
            lines.append("**Device:** " + ", ".join(
                f"{d.get('device', '?')} {d['clicks']}c/"
                f"{d['impressions']}i" for d in devices
            ))
        if countries:
            top_countries = countries[:6]
            lines.append("**Country:** " + ", ".join(
                f"{c.get('country', '?')} {c['clicks']}c/"
                f"{c['impressions']}i" for c in top_countries
            ))
        lines.append("")

    lines.append("## Suggested actions")
    if actions:
        for a in actions:
            lines.append(f"- {a}")
    else:
        lines.append("_Nothing urgent — ship more content._")
    lines.append("")

    lines.append(
        "_Generated by scripts/gsc_digest.py. Raw data: "
        "`data/gsc/*.json`._"
    )
    return "\n".join(lines)


def build_telegram_summary(current: dict, diff: dict, as_of: str) -> str:
    totals = current.get("totals_7d", {}) or {}
    pct = diff.get("totals_pct", {}) or {}
    lines = [
        f"SEO Weekly — {as_of}",
        (f"Clicks {totals.get('clicks', 0)} ({_fmt_pct(pct.get('clicks'))})"
         f" | Impr {totals.get('impressions', 0)} "
         f"({_fmt_pct(pct.get('impressions'))})"
         f" | Pos {totals.get('position', 0.0):.1f}"),
    ]
    if diff["click_gains"]:
        lines.append("Wins:")
        for r in diff["click_gains"][:3]:
            lines.append(f"  + {r['query']} ({r['delta']:+d})")
    if diff["position_drops"]:
        lines.append("Drops:")
        for r in diff["position_drops"][:3]:
            lines.append(
                f"  - {r['query']} pos {r['prev_pos']:.1f} "
                f"→ {r['cur_pos']:.1f}"
            )
    if diff["new_queries"]:
        lines.append("New:")
        for r in diff["new_queries"][:3]:
            lines.append(f"  ★ {r['query']} ({r['clicks']}c)")
    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        log.info("Telegram vars not set — skipping notification")
        return False
    import requests
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
        return True
    except requests.RequestException:
        log.exception("Telegram send failed")
        return False


def _latest_two_snapshots(data_dir: Path) -> tuple[Path | None, Path | None]:
    files = sorted(data_dir.glob("*.json"))
    if not files:
        return None, None
    if len(files) == 1:
        return files[-1], None
    return files[-1], files[-2]


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    parser.add_argument("--telegram", action="store_true",
                        help="Also send compressed summary to Telegram")
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir)
    if not data_dir.is_dir():
        log.warning("no data dir at %s — nothing to digest", data_dir)
        return 4

    cur_path, prev_path = _latest_two_snapshots(data_dir)
    if cur_path is None:
        log.warning("no GSC snapshots in %s — not enough data", data_dir)
        return 4

    current = json.loads(cur_path.read_text())
    previous = json.loads(prev_path.read_text()) if prev_path else None

    if not current.get("queries_7d") and not current.get("pages_7d"):
        log.warning("snapshot %s is empty — writing minimal digest", cur_path)

    diff = compute_diff(current, previous)
    actions = suggest_actions(current)
    md = build_markdown(current, diff, actions, args.as_of)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"weekly-seo-{args.as_of}.md"
    out_path.write_text(md)
    log.info("wrote %s", out_path)

    if args.telegram:
        summary = build_telegram_summary(current, diff, args.as_of)
        send_telegram(summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
