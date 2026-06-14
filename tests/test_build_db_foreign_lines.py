"""Tests for build_db._drop_foreign_coach_lines.

International coach routes (FlixBus N981 'München => Sofia') were getting
ingested as Niš *city* lines, polluting /gradski/nis/ and generating thin
indexable line pages. The cleanup drops a city line when most of its stops are
outside Serbia, along with its links and now-orphaned foreign stops.
"""
import duckdb

from data.pipelines import build_db


def _schema_conn():
    conn = duckdb.connect(':memory:')
    build_db._create_schema(conn)
    return conn


def _seed(conn):
    conn.executemany("INSERT INTO city_lines VALUES (?,?,?,?,?,?,?,?)", [
        (1, 'nis', '12', 'Legit Niš line', 'linija-12', 'bus', '#000', None),
        (2, 'nis', 'N981', 'Flixbus N981: München => Sofia',
         'linija-n981', 'bus', '#000', None),
    ])
    conn.executemany("INSERT INTO city_stops VALUES (?,?,?,?,?,?,?)", [
        (1, 'nis', 'Trg', 'trg', 43.32, 21.89, None),      # in Serbia
        (2, 'nis', 'München', 'munchen', 48.14, 11.55, None),  # foreign
        (3, 'nis', 'Wien', 'wien', 48.19, 16.41, None),        # foreign
    ])
    conn.executemany("INSERT INTO city_line_stops VALUES (?,?,?)", [
        (1, 1, 1),          # legit line → Serbian stop
        (2, 2, 1), (2, 3, 2),  # bogus line → foreign stops
    ])


def test_drops_foreign_line_and_orphan_stops():
    conn = _schema_conn()
    _seed(conn)
    # a GTFS trip pointing at the bogus line — the FK must not block the delete
    conn.execute("INSERT INTO gtfs_trips VALUES ('t1','r1','RD',0,2)")

    dropped = build_db._drop_foreign_coach_lines(conn)
    assert dropped == 1

    lines = [r[0] for r in conn.execute("SELECT id FROM city_lines ORDER BY id").fetchall()]
    assert lines == [1]   # bogus line gone, legit line kept

    stops = [r[0] for r in conn.execute("SELECT id FROM city_stops ORDER BY id").fetchall()]
    assert stops == [1]   # foreign stops swept, Serbian stop kept

    # the GTFS trip survives with its line_id nulled, not deleted
    row = conn.execute("SELECT line_id FROM gtfs_trips WHERE trip_id='t1'").fetchone()
    assert row[0] is None

    assert conn.execute(
        "SELECT COUNT(*) FROM city_line_stops WHERE line_id=2").fetchone()[0] == 0


def test_clean_db_drops_nothing():
    conn = _schema_conn()
    conn.execute("INSERT INTO city_lines VALUES "
                 "(1,'nis','12','L','linija-12','bus','#000',NULL)")
    conn.execute("INSERT INTO city_stops VALUES (1,'nis','Trg','trg',43.3,21.9,NULL)")
    conn.execute("INSERT INTO city_line_stops VALUES (1,1,1)")
    assert build_db._drop_foreign_coach_lines(conn) == 0
    assert conn.execute("SELECT COUNT(*) FROM city_lines").fetchone()[0] == 1


def test_line_without_coords_is_kept():
    # Can't judge a line whose stops have no coordinates → leave it alone.
    conn = _schema_conn()
    conn.execute("INSERT INTO city_lines VALUES "
                 "(1,'nis','7','L','linija-7','bus','#000',NULL)")
    conn.execute("INSERT INTO city_stops VALUES (1,'nis','X','x',NULL,NULL,NULL)")
    conn.execute("INSERT INTO city_line_stops VALUES (1,1,1)")
    assert build_db._drop_foreign_coach_lines(conn) == 0
    assert conn.execute("SELECT COUNT(*) FROM city_lines").fetchone()[0] == 1


def test_minority_foreign_stops_line_is_kept():
    # A border line with 1 foreign stop out of 3 is still a city line.
    conn = _schema_conn()
    conn.execute("INSERT INTO city_lines VALUES "
                 "(1,'nis','9','L','linija-9','bus','#000',NULL)")
    conn.executemany("INSERT INTO city_stops VALUES (?,?,?,?,?,?,?)", [
        (1, 'nis', 'A', 'a', 43.3, 21.9, None),
        (2, 'nis', 'B', 'b', 43.4, 21.8, None),
        (3, 'nis', 'C', 'c', 48.1, 11.5, None),  # one foreign (1/3 < 0.5)
    ])
    conn.executemany("INSERT INTO city_line_stops VALUES (?,?,?)",
                     [(1, 1, 1), (1, 2, 2), (1, 3, 3)])
    assert build_db._drop_foreign_coach_lines(conn) == 0
