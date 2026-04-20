"""
Tests for scripts/gsc_digest.py — pure-function diff + markdown.

We drive the fetcher with hand-rolled snapshot dicts so no network
or credentials are required. CLI integration is smoke-tested through
`main()` against a temp directory.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIGEST_PATH = PROJECT_ROOT / "scripts" / "gsc_digest.py"


@pytest.fixture(scope="module")
def digest():
    """Load scripts/gsc_digest.py as a module despite the `scripts/`
    directory not being a package."""
    spec = importlib.util.spec_from_file_location("gsc_digest", DIGEST_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _row(query, clicks=10, impressions=200, ctr=0.05, position=5.0):
    return {
        "query": query, "clicks": clicks, "impressions": impressions,
        "ctr": ctr, "position": position,
    }


def _page_row(page, clicks=10, impressions=200, ctr=0.05, position=5.0):
    return {
        "page": page, "clicks": clicks, "impressions": impressions,
        "ctr": ctr, "position": position,
    }


def _snapshot(queries=None, pages=None, indexation_pages=100,
              totals=None):
    return {
        "fetched_at": "2026-04-20",
        "site_url": "sc-domain:prevozni.com",
        "window_7d": {"start": "2026-04-13", "end": "2026-04-20"},
        "queries_7d": queries or [],
        "pages_7d": pages or [],
        "countries_7d": [],
        "devices_7d": [],
        "indexation": {
            "pages_with_impressions_7d": indexation_pages,
            "pages_with_impressions_28d": indexation_pages * 3,
            "note": "approximation",
        },
        "totals_7d": totals or {
            "clicks": sum(r["clicks"] for r in (queries or [])),
            "impressions": sum(r["impressions"] for r in (queries or [])),
            "ctr": 0.05,
            "position": 7.5,
        },
    }


def test_diff_new_and_dropped_queries(digest):
    current = _snapshot(queries=[
        _row("autobus beograd nis", clicks=30),
        _row("voz beograd novi sad", clicks=12),
        _row("prevoz srbija", clicks=5),           # new
    ])
    previous = _snapshot(queries=[
        _row("autobus beograd nis", clicks=30),
        _row("voz beograd novi sad", clicks=12),
        _row("stara karta", clicks=8),             # dropped
    ])

    diff = digest.compute_diff(current, previous)
    new_q = [r["query"] for r in diff["new_queries"]]
    dropped_q = [r["query"] for r in diff["dropped_queries"]]

    assert new_q == ["prevoz srbija"]
    assert dropped_q == ["stara karta"]


def test_position_drop_above_threshold_is_flagged(digest):
    current = _snapshot(queries=[
        _row("autobus beograd nis", position=12.0, impressions=500),
    ])
    previous = _snapshot(queries=[
        _row("autobus beograd nis", position=6.0, impressions=500),
    ])
    diff = digest.compute_diff(current, previous)

    assert len(diff["position_drops"]) == 1
    drop = diff["position_drops"][0]
    assert drop["query"] == "autobus beograd nis"
    assert drop["delta"] == pytest.approx(6.0)


def test_position_drop_below_threshold_is_ignored(digest):
    current = _snapshot(queries=[
        _row("autobus beograd nis", position=7.0),
    ])
    previous = _snapshot(queries=[
        _row("autobus beograd nis", position=6.0),  # only 1 place
    ])
    diff = digest.compute_diff(current, previous)
    assert diff["position_drops"] == []


def test_click_loss_is_flagged_for_non_trivial_queries(digest):
    # Query with 100 clicks drops to 50 — should flag.
    # Query with 3 clicks drops to 1 — should NOT flag (too small).
    current = _snapshot(queries=[
        _row("big", clicks=50),
        _row("tiny", clicks=1),
    ])
    previous = _snapshot(queries=[
        _row("big", clicks=100),
        _row("tiny", clicks=3),
    ])
    diff = digest.compute_diff(current, previous)
    losses = {r["query"] for r in diff["click_losses"]}
    assert "big" in losses
    assert "tiny" not in losses


def test_compute_diff_with_no_previous_snapshot(digest):
    # First run ever — previous is None, everything current is "new".
    current = _snapshot(queries=[_row("prevoz srbija", clicks=15)])
    diff = digest.compute_diff(current, None)

    assert len(diff["new_queries"]) == 1
    assert diff["dropped_queries"] == []
    assert diff["position_drops"] == []
    assert diff["totals_pct"]["clicks"] is None  # no baseline


def test_empty_snapshot_does_not_crash(digest):
    empty = _snapshot(queries=[], pages=[], indexation_pages=0,
                      totals={"clicks": 0, "impressions": 0,
                              "ctr": 0.0, "position": 0.0})
    diff = digest.compute_diff(empty, empty)
    actions = digest.suggest_actions(empty)
    md = digest.build_markdown(empty, diff, actions, "2026-04-20")

    assert "not enough data" in md.lower() or "no " in md.lower()
    assert "2026-04-20" in md
    assert diff["new_queries"] == []


def test_suggest_actions_picks_high_impression_low_ctr(digest):
    current = _snapshot(queries=[
        # High impressions + bad CTR + decent position → rewrite action
        _row("prevoz srbija", clicks=2, impressions=800,
             ctr=0.0025, position=6.0),
        # Healthy — should not trigger
        _row("karte autobus", clicks=200, impressions=1000,
             ctr=0.2, position=3.0),
    ])
    actions = digest.suggest_actions(current)
    joined = "\n".join(actions)
    assert "prevoz srbija" in joined
    assert "karte autobus" not in joined


def test_build_markdown_headline_has_totals(digest):
    current = _snapshot(
        queries=[_row("a", clicks=10, impressions=100)],
        totals={"clicks": 120, "impressions": 5000,
                "ctr": 0.024, "position": 8.3},
    )
    previous = _snapshot(
        queries=[_row("a", clicks=10, impressions=100)],
        totals={"clicks": 100, "impressions": 4000,
                "ctr": 0.025, "position": 8.0},
    )
    diff = digest.compute_diff(current, previous)
    md = digest.build_markdown(current, diff, [], "2026-04-20")

    assert "# SEO Weekly — 2026-04-20" in md
    assert "120 clicks" in md
    assert "+20.0%" in md          # 120 vs 100 clicks
    assert "5000 impressions" in md
    assert "## Suggested actions" in md


def test_indexation_delta_computed(digest):
    current = _snapshot(indexation_pages=120)
    previous = _snapshot(indexation_pages=100)
    diff = digest.compute_diff(current, previous)
    assert diff["indexation_delta"] == 20


def test_main_emits_file_when_snapshots_present(digest, tmp_path):
    # Arrange two snapshots in a fake data dir.
    data_dir = tmp_path / "gsc"
    data_dir.mkdir()
    out_dir = tmp_path / "out"

    prev = _snapshot(queries=[_row("a", clicks=10)])
    cur = _snapshot(queries=[
        _row("a", clicks=10),
        _row("b", clicks=5),         # new entrant
    ])
    (data_dir / "2026-04-13.json").write_text(json.dumps(prev))
    (data_dir / "2026-04-20.json").write_text(json.dumps(cur))

    rc = digest.main([
        "--data-dir", str(data_dir),
        "--out-dir", str(out_dir),
        "--as-of", "2026-04-20",
    ])
    assert rc == 0

    out_file = out_dir / "weekly-seo-2026-04-20.md"
    assert out_file.exists()
    body = out_file.read_text()
    assert "# SEO Weekly — 2026-04-20" in body
    assert "**b**" in body           # new entrant listed


def test_main_returns_4_when_no_snapshots(digest, tmp_path):
    data_dir = tmp_path / "empty-gsc"
    data_dir.mkdir()
    rc = digest.main([
        "--data-dir", str(data_dir),
        "--out-dir", str(tmp_path / "out"),
        "--as-of", "2026-04-20",
    ])
    assert rc == 4


def test_telegram_summary_is_compact(digest):
    current = _snapshot(
        queries=[_row("a", clicks=10)],
        totals={"clicks": 50, "impressions": 1000,
                "ctr": 0.05, "position": 6.0},
    )
    previous = _snapshot(
        queries=[_row("a", clicks=8)],
        totals={"clicks": 40, "impressions": 900,
                "ctr": 0.044, "position": 6.5},
    )
    diff = digest.compute_diff(current, previous)
    summary = digest.build_telegram_summary(current, diff, "2026-04-20")

    assert "SEO Weekly" in summary
    assert "2026-04-20" in summary
    # compact: under a handful of lines, never overflows a Telegram
    # message's 4096 char limit
    assert summary.count("\n") < 20
    assert len(summary) < 1500
