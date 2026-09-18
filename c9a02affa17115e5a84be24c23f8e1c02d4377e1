"""Join four native seam repairs; never resize native art."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
TILE=ROOT.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((ROOT/'plan.json').read_text())
OUT=TILE/'output'/plan['candidateVersion']
QA=TILE/'qa'/plan['candidateVersion']
ART=OUT/(plan['city']+'_'+plan['appearance']+'_r09_c10_4k_candidate_'+plan['candidateVersion']+'.png')
spec=importlib.util.spec_from_file_location('assembler',TILE/'assemble_builtin.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sources():
 src=Path(plan['sourceContext']);assert sha(src)==plan['sourceContextSha256']
 rows=[];entries=[]
 for c in range(1,5):
  tid=f'r01_c{c:02d}';p=ROOT/'native'/f'{tid}.png';rp=ROOT/'native'/f'{tid}.record.json'
  rec=json.loads(rp.read_text());assert rec['backendModelVerified'] is False
  for key,path in [('outputSha256',p),('sourceOutputSha256',Path(rec['sourceOutputPath'])),('promptSha256',ROOT/'prompts'/f'{tid}.prompt.txt'),('guideSha256',ROOT/'guides'/f'{tid}.png'),('submittedImageSha256',ROOT/'guides'/f'{tid}.jpg')]:
   assert sha(path)==rec[key],(tid,key)
  im=Image.open(p);assert im.size==(1254,1254)
  rows.append(np.asarray(im.convert('RGB')).copy())
  entries.append({'id':tid,'nativeFile':str(p),'nativeSha256':sha(p),'recordFile':str(rp),'recordSha256':sha(rp),'sourceOutputPath':rec['sourceOutputPath']})
 return src,rows,entries
def check():
 src,_,entries=sources();a=json.loads((OUT/'assembly.json').read_text())
 assert a['nativeRepairs']==entries
 assert a['scriptSha256']==sha(__file__)
 assert a['baseContextSha256']==sha(src)
 assert a['output']['sha256']==sha(ART)
 ext=Image.open(OUT/'extended-context.png');im=Image.open(ART)
 assert ext.size==(4326,4326) and im.size==(4096,4096)
 assert np.array_equal(np.asarray(ext.crop((115,115,4211,4211))),np.asarray(im))
 b=np.asarray(Image.open(src).convert('RGB'));e=np.asarray(ext)
 assert np.array_equal(b[:2560],e[:2560]) and np.array_equal(b[3814:],e[3814:])
 return {'passed':True,'repairNativeCount':4,'outputSize':[4096,4096],'unmodifiedOutsideRepairBand':True,'noUpscaling':True}
def run():
 src,rows,entries=sources();s=m.load_seam_helper();metrics=[];strip=rows[0]
 for c,p in enumerate(rows[1:],2):
  strip,met=m.append_patch(strip,p,s,f'repair_horizontal_{c-1}_{c}');metrics.append(met)
 assert strip.shape==(1254,4326,3)
 base=np.asarray(Image.open(src).convert('RGB')).copy();old=base[2560:3814].copy()
 m.OVERLAP=96
 top,met=m.append_patch(old[:96].transpose(1,0,2),strip[:96].transpose(1,0,2),s,'top_96');metrics.append(met)
 bottom,met=m.append_patch(strip[-96:].transpose(1,0,2),old[-96:].transpose(1,0,2),s,'bottom_96');metrics.append(met)
 strip[:96]=top.transpose(1,0,2);strip[-96:]=bottom.transpose(1,0,2)
 base[2560:3814]=strip
 OUT.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
 Image.fromarray(base).save(OUT/'extended-context.png')
 im=Image.fromarray(base[115:4211,115:4211]);im.save(ART)
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(QA/'overview.jpg',quality=88)
 q=[]
 for y in [2445,2493,3072,3651,3699]:
  band=im.crop((0,y-150,4096,y+150)).transpose(Image.Transpose.ROTATE_90)
  sheet=Image.new('RGB',(1200,1024))
  for k in range(4):sheet.paste(band.crop((0,k*1024,300,(k+1)*1024)),(k*300,0))
  path=QA/f'horizontal_y{y}_100pct.jpg';sheet.save(path,quality=92);q.append({'file':str(path),'sha256':sha(path),'sampling':'1:1 rotated90 no resampling'})
 for x in [1024,2048,3072]:
  band=im.crop((x-150,0,x+150,4096));sheet=Image.new('RGB',(1200,1024))
  for k in range(4):sheet.paste(band.crop((0,k*1024,300,(k+1)*1024)),(k*300,0))
  path=QA/f'vertical_x{x}_100pct.jpg';sheet.save(path,quality=92);q.append({'file':str(path),'sha256':sha(path),'sampling':'1:1'})
 report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_visual_QA','scriptFile':str(Path(__file__)),'scriptSha256':sha(__file__),'seamHelperSha256':sha(m.HELPERS),'baseContextFile':str(src),'baseContextSha256':sha(src),'baseSourcesPreserved':True,'nativeRepairs':entries,'repairBoxInExtendedContext':[0,2560,4326,3814],'horizontalOverlap':230,'topBottomBand':96,'seamFeatherRadius':2,'integerBlend':True,'finalArtUpscaled':False,'sourceResampling':False,'colorMatching':False,'globalBlur':False,'extendedContext':{'file':str(OUT/'extended-context.png'),'sha256':sha(OUT/'extended-context.png'),'pixels':[4326,4326]},'output':{'file':str(ART),'sha256':sha(ART),'pixels':[4096,4096]},'seamMetrics':metrics,'qa':q,'externalDeliveryTileSeams':'pending_neighbor_generation_and_joint_review','runtimePublished':False}
 (OUT/'assembly.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'candidate':str(ART),**check()},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.check:print(json.dumps(check()))
 else:run()
