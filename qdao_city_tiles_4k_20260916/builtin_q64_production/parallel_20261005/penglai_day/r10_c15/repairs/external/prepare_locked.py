from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h
h.O=O/'north'
p='Use case: precise local inpainting. Image1 is native1254 source containing a single remaining JOIN ERROR. Image2 is approved style. Fix only the tiny rectangular interrupted wood-paint and diagonal groove at x557,y580..640. The section LEFT of x557 is locked correct. The existing diagonal thin plank groove must meet that left endpoint exactly at x557 around y588, then join the right groove by x700 around y505. Use a subtle smooth continuous curve inside x557..720 if necessary; never shift or straighten the whole groove outside this narrow region. Remove the small flat rectangular paint patch immediately below the endpoint (x557..660,y600..645), keeping the surrounding original warm wood grain. Keep every other plank, post, rail, stone and shadow unchanged. No new lines or objects. Edit only x557..740,y515..700. Output exactly1254x1254, same crop.'
h.savecall('north-locked-return',p,[O/'qa-north-v2-1.png',h.STYLE],['native composite at locked corner continuation','actual approved style04guild'])
