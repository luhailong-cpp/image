from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Z=T.parent;R=T/'repairs/local-seams-20261016-v1';R.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
P=read(T/'progress.json');C=Path(P['candidate']);im=Image.open(C).convert('RGB');W=Path(read(Z/'r16_c14/progress.json')['candidate']);west=Image.open(W).convert('RGB')
refs=read(T/'records/p04_04_v20261014T035144_86a707ac.request.json')['referenced_image_paths'][:3]
I=R/'I01-target.png';im.crop((1010,1460,2264,2714)).save(I)
WT=R/'W01-target.png';wi=Image.new('RGB',(1254,1254));wi.paste(west.crop((3904,0,4096,1254)),(0,0));wi.paste(im.crop((0,0,1062,1254)),(192,0));wi.save(WT)
prompts={
'I01':'Change only the false short vertical grout stub near x630,y515..710 in image4. It rises from a true horizontal seam at y710 into the middle of a single broad stone slab, ending blindly around y515. ERASE that entire short vertical grout, bevel, bright rim and dark narrow shadow; restore continuous quiet pale limestone slab with the adjacent texture. Keep the horizontal course boundary at y710 and the TRUE lower row vertical joint around x650 from y720 downwards intact. Do not extend the false stub upwards, do not add any replacement joint. Preserve exact framing, all true mortar, stone silhouettes, tones, scale and all pixels outside the tiny repair. Output exactly1254x1254.',
'W01':'Repair the left edge registration of an existing limestone wall-panel only. Image4 is a native seam pair: x0..192 is LOCKED actual west neighbor; x192..1254 is this tile. Fix only x192..815,y18..350. The inner shallow upper panel moulding around y35..85 and its lower bevel around y300..330 currently show an abrupt step at x192. Continue the LOCKED left native profiles cleanly across x192 with exact height and width, and reconnect them smoothly to the existing right pillar at approximately x820. Maintain the same broad inset panel; no extra vertical border or blind-end groove at x192, no new stone rows, no ledge kink. Keep the broad lower cornice from y350..460, all pixels y460..1254, the right pillar x820..1254, x0..192 and the very top y0..15 exactly unchanged. Same hand-painted limestone tone, detail and lighting. Keep native framing; output exactly1254x1254.'}
jobs=[]
for key,target,box in [('I01',I,[1010,1460,2264,2714]),('W01',WT,[-192,0,1062,1254])]:
 prompt='Use case: precise-object-edit. Native detailed Taoist chibi daylight city-wall repair. Inputs1/2/3 are approved map/material/illustration references only. Image4 LAST is the sole actual-pixel edit target. No UI, text, characters, new props, architecture or decoration. No resizing, no whole-scene reconstruction. '+prompts[key]
 request={'prompt':prompt,'referenced_image_paths':refs+[str(target)],'transparent_background':False}
 rp=R/(key+'.request.json');rp.write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf-8')
 jobs.append({'id':key,'request':str(rp),'target':str(target),'targetSha256':sha(target),'cropBox':box,'sourceCandidate':str(C),'sourceCandidateSha256':sha(C),'westNeighbor':{'path':str(W),'sha256':sha(W)},'actualModel':None,'status':'prepared_not_generated'})
(R/'preparations.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(jobs))
