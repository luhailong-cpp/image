# Current preview adapter: preserves approved images and existing visual reviews.
from pathlib import Path
import runpy,sys
ROOT=Path(__file__).resolve().parents[2]
sys.argv=[str(ROOT/'tools/build_review_previews.py')]+['run/E', 'run/NE', 'run/NW']
runpy.run_path(sys.argv[0],run_name='__main__')
