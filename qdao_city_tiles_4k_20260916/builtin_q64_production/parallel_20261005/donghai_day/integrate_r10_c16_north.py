from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
import assembly_r10_c16 as a
import integrate_c15_repairs as m
R=Path(__file__).resolve().parent;T=a.TILE;B=T/'repairs/internal-final-v2';D=T/'repairs/north-integrated';P=T/'repairs/north-joint'
EXPECTED='8f922a70ffaf382e80a273c688205c7a8c038548863335fa950600f1aa0d581d'
def main():
 assert a.sha(B/'candidate.png')==EXPECTED
 m.a=a;m.sha=a.sha;m.load=a.load_json;m.js=a.save_json;m.save=a.save_image;m.M=D/'masks';m.joint.MASKS=m.M;m.joint.native=a;m.joint.save_image=a.save_image;m.joint.save_json=a.save_json;m.SEAMS=[];m.INSERTIONS=[];m.GLOBAL_MASK=np.zeros((4096,4096),np.uint8);m.FN=a.load_seam_function()
 base=m.rgb(B/'candidate.png');im=base.copy();north,ni=a.checked_north();n_ext=m.rgb(R/'r09_c16/output/extended-context.png');sources=[]
 for name in ['n2','n3']:
  f=P/name;patch,e=m.valid_patch(f/'edited-native.png');meta=a.load_json(f/'input.png.generation.json');x=meta['sourceRectXYXY'][0];p=patch[627:].copy();truth=n_ext[4211:4326,x+115:x+1369]
  assert np.array_equal(truth,m.rgb(f/'composition-reference.png')[627:742])
  mixed,_=m.seam(truth[50:115],p[50:115],'horizontal',[x,50,x+1254,115],name+'-true-halo')
  p[:50]=truth[:50];p[50:115]=mixed
  m.insert(im,p,[x,0,x+1254,627],96,name,rects=[[x,0,x+1254,627]])
  sources.append(e)
 assert np.array_equal(im[627:],base[627:])
 ext=m.rgb(B/'extended-context.png');assert np.array_equal(ext[115:4211,115:4211],base);ext[115:4211,115:4211]=im
 c=a.save_image(D/'candidate.png',Image.fromarray(im));e=a.save_image(D/'extended-context.png',Image.fromarray(ext));mask=a.save_image(D/'masks/union.png',Image.fromarray(m.GLOBAL_MASK));a.ART=D/'candidate.png';a.QA=D/'qa/assembly';qa=a.write_qa(Image.fromarray(im),Image.fromarray(ext),north)
 extra=[]
 for name,x in [('n2',768),('n3',1792)]:
  probe=Image.new('RGB',(1254,1027));probe.paste(north.crop((x,3696,x+1254,4096)),(0,0));probe.paste(Image.fromarray(im).crop((x,0,x+1254,627)),(0,400));extra.append(a.save_image(D/'qa'/(name+'-full-joint.png'),probe))
 for i,x in enumerate([0,1024,2048,2842],1):extra.append(a.save_image(D/'qa'/('insertion-bottom-'+str(i)+'.png'),Image.fromarray(im).crop((x,420,x+1254,755))))
 changed=[];same=[]
 for q in qa:
  old=B/'qa/assembly'/Path(q['file']).name
  if old.exists() and a.sha(old)==q['sha256']:same.append(Path(q['file']).name)
  else:changed.append(Path(q['file']).name)
 info={'createdAtUtc':a.utc_now(),'tile':'r10_c16','candidate':c,'extendedContext':e,'status':'pending-local-review','base':{'file':str(B/'candidate.png'),'sha256':EXPECTED},'nativeRepairs':sources,'insertions':m.INSERTIONS,'seams':m.SEAMS,'mask':mask,'belowY627Unchanged':True,'neighbor09Unchanged':True,'nativeResampling':False,'geometryWarp':False,'maximumBlendPixels':2,'qa':qa,'extraQA':extra,'unchangedSheets':same,'changedSheets':changed,'formalAccepted':False}
 a.save_json(D/'manifest.json',info);print(json.dumps({'candidate':c,'changedSheets':changed,'unchangedSheets':same}))
if __name__=='__main__':main()
