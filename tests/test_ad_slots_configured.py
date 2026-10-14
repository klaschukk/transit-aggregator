"""Every ad_slot('<key>') a template calls must have an entry in ADSENSE_SLOTS.

Five hub pages called ad_slot() with keys that were never added to the config,
so those slots silently rendered no unit for months. This is a static scan,
like test_i18n_keys_exist: it fails when the template is written, not when
someone notices the missing revenue."""
import json
import re
from pathlib import Path

import config

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / 'app' / 'templates'
CALL_RE = re.compile(r"""ad_slot\(\s*['"]([a-z_]+)['"]""")


def _used_keys() -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for tpl in TEMPLATES.rglob('*.html'):
        if tpl.name == '_ad_slot.html':   # the macro's own usage examples
            continue
        for key in CALL_RE.findall(tpl.read_text(encoding='utf-8')):
            found.setdefault(key, set()).add(str(tpl.relative_to(TEMPLATES)))
    return found


def test_every_template_slot_is_configurable():
    missing = {k: v for k, v in _used_keys().items() if k not in config.Config.ADSENSE_SLOTS}
    assert not missing, f'ad_slot keys with no ADSENSE_SLOTS entry: {missing}'


def test_local_file_supplies_an_id_and_env_wins(tmp_path, monkeypatch):
    (tmp_path / 'data').mkdir()
    (tmp_path / 'data' / 'ads.local.json').write_text(json.dumps({
        'ADSENSE_SLOT_PLANNER_MID': '1234567890',
        'ADSENSE_SLOT_PLANNER_HUB': 'ca-pub-123/456',   # pasted the wrong thing
    }))
    monkeypatch.setattr(config, 'BASE_DIR', tmp_path)
    monkeypatch.delenv('ADSENSE_SLOT_PLANNER_MID', raising=False)
    monkeypatch.delenv('ADSENSE_SLOT_PLANNER_HUB', raising=False)
    assert config._ad_slot_id('PLANNER_MID') == '1234567890'
    assert config._ad_slot_id('PLANNER_HUB') == ''
    assert config._ad_slot_id('ABOUT_BOTTOM') == ''
    monkeypatch.setenv('ADSENSE_SLOT_PLANNER_MID', '999')
    assert config._ad_slot_id('PLANNER_MID') == '999'


def test_example_file_lists_only_real_slots():
    example = json.loads((ROOT / 'data' / 'ads.local.json.example').read_text())
    for name in example:
        if name.startswith('_'):
            continue
        assert name.removeprefix('ADSENSE_SLOT_').lower() in config.Config.ADSENSE_SLOTS, name
