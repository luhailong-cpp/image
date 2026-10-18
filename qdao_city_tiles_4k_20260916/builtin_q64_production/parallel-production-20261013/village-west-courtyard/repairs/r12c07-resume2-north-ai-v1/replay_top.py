from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,argparse
from datetime import datetime,timezone
R=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def checked(entry):
 p=Path(entry['path']);assert sha(p)==entry['sha256'],f'Hash mismatch: {p}';return p
def reconstruct(base,plan):
 out=base.copy()
 for layer in plan['layers']:
  mask=np.load(checked(layer['mask'])).astype(bool);native=np.asarray(Image.open(checked(layer['source'])).convert('RGB'));ys,xs=np.nonzero(mask);px,py=layer['sourceOriginInContext'];assert not len(ys) or (ys.min()>=0 and ys.max()<900);assert xs.min()>=px and xs.max()<px+native.shape[1];assert ys.min()>=py and ys.max()<py+native.shape[0];out[ys,xs]=native[ys-py,xs-px]
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--base-assembly');p.add_argument('--out',required=True);a=p.parse_args();planp=R/'top-replay-plan-v1.json';plan=json.loads(planp.read_text(encoding='utf-8'));orig=np.asarray(Image.open(checked(plan['baselineR18'])).convert('RGB'));bp=Path(a.base);base=np.asarray(Image.open(bp).convert('RGB'));assert base.shape==orig.shape==(4326,4326,3);assert np.array_equal(base[:900],orig[:900]),'New baseline top900 differs from R18; require a new overlap assessment before reuse'
 outdir=Path(a.out);assert not outdir.exists(),'Use a fresh output directory';out=reconstruct(base,plan);outdir.mkdir(parents=True);cp=outdir/'context-native.png';fp=outdir/'r12_c07.north-ai-native-4096.png';Image.fromarray(out).save(cp);Image.fromarray(out[115:4211,115:4211]).save(fp);saved=np.asarray(Image.open(cp).convert('RGB'))
 report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'north_top_replayed_requires_integrated_QA','formalAccepted':False,'base':rec(bp),'baseAssembly':rec(Path(a.base_assembly)) if a.base_assembly else (rec(bp.parent/'assembly.json') if (bp.parent/'assembly.json').exists() else None),'plan':rec(planp),'layers':plan['layers'],'context':rec(cp),'candidate':rec(fp),'proof':{'top900InputDifferentPixelsFromR18':0,'hierarchicalFullContextReplayDifferentPixels':int(np.any(saved!=out,axis=2).sum()),'changesBelowY900':int(np.any(saved[900:]!=base[900:],axis=2).sum()),'noResize':True,'noBlend':True,'noBlur':True},'pending':plan['pending'],'qaReuse':'Reuse prior north QA only after confirming its actual crop pixels are identical. Subsequent H1-east repair must inspect its overlap with the north top output.'};(outdir/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'context':report['context'],'candidate':report['candidate'],'assembly':rec(outdir/'assembly.json'),'proof':report['proof']},ensure_ascii=False))
