from pathlib import Path
import json,hashlib
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def info(f):
 p=B/f['source']; g=read(Path(str(p)+'.generation.json')); im=Image.open(p); im.load()
 h=sha(p); bbox=im.getchannel('A').point(lambda x:255 if x>8 else 0).getbbox()
 return dict(action=f['action'],direction=f['direction'],frame=int(f['frame']),source=f['source'],sha256=h,sidecarMatches=h==g['sha256'],selectionMatches=h==(f.get('sourceSha256') or f.get('sha256')),nativeSize=list(im.size),mode=im.mode,visibleBBoxAlphaGt8=bbox,actualModel=g.get('actualModel'),actualQuality=g.get('actualQuality'),generationRecord=f['source']+'.generation.json')
snap=[]
for name in ['hit-selection.json','hit-W-selection.json','attack-selection.json','cast-selection.json']:
 for f in read(B/name)['frames']:
  x=info(f); a=x['action']; d=x['direction']; n=x['frame']
  if a=='hit':
   x.update(footDecision='retain',note='联系表逐帧检查，两只鞋尖均随角色朝向；受击双手持物、双靴及屈膝可辨。动态未验收。')
  elif a=='attack':
   if d=='E' and n in [1,2,3,12]: s='targeted_repair'; note='屏幕左后靴朝镜头明显，前靴朝东，形成外撇；仅局部旋转鞋掌与踝部。'
   elif d=='W' and n<=9: s='targeted_repair'; note='屏幕右后靴比朝西的前靴更朝镜头；01至08尤其明显，09减轻但未完全同向。'
   else: s='review_with_neighbors'; note='相邻帧存在后脚斜向承重或回收，需要结合局部脚向及连续性决定，不由SHA不同判定动作通过。'
   x.update(footDecision=s,note=note,repairOwner='parent; this audit records original attack-selection sources')
  elif a=='cast':
   x.update(footDecision='retain' if n in [1,12,16] else 'repaired_locally',note='01/12/16仍朝东，轻微透视保留。' if n in [1,12,16] else '原后靴较前靴外转；已局部转向东，见cast-foot-selection.json。')
  snap.append(x)
cast=[]
for sel in ['cast-foot-selection.json','cast-W-selection.json']:
 for f in read(B/sel)['frames']:
  x=info(f); x['footDecision']='repaired' if '-foot-' in x['source'] else 'retain'; x['note']=f['reviewNote']; x['staticViewed']=True; x['dynamicAcceptance']=False; cast.append(x)
assert len(cast)==32 and len({x['sha256'] for x in cast})==32
assert all(x['sidecarMatches'] and x['selectionMatches'] and x['mode']=='RGBA' and min(x['nativeSize'])>=1024 for x in cast)
audit=dict(schema=1,character='20_star_formation_master_girl',reviewedAt=datetime.now(ZoneInfo('America/New_York')).isoformat(),method='view_image actual existing contact sheets plus original PNGs; cast E and W every selected original was viewed individually; repaired outputs viewed as returned and first repairs re-opened from disk',scope='Original hit/attack/cast E selection review, actual cast W inventory, plus cast targeted edits',dynamicAcceptance=False,realTimePlaybackVerified=False,clientIntegration='not_integrated',contactSheetsViewed=['preview/hit-review-E-contact.png','preview/hit-review-W-contact.png','preview/attack-review-E-contact.png','preview/attack-review-W-contact.png','preview/cast-E-contact.png'],originalSelectionSnapshot=snap,currentCastSelection=cast,castRepairSummary={'eastFootRepaired':[2,3,4,5,6,7,8,9,10,11,13,14,15],'eastRetained':[1,12,16],'westFootRetained':list(range(1,17)),'westCardsRepaired':[6],'westSourceChoice':{'10':'10-v2.png; 10-v1 hair approached right edge'},'preserved':'Original action phases, upper-body acting, identity, hands/props and planted stance locations; no mirroring/copying/interpolation or global lowest-pixel alignment.'},sourceEvidence={'configuredModel':'gpt-image-2.5-sunburst','configuredQuality':'max','route':'builtin','submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'reason':'Tool exposes no model/quality selectors and no returned model/quality metadata. Every new image has prompt, input refs with SHA, result receipt, native dimensions and source chain.'},checks={'castSlots':32,'uniqueCastHashes':32,'selectedNativeHashesMatch':True,'castNativeRGBAge1024':True,'uniqueHashIsNotVisualAcceptance':True},remaining=['cast E04 wide stance and E11 to12/12 to13 foot placement changes require actual normal-size playback.','cast W10 to11 star-disc height changes markedly; 11 to13 rise/fall may need reordering or a transition after actual playback.','Fixed source canvas 1254 and export transform922 at51,40 preserve scale; virtual ground/root not client validated.','Parent must merge choices, export and refresh previews; this subtask does not change global STATUS/selection/preview.'])
(B/'provenance/combat-foot-review-20261003.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(audit['checks'],ensure_ascii=False))
