from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent; G=Path(r'C:\Users\luyua\.codex\generated_images\01a09f27-0628-78e0-84b5-2472601dc072')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def file(p):
 p=Path(p);d={'path':str(p),'sha256':sha(p)}
 if p.suffix=='.png':
  with Image.open(p) as im:d.update(size=list(im.size),mode=im.mode,rgba_sha256=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
 return d
# Actual built-in image_gen outputs and reference chains, including rejected attempts.
data=[
('E/generated-raw-v1.png','db9ab2f9-3893-4cb5-bb4d-2a98071358cc','E/prompt.txt',['E/reference-03-04-07-08.png'],'rejected','04 has a third arm; 08 superseded'),
('E/phase04-arm-fix-rejected.png','711d35e1-d5f5-4f72-9b7c-588b53cd579a','E/phase04-arm-fix-prompt.txt',['E/phase04-extra-arm-reference.png'],'rejected','empty extra sleeve remains'),
('E/generated-two-cell-raw.png','10f992aa-ed63-4f57-8183-3c36a1b776d6','E/two-cell-prompt.txt',['E/reference-only-04-08.png'],'selected','both 04/08 retained; original opposite arm phases preserved'),
('S/generated-two-cell-raw.png','880ab05f-2c24-4717-a3c3-6509c9c300c8','S/two-cell-prompt.txt',['S/reference-only-04-08.png'],'partially_selected','top04 retained; bottom08 rejected same arm phase as04'),
('S/phase08-native-cell.png','1c53db35-842b-4d7d-89a8-cfb9e6e1980c','S/phase08-prompt.txt',['S/original-08-cell.png'],'selected','single08 retains opposite arm phase'),
('SE/generated-two-cell-raw.png','ca2d19df-d5d2-41b4-b056-83ebf8e4e231','SE/two-cell-prompt.txt',['SE/reference-only-04-08.png'],'selected','low advancing legs; both arm phases retained'),
('SW/generated-two-cell-raw.png','1e101578-6ed9-4866-a871-d4b4ebab6034','SW/two-cell-prompt.txt',['SW/reference-only-04-08.png'],'selected','near/far thigh occlusion and left-hip drum retained'),
('W/generated-two-cell-too-high.png','e695f1da-1c98-4ec7-8324-e4276833a076','W/two-cell-prompt.txt',['W/reference-only-04-08.png'],'rejected','free feet still too high'),
('W/generated-two-cell-intermediate.png','56ec5701-0c83-4b6d-b099-dec1ae09b23c','W/lower-more-prompt.txt',['W/generated-two-cell-too-high.png'],'rejected','free feet lower but still too high for natural pre-contact'),
('W/generated-two-cell-raw.png','8e3a13e6-b34a-47ad-94d9-2f22a082b7ee','W/heel-near-ground-prompt.txt',['W/generated-two-cell-intermediate.png'],'selected','low heel clearance with both opposite arms preserved'),
('idle-NE/rejected-over-small-head.png','e541c14a-c0d1-4bbc-9b95-bfcceab726af','idle-NE/prompt.txt',['idle-NE/idle-left-walk-right-reference.png'],'rejected','head and whole body too small'),
('idle-NE/rejected-head-body-too-small-v2.png','3f066dc3-cf36-4355-90dd-7854cc09bd96','idle-NE/subtle-prompt.txt',['idle-NE/original-idle-cell.png'],'rejected','head and body still too small'),
('idle-NE/head-too-narrow-v3.png','4dcc4e9c-66b0-4546-895d-fcb4141ad15e','idle-NE/native-coordinate-prompt.txt',['idle-NE/original-upscaled-reference.png'],'intermediate','body restored but head too narrow'),
('idle-NE/generated-raw.png','b696956e-9b31-4473-9cc4-7449c133da3f','idle-NE/rounder-head-prompt.txt',['idle-NE/head-too-narrow-v3.png'],'selected','rounder head; upper100 width156 vs walk152'),
('idle-NW/head-too-small-v1.png','22a9f907-a651-4d2f-bd86-2a44497214bf','idle-NW/prompt.txt',['idle-NW/original-upscaled-reference.png'],'intermediate','head too small'),
('idle-NW/generated-raw.png','c03e5878-83bc-4679-86f3-5c175d420f49','idle-NW/head-recover-prompt.txt',['idle-NW/head-too-small-v1.png'],'selected','upper100 headwidth164 vs walk158; pending final visual'),
('idle-W/head-too-narrow-v1.png','a7b74405-0656-4e49-9bd0-3a93f9eb3269','idle-W/prompt.txt',['idle-W/original-upscaled-reference.png'],'intermediate','head too narrow'),
('idle-W/head-intermediate-v2.png','f23d55a9-776f-469d-a13a-f53e5fedd496','idle-W/head-recover-prompt.txt',['idle-W/head-too-narrow-v1.png'],'intermediate','still slightly too narrow'),
('idle-W/generated-raw.png','b7645f27-6cec-460b-bb53-fde213b95bc1','idle-W/final-width-prompt.txt',['idle-W/head-intermediate-v2.png'],'selected','upper100 headwidth167 vs walk164')]
runs=[]
for raw,ident,prompt,refs,status,note in data:
 original=G/f'exec-{ident}.png';assert sha(original)==sha(R/raw)
 runs.append({'tool':'builtin image_gen.imagegen','original_output':file(original),'local_copy':file(R/raw),'prompt':file(R/prompt),'references':[file(R/p) for p in refs],'reference_delivery':'displayed original or JPEG preview through conversation, num_last_images_to_include; no CLI generation','status':status,'review_note':note})
selected=[]
for d in ['E','S','SE','SW','W']:
 for phase,row in [(4,0),(8,1)]:
  raw=R/d/('phase08-native-cell.png' if d=='S' and phase==8 else 'generated-two-cell-raw.png');im=Image.open(raw).convert('RGBA');box=[0,0,im.width,im.height] if d=='S' and phase==8 else [0,round(row*im.height/2),im.width,round((row+1)*im.height/2)]
  native=im.crop(box);nativefile=R/d/f'phase{phase:02d}-native-cell.png';final=R/d/f'phase{phase:02d}-final-cell.png';assert native.tobytes()==Image.open(nativefile).convert('RGBA').tobytes();expected=native.resize((443,443),Image.Resampling.LANCZOS);assert expected.tobytes()==Image.open(final).convert('RGBA').tobytes()
  selected.append({'kind':'walk','direction':d,'phase':phase,'raw':file(raw),'native_cell_box':box,'native_cell':file(nativefile),'final_equal_cell':file(final),'postprocessing':'native square cell crop, then entire square uniformly resampled to443x443 with LANCZOS; no silhouette fit','visual_status':'author checked, pending root approval'})
for d in ['NE','NW','W']:
 raw=R/f'idle-{d}/generated-raw.png';final=R/f'idle-{d}/final-cell.png';im=Image.open(raw).convert('RGBA');assert im.resize((443,443),Image.Resampling.LANCZOS).tobytes()==Image.open(final).convert('RGBA').tobytes()
 selected.append({'kind':'idle','direction':d,'raw':file(raw),'native_cell_box':[0,0,*im.size],'native_cell':file(raw),'final_equal_cell':file(final),'postprocessing':'entire square uniformly resampled to443x443 with LANCZOS; no silhouette fit','visual_status':'author checked, pending root approval'})
report={'character_id':'25_lion_drum_guard','status':'pending_visual','published':False,'art_source':'built-in image_gen only','generator_call_count':len(runs),'selected_cell_count':13,'common_final_scale':1.024390243902439,'per_frame_subject_fitting':False,'mirroring':False,'repeated_frame_synthesis':False,'runs':runs,'selected_cells':selected}
(R/'generation-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved and verified',len(runs),'native output chains;',len(selected),'final cells are exact full-cell resamples')
