from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h
h.O=O/'west'
p='Use case: minimal local inpainting. Image1 is a completed native1254 harbor painting. Image2 approved PRIMARY style. Remove ONLY the short dark vertical stone joint at x620..626, y895..1045 in the small BLUE WALL opening between the wooden beams. Continue the SAME SINGLE blue stone face across this removed line. Retain its existing diagonal horizontal wall joint, all blue stone paint around it, every wooden beam outline and every other pixel/geometry. Do not touch posts or wood grain, do not modify composition. Exact1254x1254 crop. No new objects/joints, no blur, grain or sharpen halo.'
h.savecall('west-wall-clean',p,[h.O/'west-1-generated.png',h.STYLE],['native repaired western joint with one unwanted stone subdivision','actual approved style04guild'])
