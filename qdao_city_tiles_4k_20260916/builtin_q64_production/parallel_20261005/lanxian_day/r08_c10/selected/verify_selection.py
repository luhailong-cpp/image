from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent;TILE=OUT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def read(rel,expected=None):
 p=TILE/rel
 if expected:assert sha(p)==expected,(rel,sha(p))
 return np.array(Image.open(p).convert('RGB'))
def main():
 raw=read('candidate/extended4326.png','f4d2059a37599919d6e09aaa25c6e9ffc458bc70738c4ff13514400b324a9de9');west=read('west-repair/v3/extended4326.png','3d76bd7f4f990ad24f943982202c0a8a9ff284372900057c73da1fc3a34fc686')
 inside=read('geometry-v4-local/core4096.png','36fda33daf0f3d2b3c9842b269f0f95a877c2cada23bd4a92ef39f63925bb9c5');final=read('combined-final-v2/extended4326.png','2d4552bb7fa01baeb6fc0ac759360a50a08b9a90f65b285536a88947356e9e6e');core=read('combined-final-v2/core4096.png','bff348371e3ba8d23fe152885919a94b550807cbccdd1a0dccd2c81abc9f807f');wc=read('west-repair/v3/core4096.png','02714e30830c5112d1a5d76e8666e57be626d6237b095f47c49aba3af50aa1e7')
 assert final.shape==(4326,4326,3) and core.shape==(4096,4096,3)
 wm=np.any(west!=raw,axis=2);im=np.zeros(wm.shape,bool);im[115:4211,115:4211]=np.any(inside!=raw[115:4211,115:4211],axis=2);assert not np.any(wm&im)
 expected=raw.copy();expected[115:4211,115:4211]=inside;expected[wm]=west[wm]
 checks={'coreExactlyCenterIntegerCrop':np.array_equal(core,final[115:4211,115:4211]),'westCoreExactlyCenterIntegerCrop':np.array_equal(wc,west[115:4211,115:4211]),'computedMergeExactlyMatchesDecodedFinal':np.array_equal(expected,final),'actualSupportsDisjoint':not np.any(wm&im),'westChangedSupportExactlyPreserved':np.array_equal(final[wm],west[wm]),'internalChangedSupportExactlyPreserved':np.array_equal(final[im],expected[im]),'outsideUnionExactlyRaw':np.array_equal(final[~(wm|im)],raw[~(wm|im)]),'coreBottom230ExactlyActiveWestV3':np.array_equal(core[-230:],wc[-230:]),'extendedBottom230ExactlyActiveWestV3':np.array_equal(final[-230:],west[-230:]),'trueWestBoundaryExactlyWestV3':np.array_equal(core[:,:1],wc[:,:1])}
 assert all(checks.values()),checks
 boards=[]
 for name,box,labels,arrays in [
 ('close-west-and-HG01',[80,1080,340,1220],['INTERNAL v4','WEST v3','COMBINED FINAL'],[inside,wc,core]),
 ('west-registration-and-taper',[48,1744,320,1912],['WEST v3','COMBINED FINAL'],[wc,core]),
 ('west-AI-junction-and-perimeter',[16,3232,288,3416],['WEST v3','COMBINED FINAL'],[wc,core]),
 ('south-active-dependency-patch',[16,3896,288,4096],['WEST v3','COMBINED FINAL'],[wc,core]),
 ('wall-column-combined',[2720,1970,3010,2130],['INTERNAL v4','COMBINED FINAL'],[inside,core])]:
  w=box[2]-box[0];h=box[3]-box[1];b=Image.new('RGB',(w,len(arrays)*(h+20)),(28,28,28));d=ImageDraw.Draw(b)
  for i,(label,a) in enumerate(zip(labels,arrays)):d.text((3,i*(h+20)+3),label,fill='white');b.paste(Image.fromarray(a).crop(box),(0,i*(h+20)+20))
  p=OUT/'qa'/(name+'.png');p.parent.mkdir(parents=True,exist_ok=True);b.save(p);r=ref(p);r.update(coreBoxLTRB=box,scale=1,resampling='none; integer crop/paste',labelsTopToBottom=labels,actuallyViewed=False);boards.append(r)
 report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':ref(TILE/'combined-final-v2/composition.json'),'checks':checks,'actualWestChangedPixels':int(wm.sum()),'actualInternalChangedPixels':int(im.sum()),'actualSupportIntersectionPixels':int((wm&im).sum()),'activeDependency':{'core':ref(TILE/'west-repair/v3/core4096.png'),'extended':ref(TILE/'west-repair/v3/extended4326.png'),'reason':'r09_c10 native reference and frontier jobs currently depend on these exact files; preserve both throughout c10 cleanup'},'bottom230CoreRawRGBSha256':hashlib.sha256(core[-230:].tobytes()).hexdigest(),'bottom230ExtendedRawRGBSha256':hashlib.sha256(final[-230:].tobytes()).hexdigest(),'boards':boards,'selectedCopyNotYetPerformed':True,'qualifiedComplete4KCandidate':False,'formalAccepted':False}
 (OUT/'selection-proof.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'checks':checks,'overlap':report['actualSupportIntersectionPixels'],'boards':len(boards),'proof':str(OUT/'selection-proof.json')}))
if __name__=='__main__':main()
