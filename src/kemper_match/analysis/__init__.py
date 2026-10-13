"""Guitar-stem analysis: structure -> tone segments -> features -> tone clusters.

Each stage reads the previous stage's file from ``analysis/<song_id>/`` and
writes its own. The order is fixed in ``cli.main.analyze``.
"""
