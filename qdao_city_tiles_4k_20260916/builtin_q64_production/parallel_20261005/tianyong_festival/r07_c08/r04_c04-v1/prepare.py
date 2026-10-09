from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image
D=Path(__file__).parent;N=D.parent;T=N.parent;ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
cpfile=T/'source-checkpoint.json';cp=read(cpfile);tiles={v['tile']:v for v in cp['candidateSet']};selected={k:tiles[k] for k in ('r07_c09','r08_c08','r08_c09')}
im={}
for k,v in selected.items():
 assert sha(v['file'])==v['sha256'];im[k]=Image.open(v['file']).convert('RGBA');assert im[k].size==(4096,4096)
origin=[28672,24576];local=[2957,2957,4211,4211];world=[origin[i%2]+local[i] for i in range(4)];assert world==[31629,27533,32883,28787]
C=Image.new('RGBA',(1254,1254));known=[]
for tile,box,xy in [('r07_c09',[0,2957,115,4096],[1139,0]),('r08_c08',[2957,0,4096,115],[0,1139]),('r08_c09',[0,0,115,115],[1139,1139])]:
 part=im[tile].crop(box);assert np.all(np.array(part)[:,:,3]==255);C.paste(part,xy);known.append({'source':selected[tile],'sourceLTRB':box,'contextXY':xy})
C.save(D/'context.png');A=np.array(C);assert np.all(A[:,1139:,3]==255) and np.all(A[1139:,:,3]==255) and not A[:1139,:1139,3].any()
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
G=Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world));G.save(D/'layout-reference-only.png');G=G.convert('RGBA');G.alpha_composite(C);G.convert('RGB').save(D/'coarse-layout-with-native-anchors-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png'
prompt='''Edit image1 in place at this exact map crop and scale. Repaint the blurry upper-left1139x1139 area with fresh sharp native game artwork. The RIGHT115 columns and BOTTOM115 rows are sharp authentic finished native map anchors, separately visible in image2. Preserve their contour endpoints, stone bevel widths, colors, relief shapes and lighting exactly. The blurry area is same-world canonical broad layout only; where it differs from sharp anchors, the actual native endpoints take priority. Continue all courses smoothly into the known anchors, with no physical seam at x1139 or y1139. Paint truly clear native details, never leave enlarged blurry source pixels.
This is a close overhead fragment of pale ivory architectural paving: two large muted warm-slate inset panels across the upper area separated by a thin gently curved ivory rail; a broad curved ivory horizontal course across the middle; broad warm ivory stone surfaces below; and another ivory rail above the partly cropped cloud-relief panels entering from the bottom. A pale upright divides panels at the left, and another already visible upright runs along the right anchor. Keep the same broad curves, sparse real slab divisions, relief position and scale as the guide, joining the native anchor shapes precisely. Do not straighten curved courses or introduce extra parallel stripes, doubled contours or invented joints.
Image3 is approved painting STYLE only: bright clean rounded Chinese Daoist Q fantasy handpainted game art, full soft ivory stone forms, muted warm-gray inset stone, warm beige recesses, smooth clear bevel highlights and quiet gentle painted shading. Preserve the actual bottom cloud relief; no new symbols or ornament. No dense veins, mottling, cracks, dirt, speckles, grain, realistic texture, people, props, buildings, text, UI, borders or watermark. Same exact camera, scale and composition; no zoom, crop, rotation or reframing. Return one opaque square image.'''
(D/'prompt.txt').write_text(prompt,encoding='utf-8');refs=[D/'coarse-layout-with-native-anchors-reference-only.png',D/'context.png',style];payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
save(D/'actual-payload.json',payload)
save(D/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c08','patch':'r04_c04-v1','tileGlobalOrigin':origin,'tileLocalCropLTRB':local,'globalCropLTRB':world,'configSnapshot':read(ROOT/'config/image-generation.json'),'payload':payload,'knownPixels':int((A[:,:,3]==255).sum()),'missingPixels':int((A[:,:,3]==0).sum()),'submittedParameters':{'model':None,'quality':None,'size':None}})
(D/'source-checkpoint-input.json').write_bytes(cpfile.read_bytes())
prep={'sources':selected,'knownRegions':known,'knownStartX':1139,'knownStartY':1139,'references':[dict(ref(p),role=role) for p,role in zip(refs,['edit target: approximate guide in unknown plus exact native anchors; guide forbidden in final','exact native right and bottom anchors','approved primary painting style'])],'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'expectedCoupledDestinations':['r07_c08','r07_c09','r08_c08','r08_c09']}
save(D/'preparation.json',prep)
for name,op,inputs in [('context.png','exact native crop placement',known),('layout-reference-only.png','same-world canonical guide only; enlarged pixels forbidden in final',[ref(master)]),('coarse-layout-with-native-anchors-reference-only.png','input only: canonical guide plus exact native anchors',[ref(master),ref(D/'context.png')])]:save(D/(name+'.generation.json'),{'file':str(D/name),'sha256':sha(D/name),'operation':op,'derivedFrom':inputs,'newModelCalls':0,'actualModel':None,'actualQuality':None})
shutil.copy2(T/'r07_c09/r04_c03-shifted-v1/ingest.py',D/'ingest.py');shutil.copy2(T/'r07_c09/assemble-left.py',N/'assemble-left.py')
print(json.dumps({'world':world,'knownPixels':int((A[:,:,3]==255).sum()),'missingPixels':int((A[:,:,3]==0).sum()),'sourceCheckpoint':prep['sourceCheckpoint'],'request':str(D/'request.json')}))
