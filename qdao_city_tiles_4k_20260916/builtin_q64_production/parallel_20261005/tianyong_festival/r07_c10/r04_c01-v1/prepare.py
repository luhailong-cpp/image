from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;T=P.parent.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
origin=[36864,24576];window=[-115,2957,1139,4211];world=[origin[i%2]+window[i] for i in range(4)]
cp=read(T/'source-checkpoint.json');source=cp['fragment'];assert sha(source['file'])==source['sha256']
current=np.array(Image.open(source['file']).convert('RGBA'))
leftsource=cp['coupledNeighbors']['r08_c09'];assert sha(leftsource['file'])==leftsource['sha256']
left=np.array(Image.open(leftsource['file']).convert('RGBA'))
c1p=T/'r08_c10/r01_c01-v1/final-v1/joined.png';rightp=P.parent/'r04_c02-v1/final-v1/joined.png'
c1=np.array(Image.open(c1p).convert('RGBA'));right=np.array(Image.open(rightp).convert('RGBA'))
assert np.array_equal(current[:115,:909],c1[115:230,115:1024])
assert np.array_equal(left[:115,3981:],c1[115:230,:115])
previous=[]
for patch in ['r04_c04-v1','r04_c03-v1','r04_c02-v1']:
 mp=P.parent/patch/'final-v1/manifest.json';m=read(mp);previous.append(ref(mp))
 for ent in m['patches']:
  if ent['destinationTile']=='r08_c10':
   l,t,r,b=ent['destinationTileLTRB'];current[t:b,l:r]=np.array(Image.open(ent['asset']['file']).convert('RGBA'))
Image.fromarray(current).save(P/'bottom-coupled-input.png')
bottom={**ref(P/'bottom-coupled-input.png'),'tile':'r08_c10','tileLocalLTRB':[0,0,4096,4096],'nativeScale':1}
C=np.zeros((1254,1254,4),dtype=np.uint8)
C[1024:1139,:1024]=c1[:115,:1024]
C[1139:,:115]=left[:115,3981:]
C[1139:,115:1024]=current[:115,:909]
C[:,1024:]=right[:,:230]
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
req={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c10','patch':'r04_c01','tileGlobalOrigin':origin,'globalCropLTRB':world,'tileLocalCropLTRB':window,'knownPixels':int((C[:,:,3]==255).sum()),'missingPixels':int((C[:,:,3]==0).sum()),'payload':{'prompt':prompt,'referenced_image_paths':[str(x) for x in refs],'transparent_background':False},'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'size':None},'formalAccepted':False}
write(P/'request.json',req);write(P/'source-checkpoint-input.json',cp)
write(P/'preparation.json',{'references':[ref(x) for x in refs],'savedCheckpoint':ref(P/'source-checkpoint-input.json'),'sourceTile':bottom,'bottomLeftTile':leftsource,'northPriorFragment':ref(P.parent/'r04_c02-v1/final-v1/r07_c10-fragment.png'),'nativeInputs':[source,leftsource,ref(c1p),ref(rightp)],'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'requiresPriorManifest':previous[-1],'pendingManifestChain':previous,'consistencyProof':{'c01RootLowerOverlapExact':True,'leftC09RootLowerOverlapExact':True,'allContextPixelsNative':True},'knownRegions':[{'contextLTRB':[0,1024,1024,1139],'source':ref(c1p),'sourceLTRB':[0,0,1024,115]},{'contextLTRB':[0,1139,115,1254],'source':leftsource,'sourceLTRB':[3981,0,4096,115]},{'contextLTRB':[115,1139,1024,1254],'source':bottom,'sourceLTRB':[0,0,909,115]},{'contextLTRB':[1024,0,1254,1254],'source':ref(rightp),'sourceLTRB':[0,0,230,1254]}]})
for name,ss,op in [('context.png',[source,leftsource,ref(c1p),ref(rightp)],'Exact source-native context composition'),('layout-reference-only.png',[ref(master)],'Enlarged geometry reference only; never final pixels'),('bottom-coupled-input.png',[source]+previous,'Read-only prior representation with pending previous manifest bottom returns')]:
 write(P/(name+'.generation.json'),{'output':ref(P/name),'sources':ss,'operation':op,'newModelCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False,'nativeScale':1})
print(json.dumps({'request':ref(P/'request.json'),'missingPixels':req['missingPixels']}))
