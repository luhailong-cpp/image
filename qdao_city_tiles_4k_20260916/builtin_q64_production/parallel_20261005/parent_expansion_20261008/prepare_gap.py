from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,sys
R=Path(__file__).resolve().parent;P=R.parent;T=P/'tianyong_festival'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
name=sys.argv[1];assert name in ['r02_c01','r02_c03']
col=int(name[-2:]);box=[(col-1)*1024-115,909,(col-1)*1024+1139,2163]
cp=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8-sig'))
progress=json.loads((T/'progress.json').read_text(encoding='utf-8-sig'))
sp=Path(progress['candidateSet']);sel=json.loads(sp.read_text(encoding='utf-8-sig'))
by={e.get('tile'):e for e in sel['candidates']}
ctx=Image.new('RGBA',(1254,1254));parts=[]
for tile,ox in [('r08_c09',-4096),('r08_c10',0)]:
    e=by[tile];p=Path(e['file']);assert sha(p)==e['sha256']
    ix0=max(box[0],ox);ix1=min(box[2],ox+4096)
    if ix0>=ix1:continue
    crop=[ix0-ox,box[1],ix1-ox,box[3]];dst=[ix0-box[0],0]
    with Image.open(p) as im:ctx.paste(im.convert('RGBA').crop(crop),dst)
    parts.append({'source':e,'cropLTRB':crop,'pasteXY':dst})
O=R/name;O.mkdir(exist_ok=True);ctx.save(O/'context.png')
guide=(T/'r08_c10'/f'{name}-v1'/'layout-reference-only.png')
style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
refs=[O/'context.png',guide,style]
prompt='''Use case: precise-object-edit / outpainting. Complete the transparent missing area in image1, an exact native crop from an original chibi fantasy city map. The opaque pixels are the authoritative existing map, fixed in place. Image2 is ONLY the low-detail same-coordinate layout guide; do not copy its enlarged pixels. Image3 is ONLY the approved bright clean rounded painterly style; no UI or text. Return the same square framing with new native detail filling the transparent gap. Match the existing border silhouettes, stone joints, bevel widths, colors and cast shadows exactly. Continue every ivory and restrained gold curved plaza band smoothly from the top to its existing lower endpoint and side endpoint. Keep existing opaque borders structurally unchanged. Broad quiet warm-ivory and gray stone surfaces, clean rounded bevels, no new decorative relief, building or prop, no grunge, crack, noise, letters or watermark. The transparency boundary is not a physical tile seam: do not add a straight ledge, frame or stripe across it. Preserve perspective and scale. No rotation, rescale or new layout.'''
req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c10','patch':name,'windowTileLocalLTRB':box,
 'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},
 'references':[{'file':str(p),'sha256':sha(p),'role':role} for p,role in zip(refs,['edit target','layout only','approved primary style'])],
 'sourceSelection':{'file':str(sp),'sha256':sha(sp)},'parts':parts,
 'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))}
(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'context.png.generation.json').write_text(json.dumps({'file':str(O/'context.png'),'sha256':sha(O/'context.png'),
 'operation':'Native crop+concat with current missing alpha preserved; no resize.','parts':parts},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'request':str(O/'request.json'),'context':str(O/'context.png'),'guide':str(guide),'box':box}))
