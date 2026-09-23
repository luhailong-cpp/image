from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,shutil
RUN=Path(__file__).resolve().parent;P=RUN.parent;ROOT=P.parents[3]
SRC=RUN/'diagnostic-20260923T114940236668Z';OUT=RUN/'local-repair-v1';OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
layout=json.loads((P/'layout-record.json').read_text(encoding='utf-8-sig'));bot=Path(layout['bottomCore']['file']);assert sha(bot)==layout['bottomCore']['sha256']
source=SRC/'r08_c08.png';assert sha(source)=='727526a5f7b8b1fe75e29052a2f7d34ec0c45ec79f07cd5a851e2ae96e838911'
canvas=Image.new('RGB',(4096,8192));canvas.paste(Image.open(source).convert('RGB'),(0,0));canvas.paste(Image.open(bot).convert('RGB'),(0,4096))
config=ROOT/'config/image-generation.json';(OUT/'config-snapshot.json').write_bytes(config.read_bytes());(OUT/'model-capability-snapshot.json').write_bytes((RUN/'model-capability-snapshot.json').read_bytes())
cases=[('band-c03',1900,3454),('band-c04',2842,3454),('carving-left',0,3454)]
for name,x,y in cases:
 target=OUT/(name+'.context.png');box=[x,y,x+1254,y+1254];canvas.crop(tuple(box)).save(target)
 desc='Preserve the diagonal paving joint and its endpoint at approximately local y527 exactly in place. Its current flat horizontal sliced end is a paste artifact: finish the same endpoint with a subtle clean rounded stone bevel, without lengthening the joint into the blank upper field.' if name!='carving-left' else 'The horizontal artifact near local y527 makes a tiny sliced notch in existing carved relief. Reconnect exactly the same carved stroke contour and highlights across that line; keep glyph silhouette and stone rings unchanged.'
 prompt='Use case: precise-object-edit. Repair image1 only, a native1254 x1254 cropped terrain context. It is already game art, not a layout guide. Remove the false horizontal paste/color line at image y527 (global city tile y3981), restore one continuous clean bright ivory/gold/dark stone surface across it. '+desc+' The genuine boundary between new upper tile and FIXED lower neighbor is image y642. Rows y642..1253 are locked reference context: do not alter, repaint or blur them. Repair only upper rows roughly y350..641; rows above y330 must remain unchanged. Preserve all real stone block joints, oval rim, glyphs, gold ring, camera, light direction, shapes and pixel scale. Preserve geometry even if it crosses the false horizontal line. Gentle broad material transition may approach the fixed lower context but do not spread mottled mineral flakes into clean upper ivory; no cloud patches, veins, microtexture, blur, cloned repeats or new ornamental objects. Image2 is native ivory material-only reference; image3 is the confirmed PRIMARY project Q/chibi hand-painted drawing style only, no UI or text from it. Exact same1254 x1254 framing, opaque full-bleed PNG, no collage/text/UI/watermark. Do not recompose, crop, upscale or add new seams. Keep every existing true line; remove the horizontal paste stripe and sliced contour error only.'
 refs=[target,RUN/'native-ivory-material-reference.png',ROOT/'designs/gameplay-ui/04-guild.png'];request={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs]};write(OUT/(name+'.request.json'),request)
 write(OUT/(name+'.preflight.json'),{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCandidate':info(source),'sourceAssembly':info(SRC/'assembly.json'),'fixedBottomNeighbor':info(bot),'canvasBoxLTRB':box,'candidateBoundaryLocalY':642,'artifactLocalY':527,'references':[dict(info(p),role=r) for p,r in zip(refs,['native actual edit target plus fixed lower neighbor','native ivory material only','confirmed designs primary drawing style'])],'configSnapshot':json.loads(config.read_text(encoding='utf-8-sig')),'configSnapshotFile':info(OUT/'config-snapshot.json'),'modelCapabilityEvidence':info(OUT/'model-capability-snapshot.json'),'actualRequest':info(OUT/(name+'.request.json')),'actualModel':None,'actualQuality':None,'generatedAt':None,'expectedNativePixels':[1254,1254],'formalAccepted':False})
print(json.dumps({'directory':str(OUT),'targets':[v[0] for v in cases]}))
