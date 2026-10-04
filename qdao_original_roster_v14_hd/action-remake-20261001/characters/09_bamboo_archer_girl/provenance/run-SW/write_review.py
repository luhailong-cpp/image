# Current preview adapter: preserves approved images and existing visual reviews.
from pathlib import Path
import runpy,sys
ROOT=Path(__file__).resolve().parents[2]
sys.argv=[str(ROOT/'tools/build_review_previews.py')]+['run/SW']
runpy.run_path(sys.argv[0],run_name='__main__')
