"""Exact coordinate native edits; no modified reference pixels enter final artwork."""
from workflow import ROOT,read,write,sha,now,patch
from pathlib import Path
from PIL import Image
import sys,shutil
action,key=sys.argv[1:3]
specs={
 '22south':([909,1421,2163,2675],'horizontal',627,'Remove the artificial straight horizontal discontinuity through leaves and tan-gray stone at local y=627. Reconcile the two sides into uninterrupted natural foliage and matching stone facets. Preserve the current broad rock geometry and all existing leaf clusters. No new objects.'),
 '33west':([1421,1933,2675,3187],'vertical',627,'Remove the artificial straight vertical break at local x=627 through the central rock surface and leaves. Continue natural stone facets, edge shadows and foliage seamlessly across this line. Preserve the existing broad rock geometry and overall color. No new objects.'),
 '33south':([1933,2445,3187,3699],'horizontal',627,'Remove the artificial horizontal break at local y=627 through the rounded stone facets. Continue the same rock naturally across this line with coherent facet edges and small cracks. Preserve the broad geometry, shadows and surrounding plants. No new objects.')}
box,axis,line,description=specs[key];pid='r13_c10_cross_'+key;v='v01'
qf=ROOT/'prompts'/f'{pid}_{v}.request.json';pf=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';guide=ROOT/'guides'/f'{pid}.exact-candidate-{v}.png';out=ROOT/'native'/f'{pid}_{v}.png'
if action=='prepare':
 assert not any(f.exists() for f in [qf,pf,guide,out])
 candidate=ROOT/'tiles/r13_c10.candidate-left-oct16-v01.png';a=Image.open(candidate);assert a.size==(4096,4096);a.crop(box).save(guide)
 write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'source':str(candidate),'sourceSha256':sha(candidate),'sourceCrop':box,'operation':'exact unscaled crop; reference only','usableAsFinalArt':False})
 refs=[{'file':str(guide),'sha256':sha(guide),'role':'exact 1254 square native candidate crop; edit target'}]+read(ROOT/'references.json')
 prompt=f'''Use case: precise-object-edit.
Edit image 1 only, a native 1254 x 1254 square game-map crop. Keep the exact framing, object scale, world position, lighting, and every valid existing contour. {description}
The visible straight line is a stitching error, never a physical ledge or new object. Redraw only a narrow natural corridor within 180 pixels of that line so material and contours flow continuously across it. Preserve the rest of image 1, especially its outer 115 pixels. Do not add a frame, rectangular patch, blur, new ledge, gradient or different texture scale. The correction must have detailed native brushwork and the same daylight Daoist Q-painted illustration quality. Images 2 to 4 provide full-map layout, material and approved style context only.
Output a single opaque RGB square exactly 1254 x 1254. No text, UI, watermark or border.
'''
 pf.write_text(prompt,encoding='utf-8');write(qf,{'promptPath':str(pf),'promptSha256':sha(pf),'references':refs,'transparent_background':False,'preparedAt':now(),'tile':'r13_c10','tileRelativeOrigin':box[:2],'sourceCrop':[115,115,1139,1139],'destinationBox':[box[0]+115,box[1]+115,box[0]+1139,box[1]+1139],'actualModel':None,'status':'prepared_not_submitted'})
 print(str(qf))
elif action=='receive':
 src=Path(sys.argv[3]);assert src.exists() and not out.exists();q=read(qf);assert sha(pf)==q['promptSha256']
 for ref in q['references']:assert sha(Path(ref['file']))==ref['sha256']
 shutil.copy2(src,out)
 with Image.open(out) as a:a.load();size=list(a.size);mode=a.mode
 receipt=ROOT/'receipts'/f'{pid}_{v}.json';write(receipt,{'patchId':pid,'version':v,'receivedAt':now(),'route':'builtin','tool':'image_gen.imagegen','request':str(qf),'requestSha256':sha(qf),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'actualModel':None,'nativePixels':size,'mode':mode,'status':'success'})
 assert size==[1254,1254] and mode=='RGB'
 origin=patch('r13_c10_p11')['coreGlobalBox'][:2];g=[origin[0]+box[0],origin[1]+box[1],origin[0]+box[2],origin[1]+box[3]]
 write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'tile':'r13_c10','tileRelativeOrigin':box[:2],'globalBox':g,'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'prompt':str(pf),'promptSha256':sha(pf),'references':q['references'],'evidence':{'toolReceipt':str(receipt)},'resizedAfterGeneration':False,'status':'native_saved_pending_review'})
 manifest=ROOT/f'overlay-left-oct16-r13_c10-{key}-v01.json';write(manifest,{'tile':'r13_c10','createdAt':now(),'overlays':[{'file':str(out),'sha256':sha(out),'sourceCrop':q['sourceCrop'],'destinationBox':q['destinationBox']}],'status':'not_adopted_pending_review'})
 print({'file':str(out),'sha256':sha(out),'manifest':str(manifest)})
