"""Native apply entry through the existing strict memo/depth128 runner.
Only dispatch changes; original pixel/hash/ancestor/cycle checks are retained.
"""
from pathlib import Path
import sys,runpy
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
import cross_tile_native_repair as cross
import apply_native_tile_repair as native
cross.main=native.main
runpy.run_path(str(Z/'qa/run_cross_with_strict_memo_depth128_20261013.py'),run_name='__main__')

