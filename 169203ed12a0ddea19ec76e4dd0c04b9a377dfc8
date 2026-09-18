from pathlib import Path
from PIL import Image
import json,hashlib,sys
root=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/donghai_lantern/r08_c10');ident=sys.argv[1];plan=json.loads((root/'plan.json').read_text());p=next(x for x in plan['patches'] if x['id']==ident);sha=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest();g=Path(p['guide']);raw=g.with_name(ident+'.day-geometry-source.png')
if (root/'native'/f'{ident}.png').exists():raise RuntimeError('Existing native; no prep overwrite')
if raw.exists():raise RuntimeError('Patch already prepared')
g.replace(raw);im=Image.open(raw).convert('RGB');deps=[]
for side,r,c in [('left',p['row']+1,p['column']),('top',p['row'],p['column']+1)]:
 if r<1 or c<1:continue
 neighbor=root/'native'/f'r{r:02d}_c{c:02d}.png'
 if not neighbor.exists():continue
 n=Image.open(neighbor).convert('RGB');box=(1024,0,1254,1254) if side=='left' else (0,1024,1254,1254);im.paste(n.crop(box),(0,0));deps.append(dict(side=side,path=str(neighbor),sha256=sha(neighbor),cropXYXY=list(box),resized=False))
im.save(g);im.save(p['submittedReference'],quality=90);p['guideSha256']=sha(g);p['submittedReferenceSha256']=sha(p['submittedReference']);p['nativeNeighborGuideStrips']=deps;p['dayGeometrySourceCrop']=dict(path=str(raw),sha256=sha(raw));p['dayGeometryCropExact']=not bool(deps)
pr=root/'prompts'/f'{ident}.prompt.txt';text=pr.read_text();pr.write_text(text+'\n\nCONTINUITY: Narrow existing festival-colored strips at the left and/or top edge are exact native neighbor context. Preserve their geometry and festival palette, smoothly continue that same warm-gold light and lavender shadow treatment through the daytime-colored interior. Do not create any visible border between them. Keep all edge objects registered exactly.',encoding='utf8');(root/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(dict(id=ident,neighborStrips=len(deps))))
