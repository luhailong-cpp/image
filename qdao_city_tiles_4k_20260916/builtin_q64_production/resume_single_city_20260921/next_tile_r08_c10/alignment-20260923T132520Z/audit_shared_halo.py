"""Read-only source geometry audit; derived images are review only, not art."""
from pathlib import Path
from datetime import datetime,timezone
from io import BytesIO
import json,hashlib
from PIL import Image

D=Path(__file__).resolve().parent
P=D.parent;S=P.parent;A=S.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):return {'file':str(p),'sha256':sha(p.read_bytes())}
def write(p,o):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
def readimage(p,expected=None):
 raw=p.read_bytes()
 if expected:assert sha(raw)==expected,str(p)
 im=Image.open(BytesIO(raw));im.load();return im.convert('RGB'),{'file':str(p),'sha256':sha(raw),'pixels':list(im.size)}
def image(im,p,src,operation):
 with p.open('xb') as f:im.save(f,format='PNG')
 write(p.with_suffix('.derived.json'),{'output':rec(p),'pixels':list(im.size),'sources':src,'operation':operation,'role':'geometry_audit_only_never_imagegen_input_or_artwork','toolCalled':False})
 return rec(p)
assert not (D/'audit.json').exists(),'Do not overwrite an existing audit'
ledgerpath=S/'current-coverage-ledger.json';ledgerraw=ledgerpath.read_bytes();ledger=json.loads(ledgerraw.decode('utf-8-sig'))
bottomrow=next(t for t in ledger['tiles'] if t['tile']=='r09_c10')['candidate']
assert bottomrow['sha256']=='f5a45f15f69104c6f3dfe9f7a855e71f5d142d896cc78ffadbf12b3a57f813e4'
bp=Path(bottomrow['file']);bp=bp if bp.is_absolute() else A/bp
bottom,bottomrec=readimage(bp,bottomrow['sha256'])
master,mrec=readimage(P/'guides/r04_c02.master-layout-only.png','c71145d9a4f6cddf5e722d2dab4e41762d1071ec58f6eaf1cf70913ffcf989dd')
plaza,prec=readimage(P/'guides/r04_c02.plaza-layout-review-only.png','fdf241fd3e18f322f204c363ec4634861825cc59aead7306c99de2174dc7ac0c')
assert master.size==plaza.size==(1254,1254)
plan=json.loads((P/'plan.json').read_text(encoding='utf-8-sig'));patch=next(p for p in plan['patches'] if p['id']=='r04_c02')
g=[37773,31629,39027,32883];assert patch['globalNativeContextLTRB']==g
boundary_global_y=32768;boundary_target_y=boundary_global_y-g[1]
assert boundary_target_y==1139 and 1254-boundary_target_y==115
halo_global=[g[0],32768,g[2],g[3]]
bottom_box=[g[0]-36864,0,g[2]-36864,115]
assert bottom_box==[909,0,2163,115]
imgs=[master.crop((0,1139,1254,1254)),plaza.crop((0,1139,1254,1254)),bottom.crop(bottom_box)]
entries=[]
for key,im,source in zip(['master','plaza','bottom'],imgs,[mrec,prec,bottomrec]):
 entries.append(image(im,D/f'{key}-same-global-halo-native-review.png',[source],f'Exact same global LTRB {halo_global}; master/plaza are existing reference resamples, bottom original native crop {bottom_box}'))
stack=Image.new('RGB',(1254,345))
for k,im in enumerate(imgs):stack.paste(im,(0,k*115))
stackrec=image(stack,D/'three-source-shared-halo-comparison.png',[mrec,prec,bottomrec],'Rows0:115 master,115:230 plaza,230:345 bottom; each is SAME global115-high area. No labels, no scaling; review only. Panel borders are not art.')
# This review-only contact view shows the first row of the true lower tile,
# never moves it upward to y1024. It is NOT a proposed generation input yet.
contact=Image.new('RGB',(1254,371))
contact.paste(master.crop((0,883,1254,1139)),(0,0))
contact.paste(imgs[2],(0,256))
contactrec=image(contact,D/'master-core-to-real-bottom-contact-review.png',[mrec,bottomrec],'Master target y883:1139 then native bottom y0:115. True boundary at review y256, global32768; no unknown-core pixels replaced. Review only, not a generation input.')
observation={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'ledgerSnapshot':{'file':str(ledgerpath),'sha256':sha(ledgerraw)},'selectedBottom':bottomrec,'plan':rec(P/'plan.json'),'masterGuide':mrec,'plazaGuide':prec,'nativePatchGlobalLTRB':g,'nativeCoreLocalLTRB':[115,115,1139,1139],'trueBottomTileBoundaryGlobalY':32768,'trueBottomTileBoundaryTargetY':1139,'knownNeighborHaloTargetLTRB':[0,1139,1254,1254],'knownNeighborSourceLTRB':bottom_box,'sharedHaloGlobalLTRB':halo_global,'masterSharedHaloSourceLTRB':[v*3/32 for v in halo_global],'plazaSharedHaloNominalSourceLTRB':[v*3/16-4096 for v in halo_global],'placingNeighborAtY1024WouldIntrudeIntoUnknownCoreByPixels':115,'coordinateArithmeticPassed':True,'comparisonImages':entries,'stackedComparison':stackrec,'contactComparison':contactrec,'generationDecision':'pending actual static visual comparison','generationToolCalls':0,'formalAccepted':False,'navigationWritten':False,'sharedJSONWritten':False}
write(D/'audit.json',observation)
print(json.dumps(observation,ensure_ascii=False,indent=2))
