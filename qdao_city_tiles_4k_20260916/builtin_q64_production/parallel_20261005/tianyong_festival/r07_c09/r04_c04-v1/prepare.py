from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).parent;T=D.parents[1];ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def load(v):assert sha(v['file'])==v['sha256'];return Image.open(v['file']).convert('RGBA')
cpfile=T/'source-checkpoint.json';cp=read(cpfile);tiles={v['tile']:v for v in cp['candidateSet']}
selected={k:tiles[k] for k in ('r07_c10','r08_c09','r08_c10')};im={k:load(v) for k,v in selected.items()}
assert im['r07_c10'].size==(4096,4096)
origin=[32768,24576];local=[2957,2957,4211,4211];world=[origin[i%2]+local[i] for i in range(4)]
assert world==[35725,27533,36979,28787]
C=Image.new('RGBA',(1254,1254));known=[]
def paste(tile,box,xy):
 C.paste(im[tile].crop(box),xy);known.append({'source':selected[tile],'sourceLTRB':box,'contextXY':xy})
paste('r07_c10',[0,2957,115,4096],[1139,0]);paste('r08_c09',[2957,0,4096,115],[0,1139]);paste('r08_c10',[0,0,115,115],[1139,1139])
# Reuse real native west halo only where its inner115 pixels exactly match the current root tile.
halo3=T/'r07_c10/r03_c01-v1/final-v3/joined.png';halo4=T/'r07_c10/r04_c01-v1/final-v1/joined.png'
h3=Image.open(halo3).convert('RGBA');h4=Image.open(halo4).convert('RGBA')
assert h3.crop((115,1024,230,1200)).tobytes()==im['r07_c10'].crop((0,2957,115,3133)).tobytes()
assert h4.crop((115,176,230,1139)).tobytes()==im['r07_c10'].crop((0,3133,115,4096)).tobytes()
C.paste(h3.crop((0,1024,115,1200)),(1024,0));C.paste(h4.crop((0,176,115,1139)),(1024,176))
for p,b,xy in [(halo3,[0,1024,115,1200],[1024,0]),(halo4,[0,176,115,1139],[1024,176])]:known.append({'source':ref(p),'sourceLTRB':b,'contextXY':xy,'role':'real native unpublished west halo; inner115 matches latest right tile exactly'})
C.save(D/'context.png');A=np.array(C)
assert np.all(A[:,1139:,3]==255) and np.all(A[1139:,:,3]==255)
assert not A[:1139,:1024,3].any()
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as m:m.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(D/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png'
prompt='''Use case: precise-object-edit / outpainting. Continue one exact native-detail crop of the original game 五行奇谈. Return one opaque1254 by1254 square image, same crop, scale, camera and lighting as image1.
Image1 is the EDIT TARGET: authentic finished map pixels occupy the rightmost230 columns for the upper1139 rows, and the bottom115 rows across the entire image. All transparent pixels in the upper-left1024 by1139 area are missing map to paint. Precisely preserve the visible stone bevel widths, contour positions, tangents, materials, colors and light. Paint new sharp native structure into the missing upper-left area; transparent boundaries are not physical edges. Keep the entire existing right230 and bottom115 context aligned, and do not draw a straight seam at x1024 or y1139.
Image2 is only the same-world canonical LAYOUT reference. Use it for broad arrangement and shape of the paving. Never copy its blurred enlarged pixels, and never convert ambiguous marks into new symbols. Existing visible edge positions in image1 take priority. Image3 is the approved primary STYLE reference only: bright clean rounded full Daoist Q fantasy handpainting, warm ivory stone, muted slate insets, restrained warm gold shading. No imported UI, words, figures or frames.
The crop is a close overhead view of the plaza paving, not a new whole scene. Continue only the exact existing architectural courses and panel relief shown in the layout, preserving broad smooth stone profiles and real stone joints. No invented seam, duplicate bevel, decorative stripe or extra object. Stone planes stay quiet and smooth, with clear gentle painted volume; no cracks, grime, dense veins, speckles, photo texture, polygon noise or oversharpening. No buildings, people, props, plants, text, borders or watermark. No camera shift, rotation, zoom, cropping or rescale. Highest finish available through the host.'''
(D/'prompt.txt').write_text(prompt,encoding='utf-8');refs=[D/'context.png',D/'layout-reference-only.png',style]
save(D/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c09','patch':'r04_c04','tileGlobalOrigin':origin,'tileLocalCropLTRB':local,'globalCropLTRB':world,'configSnapshot':read(ROOT/'config/image-generation.json'),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'knownPixels':int((A[:,:,3]==255).sum()),'missingPixels':int((A[:,:,3]==0).sum()),'submittedParameters':{'model':None,'quality':None,'size':None}})
(D/'source-checkpoint-input.json').write_bytes(cpfile.read_bytes())
prep={'sources':selected,'knownRegions':known,'references':[dict(ref(p),role=role) for p,role in zip(refs,['edit target exact native right and bottom context','same-world canonical layout only','approved primary painting style'])],'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'haloConsistencyProof':{'inner115MatchesCurrentRightTile':True,'rightHaloPriority':'r03 current return until y3133; r04 remaining below'},'expectedCoupledDestinations':['r07_c09','r07_c10','r08_c09','r08_c10']}
save(D/'preparation.json',prep)
for name,op,inputs in [('context.png','exact native crop placement and authenticated native halo composition',known),('layout-reference-only.png','guide only; enlarged canonical pixels forbidden in final',[ref(master)])]:save(D/(name+'.generation.json'),{'file':str(D/name),'sha256':sha(D/name),'operation':op,'derivedFrom':inputs,'newModelCalls':0,'actualModel':None,'actualQuality':None})
save(D/'model-capability.json',{'checkedDate':'2026-10-08','officialRelease':'https://openai.com/index/introducing-chatgpt-images-2-5/','officialModel':'https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','projectBatchTarget':read(ROOT/'config/image-generation.json'),'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'sizeSelectorAvailable':False,'actualModel':None,'actualQuality':None,'note':'Official pages re-opened for this continuation; target is not evidence of actual backend. Same batch target retained.'})
print(json.dumps({'world':world,'knownPixels':int((A[:,:,3]==255).sum()),'missingPixels':int((A[:,:,3]==0).sum()),'rootVersion':cp['version'],'request':str(D/'request.json')}))
