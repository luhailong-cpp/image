"""Legacy command delegates to the current E phase reviewer; old holds are inactive."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('run_phase_review_v2.py')),run_name='__main__')
