from pathlib import Path
from PIL import Image, ImageDraw, ImageStat
import json, hashlib, sys
from datetime import datetime,timezone

request=Path(sys.argv[1]); bands=json.loads(sys.argv[2]);r=json.loads(request.read_text(encoding='utf-8-sig'))
assert r['tile'] in ('r13_c08','r14_c08','r15_c08','r16_c08') and r['coordinates']['column'] in (3,4)
row,col=r['coordinates']['row'],r['coordinates']['column']
src=Path(r['references'][0]['file'])
if '.quiet-geometry-guide' in src.stem:
 src=Path(json.loads(Path(str(src)+'.derivation.json').read_text(encoding='utf-8-sig'))['source'])
suffix=sys.argv[3] if len(sys.argv)>3 else ''
out=src.with_name(src.stem+'.quiet-geometry-guide'+suffix+'.png')
assert not out.exists()
im=Image.open(src).convert('RGB'); original=im.copy();d=ImageDraw.Draw(im)
pale=(226,222,215);grey=(168,179,187);dark=(110,104,96);light=(242,234,221)
vertical=[75,173]
if col==3 and any(n['targetBox']==[0,0,1254,230] for n in r.get('neighborSources',[])):
 xs=[]
 for x in range(25,220):
  rgb=ImageStat.Stat(original.crop((x,70,x+1,170))).mean
  if rgb[2]-rgb[0]>12:xs.append(x)
 if xs and 70<=min(xs)<=95 and 155<=max(xs)<=195:vertical=[min(xs),max(xs)]
if col==4 and bands and any(n['targetBox']==[0,0,230,1254] for n in r.get('neighborSources',[])):
 ys=[]
 for y in range(max(230,bands[0][0]-50),min(1254,bands[0][1]+50)):
  rgb=ImageStat.Stat(original.crop((70,y,170,y+1))).mean
  if rgb[2]-rgb[0]>12:ys.append(y)
 if ys and max(ys)-min(ys)>45:bands=[[min(ys),max(ys)+1]]
d.rectangle((0,0,1253,1253),fill=pale)
if col==3:
 lft,rgt=vertical
 d.rectangle((lft-9,0,lft-1,1253),fill=dark);d.rectangle((lft,0,rgt,1253),fill=grey);d.rectangle((rgt+1,0,rgt+7,1253),fill=light)
for top,bottom in bands:
 assert 0<=top<bottom<=1254
 d.rectangle((0,top,1253,bottom-1),fill=grey)
 d.rectangle((vertical[1]+8 if col==3 else 0,top-3,1253,top-1),fill=dark)
 d.rectangle((vertical[1]+8 if col==3 else 0,bottom,1253,min(1253,bottom+3)),fill=light)
for neighbor in r.get('neighborSources',[]):
 box=neighbor['effectiveTargetBox']
 if neighbor['targetBox']==[0,0,230,1254]: im.paste(original.crop(box),(box[0],box[1]))
for neighbor in r.get('neighborSources',[]):
 box=neighbor['effectiveTargetBox']
 if neighbor['targetBox']==[0,0,1254,230]: im.paste(original.crop(box),(box[0],box[1]))
im.save(out)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
der={'file':str(out),'sha256':sha(out),'source':str(src),'sourceSha256':sha(src),
 'operation':'Mechanical geometry GUIDE ONLY; flat colour fields must be fully repainted by built-in image generation. Exact native neighbor strips retained without resampling, upper owns corner.',
 'horizontalBands':bands,'verticalInlay': vertical if col==3 else None,
 'gameArt':False,'sourceResampling':False,'neighborSources':r.get('neighborSources',[])}
dp=Path(str(out)+'.derivation.json');dp.write_text(json.dumps(der,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r['references'][0]={'file':str(out),'sha256':sha(out),'role':'edit target: close mechanical geometry guide with exact native neighbor strips; must receive new native AI repaint'}
quiet=Path(__file__).resolve().parent.parent/'r12_c08/pipeline/guides/quiet-native-stone-20261016-v01.png'
if len(r['references'])==4:r['references'].append({'file':str(quiet),'sha256':sha(quiet),'role':'quiet native limestone material only; never copy its framing'})
r['referenced_image_paths']=[x['file'] for x in r['references']]
r['mechanicalGuideEvidence']={'file':str(dp),'sha256':sha(dp)}
vertical=f'Continuous vertical grey inlay face at x{vertical[0]}..{vertical[1]}, same width all the way from top to bottom, exactly matching upper native strip.' if col==3 else 'No vertical grey inlay appears anywhere in this crop.'
horizontal=f'Continuous horizontal grey inlay face at these exact y extents: {bands}.' if bands else 'No horizontal grey inlay anywhere in this crop.'
prompt=f'''Use case: precise-object-edit. EDIT IMAGE1 ONLY into genuinely new native handpainted game-map detail. Output one opaque1254x1254PNG, exact close crop, no zoom/reframe. Target {r['tile']} {r['coordinates']['id']}, art-world context {r['coordinates']['contextWorldBox']}. Image1 is a mechanical geometry GUIDE with exact sharp native neighbor strips, not final artwork. Render only this quiet close stone surface. {vertical} {horizontal} Grey inlays are continuous flat bands with shallow rounded edge bevels. Pale stone is broad continuous matte pale-grey limestone, use quiet broad brush washes like image5. DO NOT add separate paving tiles, any grout/seam segment across inlays, rectangular/diamond grids, extra horizontal/vertical divider, new line at x230/y230, cracks, dense marble veins, emblems, decoration or objects. Preserve exact native upper/left strips and extend their crossing geometry into interior; upper owns shared corner. Image2 approved whole-city geometry only, do not render a city/building. Image3 finished daylight natural grey stone and Daoist handpainting only, do not copy its tile joints. Image4 Daoist chibi handpainted style only; no UI/text/person/night. Image5 quiet material only, no dense fine veins/cells/noise. Crisp soft bevels, restrained handpainted finish; no blur, no new object, no text, no watermark.'''
prompt+=' IMPORTANT MATERIAL: Almost completely smooth matte interior stone faces, only a few very faint broad translucent brush washes. Tiny texture lines and dense rough scales must be absent. Painted detail belongs along the existing shallow edge bevels; do not cover broad faces with small marks. No embossed plaster or marble appearance.'
pf=Path(r['promptFile']);pf.write_text(prompt,encoding='utf-8')
r.update(prompt=prompt,promptSha256=sha(pf),preparedAtUtc=datetime.now(timezone.utc).isoformat())
request.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(request),'guide':str(out),'bands':bands},ensure_ascii=False))
