"""Deprecated partial audit entrypoint; current per-direction inventory is authoritative."""

# RETIRED_20261005: direct human timing correction supersedes historical writers.
raise SystemExit("Retired: use tools/build_preview.py, build_delivery.py, build_run_board.py and build_timing_grounding.py; run60ms/960ms.")
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('run_refresh_legacy_review.py')),run_name='__main__')
