from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,sys
B=Path(__file__).resolve().parents[1];T=B/'r12_c06';name='right-ground-inlay-20261016-v01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prefix=T/'pipeline/prompts'/f'{name}.content-prefix.txt';assert not prefix.exists()
prefix.write_text('Restore the original missing UPPER shallow gray horizontal stone inlay and the original sparse diagonal ground seam in this exact native crop. Image5 is aligned original layout guidance, not surface pattern. Local target coordinates are original p01_04 y minus115: upper flat inlay spans across the crop at y465..568 (upper pale half y465..516, lower gray half y517..568); the sparse diagonal join rises right from near x0,y535 toward x1050,y0 and crosses that upper inlay near the left. Remove the incorrect lone thin horizontal join at y645 that currently substitutes for the upper inlay. Preserve the separate LOWER blue-gray horizontal strip around y735..785 exactly; never move it upward. Keep the gold post, gold railing, clipped shapes, shadows, all existing scale and lower architecture unchanged. Only restore those missing original ground features; no extra grid/frame or raised curb. Ground faces remain broad quiet smooth pale-gray daylight stone with extremely subtle shading; guide pixels are not tiny stone cells. No polygon patches, cellular outlines, diamond meshes, cracks or noise. Restore new native art in the original footprint, no resampling.\\n',encoding='utf-8')
a=T/'repairs-resume-20261012/V2-roof-rim-v01/integrated/assembly.json'
subprocess.run([sys.executable,'-X','utf8',str(B/'pipeline-tools/root-local-repair-20261012.py'),'prepare','r12_c06',name,str(a),'2957','0',str(prefix)],check=True)
d=T/'repairs-resume-20261012'/name
g1=T/'guides/p01_04.layout-only.png';g2=T/'guides/p02_04.layout-only.png'
out=d/'aligned-layout-guidance.png';im=Image.new('RGB',(1254,1254));im.paste(Image.open(g1).convert('RGB').crop((0,115,1254,1254)),(0,0));im.paste(Image.open(g2).convert('RGB').crop((0,230,1254,345)),(0,1139));im.save(out)
der={'purpose':'aligned layout guidance only, never native game art','sources':[{'file':str(g1),'sha256':sha(g1),'crop':[0,115,1254,1254],'target':[0,0]},{'file':str(g2),'sha256':sha(g2),'crop':[0,230,1254,345],'target':[0,1139]}],'operations':'exact crop/paste of existing guide, no additional resampling','finalArtwork':False,'sha256':sha(out)}
out.with_suffix('.derivation.json').write_text(json.dumps(der,ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')
r=json.loads((d/'request.json').read_text(encoding='utf-8'));r['references'][4]={'file':str(out),'sha256':sha(out),'role':'aligned original local layout guidance only, coarse pixels not native art or surface pattern'};r['referenced_image_paths']=[v['file'] for v in r['references']]
r['prompt']=r['prompt'].replace('Image 5 is quiet smooth natural stone surface finish only; copy no geometry, seams or red paper.','Image 5 is aligned original layout guidance only; restore its missing sparse ground joins at native detail, never copy coarse pixel blocks as stone cells.');(d/'prompt.txt').write_text(r['prompt'],encoding='utf-8');r['promptSha256']=sha(d/'prompt.txt');(d/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')
print(json.dumps({'request':str(d/'request.json'),'input':str(d/'input.png'),'guide':str(out),'plannedPatchWindow':[0,350,1254,700],'baseCandidateSha256':r['inputCandidateSha256']}))

