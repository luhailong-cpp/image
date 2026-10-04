"""Deprecated partial audit entrypoint; current per-direction inventory is authoritative."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('run_refresh_legacy_review.py')),run_name='__main__')
