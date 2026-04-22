"""Content generators — rules-based prose that enriches thin PSEO pages.

All generators are deterministic: same input → same output. Output varies
across adjacent pages because we hash (slug + salt) with different salts
per paragraph, so nearby stops don't land on the same template twice.
"""
