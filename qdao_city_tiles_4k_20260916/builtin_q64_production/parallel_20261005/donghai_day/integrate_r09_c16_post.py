"""Insert the reviewed native micro-repair only inside its bounded ROI."""
from pathlib import Path
import sys
import numpy as np
from PIL import Image
import assembly_r09_c16 as a
import integrate_c15_repairs as m
from qa_r09_c16_external import probes
R=Path(__file__).resolve().parent;T=a.TILE;D=T/'repairs/post-integrated';P=T/'repairs/post-tonal-fix'
BASE=T/'repairs/color-match-v2';EXPECTED='093589a138671f1112dc25835f7857871bccbc44bf5a9df3a835e12cf63c6f96'
MASKED='--masked' in sys.argv
if MASKED:D=T/'repairs/post-integrated-masked';P=T/'repairs/post-tonal-masked'
def main():
 assert a.sha(BASE/'candidate.png')==EXPECTED
 m.a=a;m.sha=a.sha;m.load=a.load_json;m.js=a.save_json;m.save=a.save_image
 m.M=D/'masks';m.joint.MASKS=m.M;m.joint.native=a;m.joint.save_image=a.save_image;m.joint.save_json=a.save_json
 m.SEAMS=[];m.INSERTIONS=[];m.GLOBAL_MASK=np.zeros((4096,4096),np.uint8);m.FN=a.load_seam_function()
 base=m.rgb(BASE/'candidate.png');image=base.copy()
 patch,source=m.valid_patch(P/'edited-native.png')
 meta=a.load_json(str(P/'input.png')+'.generation.json');box=meta['sourceRectXYXY']
 assert np.array_equal(m.cut(base,box),m.rgb(P/('composition-reference.png' if MASKED else 'input.png')))
 sys.argv.append('--color')
 roi=[[1938,3035,2058,3235],[2096,2980,2230,3250]] if MASKED else [[1920,2910,2250,3370]]
 m.insert(image,patch,box,30 if MASKED else 64,'lantern-post-and-banner',rects=roi)
 assert np.array_equal(image[m.GLOBAL_MASK==0],base[m.GLOBAL_MASK==0])
 ext=m.rgb(BASE/'extended-context.png');assert np.array_equal(ext[115:4211,115:4211],base)
 ext[115:4211,115:4211]=image
 c=a.save_image(D/'candidate.png',Image.fromarray(image));e=a.save_image(D/'extended-context.png',Image.fromarray(ext))
 mask=a.save_image(D/'masks/union.png',Image.fromarray(m.GLOBAL_MASK))
 a.ART=D/'candidate.png';a.QA=D/'qa'
 north,ni=a.checked_north();qa=a.write_qa(Image.fromarray(image),Image.fromarray(ext),north)
 probes(a.ART,a.QA)
 q=a.save_image(a.QA/'post-insertion-all-edges.png',Image.fromarray(image).crop((1792,2782,2378,3498)))
 unchanged=[];changed=[]
 for item in qa:
  prior=BASE/'qa'/Path(item['file']).name
  if prior.exists() and a.sha(prior)==item['sha256']:unchanged.append(Path(item['file']).name)
  else:changed.append(Path(item['file']).name)
 info={'createdAtUtc':a.utc_now(),'tile':'r09_c16','status':'candidate-pending-local-review','candidate':c,'extendedContext':e,
  'baseline':{'file':str(BASE/'candidate.png'),'sha256':EXPECTED,'manifest':str(BASE/'manifest.json'),'manifestSha256':a.sha(BASE/'manifest.json')},
  'nativeRepairs':[source],'sourceRectXYXY':box,'authorizedROI':roi,'seams':m.SEAMS,'insertions':m.INSERTIONS,'mask':mask,
  'outsideMaskUnchanged':True,'geometryWarp':False,'imageBlur':False,'resampling':False,'maximumAlphaTransitionPixels':2,
  'qa':qa,'extraQA':q,'unchangedPriorSheets':unchanged,'changedSheetsRequiringReview':changed,'formalAccepted':False}
 a.save_json(D/'manifest.json',info);a.save_json(a.QA/'manifest.json',{'candidateSha256':c['sha256'],'qa':qa,'extra':q,'visualReview':'pending'})
 print(__import__('json').dumps({'candidate':c,'changedSheets':changed,'unchangedSheets':len(unchanged),'insertionQA':q}))
if __name__=='__main__':main()
