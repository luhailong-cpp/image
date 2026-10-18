from pathlib import Path
from PIL import Image,ImageDraw,ImageStat
import json,sys,hashlib

p=Path(sys.argv[1]);r=json.loads(p.read_text(encoding='utf-8-sig'))
assert r['tile']=='r11_c08' and r['coordinates']['column']==2 and r['coordinates']['row'] in (3,4)
src=Path(r['references'][0]['file']);out=src.with_name(src.stem+'.quiet-field-guide.png');assert not out.exists()
im=Image.open(src).convert('RGB');upper=im.crop((0,0,1254,230))
mean=lambda box:tuple(round(v) for v in ImageStat.Stat(upper.crop(box)).mean)
pale=mean((950,50,1100,180));grey=mean((300,50,650,180))
d=ImageDraw.Draw(im);d.rectangle((0,230,1253,1253),fill=pale);d.rectangle((208,230,806,1253),fill=grey)
strip=upper.crop((45,100,57,101))
for y in range(230,1254):im.paste(strip,(45,y))
im.paste(upper,(0,0));im.save(out)
sha=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
der=Path(str(out)+'.derivation.json');der.write_text(json.dumps({'file':str(out),'sha256':sha(out),'source':str(src),'sourceSha256':sha(src),'operation':'Mechanical geometry GUIDE only. Actual native upper230 preserved without resampling. Extend same flat blue-grey ground field x208..806 and existing pale joint x50. All flat fields must receive new built-in native AI repaint.','gameArt':False,'resampling':False,'neighborSources':r['neighborSources']},indent=2)+'\n',encoding='utf-8')
r['references'][0]={'file':str(out),'sha256':sha(out),'role':'edit target: mechanical exact close field guide with native upper230, must receive native AI repaint'};r['referenced_image_paths'][0]=str(out);r['mechanicalGuideEvidence']={'file':str(der),'sha256':sha(der)}
prompt='''Use case: precise-object-edit. EDIT IMAGE1 ONLY into new native painted map detail. One opaque1254x1254PNG. Exactly this extremely close flat horizontal ground fragment, not architecture or vertical wall. Preserve native TOP230exactly. Extend the same existing continuous wide blue-grey inlaid ground field x208..806 all the way to bottom, keep its two edges perfectly vertical with identical width; shallow narrow rounded bevels only. Pale-grey natural limestone ground remains either side. The existing shallow pale joint entering from TOP at x50 must continue straight to bottom matching its native width, and must not stop at y230. No horizontal or diagonal joint anywhere in new interior. No new rectangles, grid, slab segments, extra divider at y230/x230, crack, emblem, object or building. Image1flat colors are mechanical guidance only, repaint with genuine native handpainting. Interior stone faces almost completely smooth and matte: only a few faint broad translucent washes like image5, absolutely no tiny texture lines, dense veins, microgrid, scales or embossed plaster. Handpainted detail at existing shallow edge bevels only. Image2 approved city geometry only, no whole city output. Image3 daylight clean stone and finished soft handpainting only, do not copy its grout. Image4 Daoist chibi style only, no UI/text/person/night. Image5 quiet stone material only. Do not zoom/reframe. Output cropped empty stone only, no watermark.'''
pf=Path(r['promptFile']);pf.write_text(prompt,encoding='utf-8');r['prompt']=prompt;r['promptSha256']=sha(pf);p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out)
