from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;T=P.parent.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
origin=[36864,24576];window=[1933,2957,3187,4211];world=[origin[i%2]+window[i] for i in range(4)]
cp=read(T/'source-checkpoint.json');source=cp['fragment'];assert sha(source['file'])==source['sha256']
current=np.array(Image.open(source['file']).convert('RGBA'))
c2p=T/'r08_c10/r01_c02-v1/registration-v1/joined.png';c3p=T/'r08_c10/r01_c03-v1/registration-v1/joined.png';rightp=T/'r07_c10/r04_c04-v1/final-v1/joined.png'
c2=np.array(Image.open(c2p).convert('RGBA'));c3=np.array(Image.open(c3p).convert('RGBA'));right=np.array(Image.open(rightp).convert('RGBA'))
assert np.array_equal(current[:115,1933:2013],c2[115:230,1024:1104])
assert np.array_equal(current[:115,2013:2957],c3[115:230,80:1024])
current[:61,2957:4096]=right[1139:1200,:1139]
Image.fromarray(current).save(P/'bottom-coupled-input.png')
bottom={**ref(P/'bottom-coupled-input.png'),'tile':'r08_c10','tileLocalLTRB':[0,0,4096,4096],'nativeScale':1}
C=np.zeros((1254,1254,4),dtype=np.uint8)
C[1024:1139,:80]=c2[:115,1024:1104]
C[1024:1139,80:1024]=c3[:115,80:1024]
C[1139:1254,:1024]=current[:115,1933:2957]
C[:,1024:]=right[:,:230]
assert np.all(C[1024:,:,3]==255) and np.all(C[:,1024:,3]==255)
Image.fromarray(C).save(P/'context.png')
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(P/'layout-reference-only.png')
refs=[P/'context.png',P/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
prompt='''Use case: precise-object-edit / outpainting. Continue one exact native-detail crop of the original game 五行奇谈. Return one opaque 1254 by 1254 square image, same crop, scale and camera as image 1.
Image 1 is the EDIT TARGET: authentic existing pixels occupy the entire right 230 columns and bottom 230 rows. Only the top-left 1024 by 1024 area is transparent and missing. Precisely preserve all visible stone contours, bevel widths, junctions, color and light. Continue them into the missing area, painting sharp native detail without changing scale. The transparency boundaries are not physical edges.
Image 2 is only the identical-world canonical LAYOUT reference. Newly render its broad native stone shapes and existing partial carved details; never copy blurred enlarged pixels or interpret tiny ambiguous marks as extra decoration. Existing right and lower edges in image 1 take priority. Image 3 is the approved primary STYLE reference only: bright clean rounded full Daoist Q fantasy handpainting, warm ivory and slate stone, restrained warm golden shading; no UI, words, figures or frames.
Finish only the real plaza geometry present in the layout, with broad smooth architectural bands, simple paving planes and continuous carved relief. Keep all edge endpoints and tangents. No new decorative stripe or invented seam. Quiet clean smooth stone, no cracks, grunge, veins, speckles, photo textures, polygon noise or oversharpening. No buildings, figures, props, plants, text, borders or watermark. No rotation, zoom, camera shift, cropping or rescale. Highest finish available through the host.'''
(P/'prompt.txt').write_text(prompt,encoding='utf8')
req={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c10','patch':'r04_c03','tileGlobalOrigin':origin,'globalCropLTRB':world,'tileLocalCropLTRB':window,'knownPixels':int((C[:,:,3]==255).sum()),'missingPixels':int((C[:,:,3]==0).sum()),'payload':{'prompt':prompt,'referenced_image_paths':[str(x) for x in refs],'transparent_background':False},'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'size':None},'formalAccepted':False}
write(P/'request.json',req);write(P/'source-checkpoint-input.json',cp)
write(P/'preparation.json',{'references':[ref(x) for x in refs],'savedCheckpoint':ref(P/'source-checkpoint-input.json'),'sourceTile':bottom,'northPriorFragment':ref(T/'r07_c10/r04_c04-v1/final-v1/r07_c10-fragment.png'),'nativeInputs':[source,ref(c2p),ref(c3p),ref(rightp)],'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'requiresPriorManifest':ref(T/'r07_c10/r04_c04-v1/final-v1/manifest.json'),'consistencyProof':{'c02Latest80UpperHalo':True,'c03Remaining944UpperHalo':True,'bottomCoupled61RowsOverlay':True,'allContextPixelsNative':True},'knownRegions':[{'contextLTRB':[0,1024,80,1139],'source':ref(c2p),'sourceLTRB':[1024,0,1104,115]},{'contextLTRB':[80,1024,1024,1139],'source':ref(c3p),'sourceLTRB':[80,0,1024,115]},{'contextLTRB':[0,1139,1024,1254],'source':bottom,'sourceLTRB':[1933,0,2957,115]},{'contextLTRB':[1024,0,1254,1254],'source':ref(rightp),'sourceLTRB':[0,0,230,1254]}]})
for name,sourceobj,op in [('context.png',[source,ref(c2p),ref(c3p),ref(rightp)],'Exact source-native context composition'),('layout-reference-only.png',[ref(master)],'Enlarged geometry reference only; never final pixels'),('bottom-coupled-input.png',[source,ref(rightp)],'Read-only prior representation with pending previous manifest bottom return')]:
 write(P/(name+'.generation.json'),{'output':ref(P/name),'sources':sourceobj,'operation':op,'newModelCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False,'nativeScale':1})
print(json.dumps({'request':ref(P/'request.json'),'missingPixels':req['missingPixels']}))
