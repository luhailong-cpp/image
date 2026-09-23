from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent));import archive_generation as archive
GEN=HERE.parent.parent/'06-generation'
r=json.loads((GEN/'NW08-single-v1/request.json').read_text())
r['referenced_image_paths'][2]=str(GEN/'NW07-single-v1/raw.png')
r['prompt'] += '\nCRITICAL: preserve the SAME FOOT ORDER as references 3 and 4 (NW07 and NW09): SCREEN-LEFT boot must be LOW and nearer viewer, SCREEN-RIGHT boot HIGHER farther away. Do NOT copy the opposite split from idle or swap to left leading. At NW08 the LEFT boot stays at about x43% y92%, heel up with sole partly visible; RIGHT boot at x56% y86% extends away ready to land. RIGHT boot must NOT be the bottommost boot. Need coherent support and visible left toe on ground. Change knee and ankle subtly from NW07 but newly paint exact pre-contact action.\n'
archive.prepare('NW08-single-v2',r['prompt'],r['referenced_image_paths'])
