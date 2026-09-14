from pathlib import Path
from PIL import Image
import hashlib,json
R=Path(__file__).resolve().parent;G=Path(r'C:\Users\luyua\.codex\generated_images\01a09f27-0628-78e0-84b5-2472601dc072')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):
 p=Path(p);d={'path':str(p),'sha256':sha(p)}
 if p.suffix=='.png':
  i=Image.open(p);d.update(size=list(i.size),mode=i.mode,rgba_sha256=hashlib.sha256(i.convert('RGBA').tobytes()).hexdigest())
 return d
runspec=[
('N/head-01-05-v1.png','a089efb6-9694-4f93-bce0-94c19a8c9dca','N/head-01-05-prompt.txt','N/head-01-05-reference.png','superseded','head still smaller than stable reference'),
('N/head-01-05-raw.png','9316a1d8-8c2b-4aa6-b4ca-51f29bc6a532','N/head-01-05-refine-prompt.txt','N/head-01-05-v1.png','superseded','head now wider than reference by5-6percent'),
('N/head-01-05-narrow-anchor-v3.png','436a99c5-cef9-411e-8dcb-2c581a21bdd5','N/head-01-05-final-anchor-prompt.txt','N/head-01-05-final-anchor-reference.png','superseded','head was narrowed too far'),
('N/head-01-05-final-raw.png','1313619b-24bc-4c10-9e58-de566cca11ea','N/head-01-05-width-prompt.txt','N/head-01-05-narrow-anchor-v3.png','selected_right_column','head width matched with small widening'),
('N/head-06-08-raw.png','ad22556e-e72c-49c5-963d-e3362595ca02','N/head-06-08-prompt.txt','N/head-06-08-anchor-reference.png','selected_right_column','same-direction N02 head anchor; own legs retained'),
('N/head-07-raw.png','6cf25886-1d5f-4191-bd84-5a417614125f','N/head-07-prompt.txt','N/head-07-anchor-reference.png','selected_right_cell','N03 head anchor; original N07 crossing preserved'),
('W/head-01-02-raw.png','693406d0-8a27-4731-aa85-da971946a9ea','W/head-01-02-prompt.txt','W/head-01-02-anchor-reference.png','selected_right_column','W03 stable head reference; original contact/down poses'),
('SW/head-03-07-raw.png','3cf717ac-5b88-467e-a557-ac01576af13f','SW/head-03-07-prompt.txt','SW/head-03-07-anchor-reference.png','selected_right_column','SW01 scale reference; SW03 head/upper torso and SW07 head'),
('E/low-04-08-v1.png','01f0b0a5-45f5-4a0f-ae37-c490277a1598','E/low-04-08-prompt.txt','E/reference-low-04-08.png','superseded','heel clearance still large'),
('E/low-04-08-raw.png','b8ababa9-01dd-4170-a25a-14aca79d7fce','E/low-04-08-refine-prompt.txt','E/low-04-08-v1.png','selected_both','lower heels, opposite near/far free legs'),
('S/low-04-08-raw.png','47c6089e-6f77-43f3-8664-b1df01ee7203','S/low-04-08-prompt.txt','S/reference-low-04-08.png','selected_both','front view; LEFT then RIGHT low reaching leg'),
('SE/low-04-08-raw.png','fc6dbead-5b85-495d-8433-e1fceb858d29','SE/low-04-08-prompt.txt','SE/reference-low-04-08.png','selected_both','farLEFT then nearRIGHT; body and lantern orientation retained'),
('SW/low-04-08-raw-v1.png','27bf8745-2878-44c8-9b33-b552fa2a4c96','SW/low-04-08-prompt.txt','SW/reference-low-04-08.png','selected_top04_only','bottom08 rejected because hip occlusion too similar to04'),
('SW/low08-single-v1.png','7fac242a-aa21-430a-b7dc-dd38f38d8334','SW/low08-single-prompt.txt','SW/low08-original-upscaled.png','superseded','farRIGHT leg correct but heel still too high'),
('SW/phase08-native-cell.png','c02af1a8-c53b-4768-b3b5-75f2c6f1bbdf','SW/low08-lower-prompt.txt','SW/low08-single-v1.png','selected','farRIGHT low reaching, nearLEFT supports'),
('W/low-04-08-raw.png','2912f590-2f3a-408a-8f3f-8708ad03b324','W/low-04-08-prompt.txt','W/reference-low-04-08.png','selected_both','nearLEFT free then farRIGHT free; left lantern stays left')]
runs=[]
for raw,ident,prompt,ref,status,note in runspec:
 original=G/f'exec-{ident}.png';assert sha(original)==sha(R/raw)
 runs.append({'tool':'built-in image_gen.imagegen','original_output':rec(original),'saved_raw':rec(R/raw),'prompt':rec(R/prompt),'reference':rec(R/ref),'reference_delivery':'displayed reference through conversation, num_last_images_to_include; no CLI generation','status':status,'visual_note':note})
spec=[]
for d,phases,raw,boxes in [
('N',[1,5],'N/head-01-05-final-raw.png',[[627,0,1254,627],[627,627,1254,1254]]),
('N',[6,8],'N/head-06-08-raw.png',[[627,0,1254,627],[627,627,1254,1254]]),
('N',[7],'N/head-07-raw.png',[[887,0,1774,887]]),
('W',[1,2],'W/head-01-02-raw.png',[[627,0,1254,627],[627,627,1254,1254]]),
('SW',[3,7],'SW/head-03-07-raw.png',[[627,0,1254,627],[627,627,1254,1254]]),
('E',[4,8],'E/low-04-08-raw.png',[[0,0,887,887],[0,887,887,1774]]),
('S',[4,8],'S/low-04-08-raw.png',[[0,0,887,887],[0,887,887,1774]]),
('SE',[4,8],'SE/low-04-08-raw.png',[[0,0,887,887],[0,887,887,1774]]),
('SW',[4],'SW/low-04-08-raw-v1.png',[[0,0,887,887]]),
('SW',[8],'SW/phase08-native-cell.png',[[0,0,1254,1254]]),
('W',[4,8],'W/low-04-08-raw.png',[[0,0,887,887],[0,887,887,1774]])]:
 for n,box in zip(phases,boxes):
  native=Image.open(R/raw).convert('RGBA').crop(box);nativefile=R/d/f'phase{n:02d}-native-cell.png';final=R/d/f'phase{n:02d}-final-cell.png';assert native.tobytes()==Image.open(nativefile).convert('RGBA').tobytes();assert native.resize((443,443),Image.Resampling.LANCZOS).tobytes()==Image.open(final).convert('RGBA').tobytes()
  spec.append({'direction':d,'phase':n,'raw_source':rec(R/raw),'native_cell_box':box,'native_cell':rec(nativefile),'final_equal_cell':rec(final),'operation':'exact square crop then entire square isotropic LANCZOS to443; no silhouette-based fitting','visual_status':'author_checked_pending_root'})
report={'character_id':'23_lantern_courier','status':'pending_visual','published':False,'generator_call_count':len(runs),'selected_cell_count':len(spec),'art_source':'built-in image_gen only','per_frame_body_fitting':False,'mirroring':False,'synthetic_motion':False,'common_final_scale':1.0194174757281553,'runs':runs,'selected_cells':spec}
(R/'generation-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Verified',len(runs),'native output chains and',len(spec),'exact native-to-final full-cell resamples')
