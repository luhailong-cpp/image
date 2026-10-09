"""Integrate disjoint, actually reviewed builtin local repairs on immutable approved-sync."""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, argparse
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
BASE=T/'repairs/approved-sync/output/r08_c15.png'
EXT=T/'repairs/approved-sync/output/extended-context.png'
MAN=T/'repairs/approved-sync/output/integration-manifest.json'
D=T/'repairs/approved-sync-final'
SHA='908df2ad815315cac373cf0ace48c0f2493e45b981b729ee28741cae5da82fa9'
ESHA='03f287ebf7ea279a5c48f894d5c0d01af55dcaea4f536a00d1ff6dad9dd0bf96'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def verify(e):
 p=Path(e['file']);assert p.is_file() and sha(p)==e['sha256'],str(p)
 return p
def write(p,d):
 p=Path(p);assert p.resolve().is_relative_to(T.resolve());p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def save(p,a,meta):
 p=Path(p);assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);im=Image.fromarray(a);im.save(p)
 assert np.array_equal(np.asarray(Image.open(p)),a)
 e={**ref(p),'pixels':list(im.size)};write(str(p)+'.generation.json',{**e,**meta,'generatedByAI':False,'actualModel':None,'actualQuality':None,'artResampled':False,'formalAccepted':False});return e
def run(config,build=False):
 assert sha(BASE)==SHA and sha(EXT)==ESHA
 cfg=read(config);assert cfg['baseSha256']==SHA
 base=rgb(BASE);ext=rgb(EXT);assert np.array_equal(ext[115:4211,115:4211],base)
 union=np.zeros((4096,4096),np.uint8);out=base.copy();entries=[]
 for spec in cfg['repairs']:
  p=Path(spec['completion']);c=read(p);verify(c['base']);assert c['base']['sha256']==SHA
  w=c['windowXYXY'];x,y,x1,y1=w;assert x1-x==y1-y==1254 and min(w)>=0 and max(w)<=4096
  native=rgb(verify(c['native']));mi=Image.open(verify(c['mask']));assert mi.mode=='L';mask=np.asarray(mi);assert mask.shape==(1254,1254)
  assert native.shape==(1254,1254,3)
  old=base[y:y1,x:x1];v=((old.astype(np.uint32)*(255-mask[:,:,None])+native.astype(np.uint32)*mask[:,:,None]+127)//255).astype(np.uint8)
  actual=rgb(verify(c['patchedWindow']));assert np.array_equal(v,actual),'patched window is not exact recorded mask blend'
  assert not np.any((union[y:y1,x:x1]>0)&(mask>0)),'Overlapping local repairs require explicit reconciliation'
  dst=out[y:y1,x:x1];dst[mask>0]=v[mask>0];np.maximum(union[y:y1,x:x1],mask,out=union[y:y1,x:x1])
  review=Path(spec['review']);rd=read(review)
  assert spec['actualLocalQaConfirmed'] is True,'Local QA not confirmed'
  entries.append({'id':spec['id'],'completion':ref(p),'review':ref(review),'windowXYXY':w,'roisXYXY':c.get('roisXYXY'),'native':c['native'],'mask':c['mask'],'patchedWindow':c['patchedWindow'],'noNonzeroMaskOverlap':True})
 assert np.array_equal(out[union==0],base[union==0])
 assert np.array_equal(out[:,:128],base[:,:128]),'West128 protection escaped'
 extout=ext.copy();extout[115:4211,115:4211]=out
 assert np.array_equal(extout[:115],ext[:115]) and np.array_equal(extout[4211:],ext[4211:])
 assert np.array_equal(extout[:,:115],ext[:,:115]) and np.array_equal(extout[:,4211:],ext[:,4211:])
 summary={'base':ref(BASE),'extendedBase':ref(EXT),'configuration':ref(config),'localRepairCount':len(entries),'repairs':entries,'outsideMaskUnionExactlyPreserved':True,'west128ExactlyPreserved':True,'allTrueHalosExactlyPreserved':True,'changedPixels':int(np.any(out!=base,axis=2).sum()),'maximumNativeEditChannelDifferenceFromBase':int(np.abs(out.astype(np.int16)-base.astype(np.int16)).max()),'differenceMeaning':'Local built-in painted edits bounded by exact masks; this is not the earlier +/-24 assembly RGB field. No additional computed RGB field is applied.','geometryWarped':False,'artBlurred':False,'DAYWritten':False,'formalAccepted':False,'remainingOutsideScope':cfg.get('remainingOutsideScope',[])}
 if not build:return summary
 assert not D.exists(),'Immutable final directory already exists'
 common={**summary,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'Disjoint local builtin edit native pixels, exact integer alpha blend with per-patch 40px or 48px returns, no global image processing','baseManifest':ref(MAN),'script':ref(__file__)}
 candidate=save(D/'output/r08_c15.png',out,common);extended=save(D/'output/extended-context.png',extout,common);mi=save(D/'masks/local-union.png',union,{'operation':'maximum disjoint local alpha masks','notArtwork':True})
 original=read(MAN);qa=[]
 for prior in cfg['priorReviews']: verify(prior)
 for q in original['qa']:
  verify(q);x,y,x1,y1=q['rectInExtendedXYXY'];pix=extout[y:y1,x:x1];prior=rgb(q['file']);same=np.array_equal(pix,prior)
  p=D/'qa'/Path(q['file']).name
  e=save(p,pix,{'derivedFrom':[candidate,extended],'rectInExtendedXYXY':q['rectInExtendedXYXY'],'actualTileAndHaloRectXYXY':q['actualTileAndHaloRectXYXY'],'pixelScale':1,'resized':False,'previousActualQa':{'file':q['file'],'sha256':q['sha256']},'pixelIdenticalToPriorActualQa':same,'visualReview':'inherit prior actual view by exact pixel identity' if same else 'changed by localized reviewed patches; final affected-window review pending'})
  qa.append({**e,'name':p.stem,'pixelIdenticalToPriorActualQa':same,'previousQa':{'file':q['file'],'sha256':q['sha256']},'rectInExtendedXYXY':q['rectInExtendedXYXY']})
 manifest={**common,'candidate':candidate,'extendedContext':extended,'union':mi,'qa':qa,'qaCount':len(qa),'unchangedQaCount':sum(q['pixelIdenticalToPriorActualQa'] for q in qa),'changedQaCount':sum(not q['pixelIdenticalToPriorActualQa'] for q in qa),'priorReviews':cfg['priorReviews'],'visualReview':'local patches passed; changed assembled QA pending; western shared edge pending'}
 write(D/'output/integration-manifest.json',manifest)
 return {'candidate':candidate,'extendedContext':extended,'manifest':ref(D/'output/integration-manifest.json'),'changedQa':[q['name'] for q in qa if not q['pixelIdenticalToPriorActualQa']],'unchangedQaCount':manifest['unchangedQaCount']}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('config');a.add_argument('--build',action='store_true');args=a.parse_args();print(json.dumps(run(args.config,args.build),ensure_ascii=False,indent=2))
