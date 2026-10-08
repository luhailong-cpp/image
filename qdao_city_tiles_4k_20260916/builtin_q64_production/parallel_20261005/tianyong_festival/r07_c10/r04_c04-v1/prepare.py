"""Prepare the next tile using only verified native bottom context and true halos."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;T=P.parent.parent
ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tile='r07_c10';row,col=7,10;size=4096;origin=[(col-1)*size,(row-1)*size]
window=[2957,2957,4211,4211];world=[origin[i%2]+window[i] for i in range(4)]
assert origin==[36864,24576] and world==[39821,27533,41075,28787]
assert (16*4096)==65536 and all(0<=x<=65536 for x in world)
cp=read(T/'r08_c10/current/v014/source-checkpoint.json');source=cp['fragment'];assert sha(source['file'])==source['sha256']
current=np.array(Image.open(source['file']).convert('RGBA'))
c4path=T/'r08_c10/r01_c04-v1/joined.png';c3path=T/'r08_c10/r01_c03-v1/registration-v1/joined.png'
c4=np.array(Image.open(c4path).convert('RGBA'));c3=np.array(Image.open(c3path).convert('RGBA'))
assert c3.shape==c4.shape==(1254,1254,4)
assert np.array_equal(current[:115,2957:3187],c3[115:230,1024:1254])
assert np.array_equal(current[:115,3187:4096],c4[115:230,230:1139])
canvas=np.zeros((1254,1254,4),dtype=np.uint8)
canvas[1024:1139,:230]=c3[:115,1024:1254]
canvas[1024:1139,230:1139]=c4[:115,230:1139]
canvas[1139:1254,:1139]=current[:115,2957:4096]
assert not canvas[:1024,:,3].any() and not canvas[:,1139:,3].any()
assert np.all(canvas[1024:,:1139,3]==255)
Image.fromarray(canvas,'RGBA').save(P/'context.png')
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(P/'layout-reference-only.png')
refs=[P/'context.png',P/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
prompt='''Use case: precise-object-edit / outpainting. Continue one exact native-detail crop of the original game 五行奇谈. Return one opaque1254 by1254 square image, same crop, scale and camera as image1.
Image1 is the EDIT TARGET: authentic finished map pixels occupy the lower230 rows in the left1139 columns, with transparent missing area above and in the rightmost115 columns. Precisely preserve these existing contours, all stone bevel widths, positions, tangents, carving shape, color and light. Continue them into the missing area, painting new sharp native structure without changing the image scale. The transparent boundaries are not physical edges.
Image2 is only the identical-world canonical LAYOUT reference: it determines broad stone and relief forms entering from the missing upper area. Never copy its blurred enlarged pixels or tiny ambiguous marks. Existing visible edge positions in image1 take priority. Image3 is the approved primary STYLE reference only: bright clean rounded full Daoist Q fantasy handpainting, warm ivory stone, slate inset and restrained warm gold shading; no imported UI, words, figures or frames.
Finish only the real plaza geometry present in the layout, preserving broad smooth architectural bands and continuous carved relief. No extra decorative stripe or invented stone seam. Stone planes should stay quiet, smooth and clean: no cracks, grunge, veins, speckles, photo texture, polygon noise or oversharpening. No buildings, figures, props, plants, text, borders or watermark. No rotation, zoom, camera shift, cropping or rescale. The right115 columns are also missing map, not an existing neighboring image. Fill them by continuing the same geometry, and do not draw a boundary at x1139. Highest finish available through the host.'''
(P/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(x) for x in refs],'transparent_background':False}
write(P/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':tile,'patch':'r04_c04','tileGlobalOrigin':origin,'globalCropLTRB':world,'tileLocalCropLTRB':window,'knownPixels':int((canvas[:,:,3]==255).sum()),'missingPixels':int((canvas[:,:,3]==0).sum()),'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json'),'referenceRoles':['edit target: exact same-world native bottom context','same-world canonical layout only','approved primary rendering style only'],'submittedParameters':{'model':None,'quality':None,'size':None},'formalAccepted':False})
write(P/'source-checkpoint-input.json',cp)
prep={'references':[ref(x) for x in refs],'savedCheckpoint':ref(P/'source-checkpoint-input.json'),'sourceTile':source,'nativeInputs':[source,{**ref(c3path),'role':'Latest matched upper halo for x2957..3187; overrides obsolete c04 corresponding halo'},{**ref(c4path),'role':'Upper halo for x3187..4096 only'}],'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'knownRegions':[{'contextLTRB':[0,1024,230,1139],'source':ref(c3path),'sourceLTRB':[1024,0,1254,115],'formalNeighborAccepted':False},{'contextLTRB':[230,1024,1139,1139],'source':ref(c4path),'sourceLTRB':[230,0,1139,115],'formalNeighborAccepted':False},{'contextLTRB':[0,1139,1139,1254],'source':source,'sourceLTRB':[2957,0,4096,115],'formalNeighborAccepted':False}],'consistencyProof':{'c03Bottom115MatchesLatestCurrentTop115':True,'c04Remaining909ColumnsMatchLatestCurrentTop115':True,'oldC04HaloNotReusedInChangedC03Return':True},'unknownRegions':[{'contextLTRB':[0,0,1254,1024],'owner':'r07_c10 and unknown r07_c11 halo'},{'contextLTRB':[1139,1024,1254,1254],'owner':'Unknown r07_c11 / r08_c11; no oldpixels fabricated'}],'expectedCommitScope':{'newActiveTileLTRB':[2957,2957,4096,4096],'returnBottomTile':'r08_c10','returnBottomTileLTRB':[2957,0,4096,115],'unknownRightHaloNeverCommittedWithoutOwner':True}}
write(P/'preparation.json',prep)
for f,inputs,op in [('context.png',prep['nativeInputs'],'Exact native same-world crop ownership; unknown right column remains transparent'),('layout-reference-only.png',[ref(master)],'Canonical layout reference only; enlarged pixels prohibited in output')]:write(P/(f+'.generation.json'),{'file':str(P/f),'sha256':sha(P/f),'derivedFrom':inputs,'operation':op,'newModelCalls':0,'nativeScale':1,'actualModel':None,'actualQuality':None})
print(json.dumps({'origin':origin,'windowGlobal':world,'knownPixels':int((canvas[:,:,3]==255).sum()),'request':ref(P/'request.json')}))
