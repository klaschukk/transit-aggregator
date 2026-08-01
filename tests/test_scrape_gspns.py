"""Tests for the JGSP Novi Sad scraper's schedule-validity date discovery.

The line-list API returns an empty <select> for any vaziod (schedule-validity
date) that JGSP no longer publishes, so hardcoding one silently drops the whole
city from the build. These tests pin the discovery of that date from the live
schedule page markup.
"""
import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = (Path(__file__).parent.parent / 'data' / 'pipelines'
               / 'scrape_gspns.py')


def _load_module():
    spec = importlib.util.spec_from_file_location('scrape_gspns', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scrape_gspns = _load_module()


def test_parse_vaziod_reads_single_option() -> None:
    """The live page shape: one option, no selected attribute."""
    html = """
        <select class="form-control" id='vaziod' onchange="lista_linija();" name=vaziod>
            <option value="2026-06-22"  >
                22.06.2026
            </option>
        </select>
    """
    assert scrape_gspns.parse_vaziod(html) == '2026-06-22'


def test_parse_vaziod_prefers_selected_option() -> None:
    """When JGSP lists several validity periods, the selected one is current."""
    html = """
        <select id='vaziod' name=vaziod>
            <option value="2026-04-01">01.04.2026</option>
            <option value="2026-06-22" selected>22.06.2026</option>
            <option value="2026-09-01">01.09.2026</option>
        </select>
    """
    assert scrape_gspns.parse_vaziod(html) == '2026-06-22'


def test_parse_vaziod_falls_back_to_first_option() -> None:
    html = """
        <select id="vaziod">
            <option value="2026-06-22">22.06.2026</option>
            <option value="2026-09-01">01.09.2026</option>
        </select>
    """
    assert scrape_gspns.parse_vaziod(html) == '2026-06-22'


@pytest.mark.parametrize('html', [
    '',
    '<html><body>no select here</body></html>',
    "<select id='vaziod'></select>",
    "<select id='vaziod'><option value='lat'>LAT</option></select>",
])
def test_parse_vaziod_returns_none_when_absent(html: str) -> None:
    """Non-date options (the language switcher) must never be mistaken for one."""
    assert scrape_gspns.parse_vaziod(html) is None


def test_parse_vaziod_ignores_other_selects() -> None:
    """The page has several selects; only #vaziod carries validity dates."""
    html = """
        <select id='rv'><option value='rvg' selected>Gradski</option></select>
        <select id='vaziod'><option value="2026-06-22">22.06.2026</option></select>
    """
    assert scrape_gspns.parse_vaziod(html) == '2026-06-22'


def test_parse_line_list_extracts_number_and_name() -> None:
    """Shape actually returned by /red-voznje/lista-linija."""
    html = (
        '<select id="linija">'
        '<option value="1*">1 KLISA-CENTAR-LIMAN I</option>'
        '<option value="3A.">3A ZEL.STANICA - POBEDA</option>'
        '</select>'
    )
    lines = scrape_gspns.parse_line_list(html)
    assert [line['number'] for line in lines] == ['1', '3A']
    # Hyphens between terminus names are normalised to em-dashes.
    assert lines[0]['name'] == 'KLISA — CENTAR — LIMAN I'
    assert lines[1]['name'] == 'ZEL.STANICA — POBEDA'
