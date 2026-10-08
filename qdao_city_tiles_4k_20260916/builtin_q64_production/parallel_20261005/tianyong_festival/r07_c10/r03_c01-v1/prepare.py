from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;T=P.parent.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
origin=[36864,24576];window=[-115,1933,1139,3187];world=[origin[i%2]+window[i] for i in range(4)]
cp=read(P.parent/'local-source-checkpoint.json');source=cp['fragment'];assert sha(source['file'])==source['sha256']
current=np.array(Image.open(source['file']).convert('RGBA'))
bottomp=P.parent/'r04_c01-v1/final-v1/joined.png';bottom=np.array(Image.open(bottomp).convert('RGBA'))
assert np.array_equal(current[2957:3187,:1139],bottom[:230,115:])
C=np.zeros((1254,1254,4),dtype=np.uint8);C[1024:,:,:]=bottom[:230,:,:]
Image.fromarray(C).save(P/'context.png')
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(P/'layout-reference-only.png')
refs=[P/'context.png',P/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
prompt='''Use case: precise-object-edit / outpainting. Continue one exact native-detail crop of the original game 五行奇谈. Return one opaque 1254 by 1254 square image, same crop, scale and camera as image 1.
Image 1 is the EDIT TARGET: authentic existing pixels occupy the entire bottom 230 rows. Only the upper 1024 rows are transparent and missing. Precisely preserve every visible stone contour, bevel width, junction, color and light in the bottom strip. Continue the same ground upward into the missing area, painting sharp native detail without changing scale. The horizontal transparency boundary is not a physical edge.
Image 2 is only the identical-world canonical LAYOUT reference. Newly render its broad native stone shapes and existing partial carved details; never copy blurred enlarged pixels or interpret tiny ambiguous marks as extra decoration. The real bottom edges in image 1 take priority. Image 3 is the approved primary STYLE reference only: bright clean rounded full Daoist Q fantasy handpainting, warm ivory and slate stone, restrained warm golden shading; no UI, words, figures or frames.
Finish only the real plaza geometry present in the layout, with broad smooth architectural bands, simple paving planes and continuous carved relief. Keep all edge endpoints and tangents. No new decorative stripe or invented seam. Quiet clean smooth stone, no cracks, grunge, veins, speckles, photo textures, polygon noise or oversharpening. No buildings, figures, props, plants, text, borders or watermark. No rotation, zoom, camera shift, cropping or rescale. Highest finish available through the host.'''
(P/'prompt.txt').write_text(prompt,encoding='utf8')
req={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c10','patch':'r03_c01','tileGlobalOrigin':origin,'globalCropLTRB':world,'tileLocalCropLTRB':window,'knownPixels':int((C[:,:,3]==255).sum()),'missingPixels':int((C[:,:,3]==0).sum()),'payload':{'prompt':prompt,'referenced_image_paths':[str(x) for x in refs],'transparent_background':False},'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'size':None},'formalAccepted':False}
write(P/'request.json',req);write(P/'source-checkpoint-input.json',cp)
write(P/'preparation.json',{'references':[ref(x) for x in refs],'savedCheckpoint':ref(P/'source-checkpoint-input.json'),'sourceTile':{**source,'tile':'r07_c10','tileLocalLTRB':[0,0,4096,4096],'nativeScale':1},'northPriorFragment':source,'nativeInputs':[source,ref(bottomp)],'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'requiresPriorManifest':cp['manifest'],'consistencyProof':{'bottomLowerOverlapExact':True,'allContextPixelsNative':True},'knownRegions':[{'contextLTRB':[0,1024,1254,1254],'source':ref(bottomp),'sourceLTRB':[0,0,1254,230]}]})
for name,ss,op in [('context.png',[source,ref(bottomp)],'Exact source-native context composition'),('layout-reference-only.png',[ref(master)],'Enlarged geometry reference only; never final pixels')]:
 write(P/(name+'.generation.json'),{'output':ref(P/name),'sources':ss,'operation':op,'newModelCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False,'nativeScale':1})
print(json.dumps({'request':ref(P/'request.json'),'missingPixels':req['missingPixels']}))
