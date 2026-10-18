from workflow import ROOT,read,write,sha,now,patch
from PIL import Image
from pathlib import Path
import sys,shutil
pid,v,srcarg=sys.argv[1:4];src=Path(srcarg);out=ROOT/'native'/f'{pid}_{v}.png'
assert not out.exists()
qf=ROOT/'prompts'/f'{pid}_{v}.request.json';q=read(qf);pf=Path(q['promptPath'])
assert sha(pf)==q['promptSha256']
for ref in q['references']:assert sha(Path(ref['file']))==ref['sha256']
shutil.copy2(src,out)
with Image.open(out) as im:im.load();size=list(im.size);mode=im.mode
receipt=ROOT/'receipts'/f'{pid}_{v}.json'
write(receipt,{'patchId':pid,'version':v,'receivedAt':now(),'tool':'image_gen.imagegen','route':'builtin','status':'success','request':str(qf),'requestSha256':sha(qf),'promptPath':str(pf),'promptSha256':sha(pf),'references':q['references'],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'nativePixels':size,'mode':mode,'returnedFields':['image_url','output_hint'],'actualModel':None,'actualQuality':None,'largeImageDataLogged':False})
assert size==[1254,1254] and mode=='RGB',(size,mode)
rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':size[0],'height':size[1],'format':'PNG','mode':mode,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'prompt':str(pf),'promptSha256':sha(pf),'references':q['references'],'coordinate':patch(pid),'evidence':{'toolReceipt':str(receipt),'returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'resizedAfterGeneration':False,'status':'native_saved_pending_actual_seam_review'}
write(Path(str(out)+'.generation.json'),rec)
p=read(ROOT/'progress-left-oct16.json');p.update(updatedAt=now(),lastNative=str(out),lastNativeSha256=sha(out),lastReceipt=str(receipt),status='native_received_pending_review');p.setdefault('received',[]).append({'patch':pid,'version':v,'sha256':sha(out)});p['inFlightRequests']=[x for x in p.get('inFlightRequests',[]) if x['patch']!=pid];write(ROOT/'progress-left-oct16.json',p)
print({'file':str(out),'sha256':sha(out),'size':size,'receipt':str(receipt)})
