from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,argparse
from datetime import datetime,timezone
R=Path(__file__).parent
B=R.parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
p=argparse.ArgumentParser(description='Reuse the native north donor and binary hard mask on a new baseline with identical top230 pixels; refuses overwrite.');p.add_argument('--base',required=True);p.add_argument('--out',required=True);args=p.parse_args()
tracep=B/'qa/r12c07-resume2-north-hard-v1/assembly.json';trace=json.loads(tracep.read_text(encoding='utf-8'));basep=Path(args.base);outdir=Path(args.out);assert not outdir.exists(),'Use a fresh output directory'
old=np.asarray(Image.open(trace['base']['path']).convert('RGB'));base=np.asarray(Image.open(basep).convert('RGB'));assert base.shape==old.shape==(4326,4326,3)
assert np.array_equal(old[:230],base[:230]),'Top230 changed; saved path is not valid for this baseline without a new assessment'
maskp=Path(trace['mask']['path']);donorp=Path(trace['donor']['path']);assert sha(maskp)==trace['mask']['sha256'];assert sha(donorp)==trace['donor']['sha256']
mask=np.load(maskp).astype(bool);donor=np.asarray(Image.open(donorp).convert('RGB'));out=base.copy();out[:230][mask[:230]]=donor[mask[:230]]
outdir.mkdir(parents=True);cp=outdir/'context-native.png';fp=outdir/'r12_c07.north-hard-native-4096.png';Image.fromarray(out).save(cp);Image.fromarray(out[115:4211,115:4211]).save(fp)
saved=np.asarray(Image.open(cp).convert('RGB'));report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_requires_reuse_scope_review','formalAccepted':False,'parentTrace':rec(tracep),'base':rec(basep),'mask':rec(maskp),'donor':rec(donorp),'context':rec(cp),'candidate':rec(fp),'proof':{'baseTop230DifferentPixelsFromR18':0,'fullContextReplayDifferentPixels':int(np.any(saved!=out,axis=2).sum()),'changedPixelsOutsideAllowedBand':int(np.any(saved[230:]!=base[230:],axis=2).sum()),'noResize':True,'noBlend':True,'noAI':True}}
(outdir/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
