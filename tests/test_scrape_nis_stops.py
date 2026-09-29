"""OSM city-line importer must not turn passing coach routes into city lines."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    'scrape_nis_stops',
    Path(__file__).parent.parent / 'data' / 'pipelines' / 'scrape_nis_stops.py')
sns = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sns)


def _route(rid, ref, name, stop_ids, **tags):
    return {'id': rid, 'tags': {'ref': ref, 'name': name, **tags},
            'members': [{'type': 'node', 'ref': n, 'role': 'stop'} for n in stop_ids]}


NODES = {
    1: {'lat': 45.26, 'lon': 19.83, 'tags': {'name': 'Železnička stanica'}},
    2: {'lat': 45.25, 'lon': 19.84, 'tags': {'name': 'Centar'}},
    3: {'lat': 48.19, 'lon': 16.41, 'tags': {'name': 'Vienna International Busterminal'}},
    4: {'lat': 45.12, 'lon': 19.73, 'tags': {'name': 'Vrdnik'}},
}


def test_build_lines_skips_foreign_stops_and_coach_operators():
    routes = [
        _route(10, '4', 'Bus 4', [1, 2]),
        _route(11, '86', 'Vrdnik', [1, 4]),                      # suburban, in Serbia
        _route(12, '990', 'Flixbus 990: Wien => Pančevo', [3, 1]),
        _route(13, 'N7', 'Night coach', [1, 2], operator='FlixBus'),
    ]
    refs = {l['number'] for l in sns.build_lines(routes, NODES)}
    assert refs == {'4', '86'}


def test_is_intercity_ignores_name_only_stops():
    assert not sns.is_intercity({'name': 'CENTAR — TELEP', 'stops': [{'name': 'Centar'}]})
    assert not sns.is_intercity({'name': 'KAĆ', 'stops': ['Centar', 'Kać']})
    assert sns.is_intercity({'name': 'Flixbus 1910: Beograd => Budapest', 'stops': []})
