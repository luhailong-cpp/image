from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c01-v1");R=D/'alignment-repair-v2';R.mkdir(exist_ok=True)
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()}
prev=D/'alignment-repair-v1';host=Path(r"C:/Users/luyua/.codex/generated_images/01a11b05-7488-7d11-bfe3-c3b64c8f7651/exec-a5210dce-43e0-414f-b244-db012bd8d816.png");shutil.copy2(host,prev/'native.png');(prev/'rejection.json').write_text(json.dumps({"status":"rejected-never-used","reason":"Did not preserve real lower panel geometry or motif; panel width still deviated from fixed real source.","output":ref(prev/'native.png'),"actualReturnedModel":None,"actualReturnedQuality":None},indent=2),encoding="utf-8")
N=np.array(Image.open(D/'native.png').convert('RGBA')); C=np.array(Image.open(D/'context.png').convert('RGBA'));prep=json.loads((D/'preparation.json').read_text(encoding='utf-8'));bottom=prep['coupledBottom'];S=np.array(Image.open(bottom['file']).convert('RGBA'))
base=np.zeros((1254,1254,4),dtype=np.uint8);base[:789]=N[350:1139];right=C[350:1139,1024:];base[:789,1024:]=right
base[789:,115:]=S[:465,:1139]
Image.fromarray(base).save(R/'source-composite.png')
mask=np.zeros((1254,1254),dtype=np.uint8);mask[180:789,:1024]=255;mask[110:789,220:650]=255
mask[base[:,:,3]==0]=255
target=base.copy();target[mask==255]=0;Image.fromarray(target).save(R/'edit-target.png');Image.fromarray(mask).save(R/'mask.png')
world=[36749,19691,38003,20945];master=Path(r"D:/work/image/tianyong_festival_hd_20260910/tianyong_city_master_6144.png")
Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(R/'layout-reference-only.png')
prompt="""Use case: precise-object-edit. Fill only the transparent masked region of LAST IMAGE4. Return one opaque native1254x1254 image with the exact same world crop.
Image1 approved style, image2 a small nearby foliage/material swatch only, image3 SAME WORLD CROP canonical layout, image4 SINGLE EDIT TARGET. The large visible BOTTOM465 rows and visible RIGHT230 pixels are actual accepted native map and must stay in their EXACT coordinates. They have the correct real red plaque width, gold motif, lantern silhouette, planter and railing. Continue these accepted features UPWARD through the transparent band into the small fixed top crown. Do not narrow the plaque, recenter the motif or relocate any visible geometry.
Red plaque sides continue upward from the bottom at x250 and600; keep a red raised outer rim, NO long gold outline. Match the actual centered floral/cloud gold ornaments that continue from the lower panel. Continue the lower ornament exactly, no duplicate motif or transparent ghost. Retain upper red curled crown, hanging red bead and jade roof above the crop. Left partial orange lantern meets its fixed bottom contour. Right leafy bush, trunk, rectangular stone planter and ivory wall meet the right and bottom accepted contours without displaced leaves or doubled edges.
Draw only missing native details inside the black/transparent area. All visible opaque areas must remain literally unchanged. The entire composition stays locked to image4. No readable text, crack, thin diagonal fracture, grunge, UI, figure, watermark, scaling, crop change or warp. Clean bright polished rounded Daoist Q game art, same lighting and smooth ivory bevels."""
refs=[Path(r"D:/work/image/designs/gameplay-ui/04-guild.png"),D/'nearby-native-material-swatch.png',R/'layout-reference-only.png',R/'edit-target.png']; req={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
(R/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'preparation.json').write_text(json.dumps({"globalCropLTRB":world,"mainNativeYOffset":350,"actualBottomSource":bottom,"sourceMain":ref(D/'native.png'),"sourceContext":ref(D/'context.png'),"sourceComposite":ref(R/'source-composite.png'),"mask":ref(R/'mask.png'),"references":[ref(p) for p in refs],"nativeScale":1,"configTarget":json.loads((D/'request.json').read_text(encoding='utf-8'))['configSnapshot'],"actualSubmittedModel":None,"actualSubmittedQuality":None},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(req))

