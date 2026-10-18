from pathlib import Path
from PIL import Image,ImageStat,ImageDraw
import json,hashlib,sys
p=Path(sys.argv[1]);r=json.loads(p.read_text(encoding='utf-8-sig'))
src=Path(r['references'][0]['file']);out=src.with_name(src.stem+'.straight-inlay-guide.png')
assert not out.exists() and len(r['references'])==4
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
mean=lambda box:tuple(round(x) for x in ImageStat.Stat(im.crop(box)).mean)
pale=mean((400,100,700,220));grey=mean((90,100,150,220));dark=mean((67,100,74,220));rim=mean((175,100,186,220))
d.rectangle((0,230,1253,1253),fill=pale)
d.rectangle((66,230,74,1253),fill=dark)
d.rectangle((75,230,165,1253),fill=grey)
d.rectangle((166,230,173,1253),fill=dark)
d.rectangle((174,230,180,1253),fill=rim)
im.save(out)
sha=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
der={'file':str(out),'sha256':sha(out),'source':str(src),'sourceSha256':sha(src),'operation':'Mechanical geometry GUIDE ONLY. Exact native upper230 retained. Coarse lower region replaced by flat pale guidance and a single straight grey vertical inlay face x75..165, dark shallow edge66..74 and166..173, matching native top. No labels. Must be repainted by builtin AI; no guide pixels may be selected as final.','gameArt':False,'sourceResampling':False,'nativeTopPixelsPreserved':True}
Path(str(out)+'.derivation.json').write_text(json.dumps(der,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r['references'][0]={'file':str(out),'sha256':sha(out),'role':'edit target: mechanical geometry guide with exact native upper230; guide only, require native AI repaint'}
r['referenced_image_paths']=[x['file'] for x in r['references']]
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'guide':str(out),'sha256':sha(out),'colors':{'pale':pale,'grey':grey}}))

