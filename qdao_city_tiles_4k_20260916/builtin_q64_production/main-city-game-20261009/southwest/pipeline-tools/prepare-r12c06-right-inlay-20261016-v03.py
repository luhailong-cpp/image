from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,sys
B=Path(__file__).resolve().parents[1];T=B/'r12_c06';name='right-ground-inlay-20261016-v03';v2=T/'repairs-resume-20261012/right-ground-inlay-20261016-v02';v1=T/'repairs-resume-20261012/right-ground-inlay-20261016-v01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rev={'actualNativeViewed':True,'selected':False,'formalAccepted':False,'improved':['upper inlay starts near469, close to465','diagonal slope improved','lower blue strip remains fixed'],'remaining':['upper inlay bottom584 vs original568','diagonal intercepts still need consolidated QA'],'next':'one native-band alignment guidance, no repeated broad repaint'}
assert not (v2/'root-review.json').exists();(v2/'root-review.json').write_text(json.dumps(rev,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=T/'pipeline/prompts'/f'{name}.content-prefix.txt';assert not p.exists()
p.write_text('Image1 is a mechanical native-band alignment guide, not a finished generated native. Produce the final native edit preserving its corrected UPPER inlay exactly y465..568. It consists of pale stone y465..524 and lower neutral-gray stone y524..568; integrate the guidance joins into one clean shallow flat band without moving its top or bottom. Do NOT expand its height back down to584. Keep the existing sparse diagonal join in position and continuous through the upper inlay. Preserve the entire separate LOWER blue-gray band y735..785, the gold scroll/railing, shadows and all architecture/crop/scale exactly. No new ground joints, grid/frame, cracks or props. Quiet broad pale-gray daylight surfaces, no cellular/diamond texture. Output one native1254x1254 opaque PNG.\n',encoding='utf-8')
a=T/'repairs-resume-20261012/V2-roof-rim-v01/integrated/assembly.json'
subprocess.run([sys.executable,'-X','utf8',str(B/'pipeline-tools/root-local-repair-20261012.py'),'prepare','r12_c06',name,str(a),'2957','0',str(p)],check=True)
d=T/'repairs-resume-20261012'/name;s=Image.open(v2/'native.png').convert('RGB');assert s.size==(1254,1254);im=s.copy()
im.paste(s.crop((0,600,1254,620)),(0,568))
im.paste(s.crop((0,468,1254,527)),(0,465))
im.paste(s.crop((0,540,1254,584)),(0,524))
g=d/'native-band-alignment-guidance.png';im.save(g)
der={'guidanceOnly':True,'finalArtwork':False,'source':str(v2/'native.png'),'sourceSha256':sha(v2/'native.png'),'operations':[{'sourceBox':[0,600,1254,620],'target':[0,568],'purpose':'temporary native ground guidance only'},{'sourceBox':[0,468,1254,527],'target':[0,465]},{'sourceBox':[0,540,1254,584],'target':[0,524]}],'sourceResampling':False,'sha256':sha(g)}
g.with_suffix('.derivation.json').write_text(json.dumps(der,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=json.loads((d/'request.json').read_text(encoding='utf-8'));r['references'][0]={'file':str(g),'sha256':sha(g),'role':'mechanical native-band alignment guidance only; exact crop/paste, no resampling; not generated final artwork','derivation':str(g.with_suffix('.derivation.json'))}
orig=v1/'aligned-layout-guidance.png';r['references'][4]={'file':str(orig),'sha256':sha(orig),'role':'aligned original local layout only; no surface pattern or final pixels'};r['referenced_image_paths']=[v['file'] for v in r['references']]
r['prompt']=r['prompt'].replace('Image 5 is quiet smooth natural stone surface finish only; copy no geometry, seams or red paper.','Image 5 is aligned original local layout only, not surface pattern or final pixels.')
(d/'prompt.txt').write_text(r['prompt'],encoding='utf-8');r['promptSha256']=sha(d/'prompt.txt');r['plannedNativeSelectionWindow']=[0,0,1254,700];r['editBaseGeneration']={'file':str(v2/'generation.json'),'sha256':sha(v2/'generation.json')}
(d/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))

