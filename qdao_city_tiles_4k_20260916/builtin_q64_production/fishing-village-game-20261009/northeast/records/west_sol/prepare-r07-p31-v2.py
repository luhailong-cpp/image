import sys
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
from PIL import Image
p='r07_c11_p31';v='v2';src=w.Z/f'native/{p}-v1-west_sol.png';d=w.read(w.R/f'{p}-v1.plan.json');guide=w.Z/f'guides/{p}-{v}-west_sol.restored-native-right.png'
im=Image.open(src).convert('RGB');neighbor=w.Z/'native/r07_c11_p32-v1-west_sol.png';im.paste(Image.open(neighbor).crop((0,0,230,1254)),(1024,0));im.save(guide)
refs=[w.ref(guide,'PRIMARY edit target: previous native image with exact right230 neighbor restored')]+w.mandatory()
prompt="""Edit IMAGE1 only. Repair the stepped bronze lamp pedestal where it meets the right native anchor: this image contains the exact correct rightmost230 pixels (x1024..1254) copied from the existing neighbor. Keep that right230 region FIXED, including every bronze edge, stone joint and tiny grass mark. Redraw only the bronze pedestal to its LEFT so ALL its levels and outer contour join the existing bronze fragments in that right strip seamlessly. There must be ONE connected broad stepped bronze plinth, with no duplicated small block, offset rim, rectangular clipping or abrupt step at x1024 or x1139. The pedestal extends slightly farther right than the previous candidate. Preserve the same tall shaft at x710..930, top230 pixels, stone texture, daylight and framing. Keep paving continuous around the corrected outer silhouette. Do not add objects, blur, resize or move the whole scene. Images2/3/4 are map/material/DaoistQ style only. Opaque native1254 square, r07_c11_p31 world[40845,26509,42099,27763], core[115,115,1139,1139]."""
d.update(version=v,preparedAtUtc=w.now(),references=refs,guide=w.ref(guide),guidePurpose='Exact native copy of prior candidate with original right230 restored; edit guide only',previousCandidate=w.ref(src),guideOperations=[dict(operation='integer native paste',source=w.ref(neighbor),sourceCropBox=[0,0,230,1254],targetPasteAt=[1024,0])],formalAccepted=False)
w.write(w.R/f'{p}-{v}.plan.json',d);(w.R/f'{p}-{v}.prompt.txt').write_text(prompt,encoding='utf-8')
w.write(w.R/f'{p}-{v}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
w.write(w.R/f'{p}-v1.review.json',dict(native=w.ref(src),reviewedAtUtc=w.now(),status='not_selected_right_geometry_error',issues=['Pedestal narrowed/moved relative to right neighbor; duplicated/offset lower-right silhouette across actual core seam'],formalAccepted=False))

