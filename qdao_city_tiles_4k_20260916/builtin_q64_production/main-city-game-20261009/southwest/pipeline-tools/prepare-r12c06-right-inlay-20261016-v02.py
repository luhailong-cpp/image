from pathlib import Path
import json,hashlib,subprocess,sys
B=Path(__file__).resolve().parents[1];T=B/'r12_c06';name='right-ground-inlay-20261016-v02';v1=T/'repairs-resume-20261012/right-ground-inlay-20261016-v01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
review={'nativeSha256':sha(v1/'native.png'),'actualNativeViewed':True,'selected':False,'formalAccepted':False,'improved':['missing upper inlay restored','incorrect down-right join removed','lower blue band and gold architecture preserved'],'remaining':['upper inlay top is y440 instead of target465; bottom close565 vs568','diagonal joint enters at x120,y565 and exits near x890,y0, instead of original x0,y535 to x1050,y0'],'decision':'single focused geometric correction before integration'}
rp=v1/'root-review.json';assert not rp.exists();rp.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=T/'pipeline/prompts'/f'{name}.content-prefix.txt';assert not p.exists()
p.write_text('Edit the actual native candidate Image1 with two precise geometric corrections only. The UPPER flat inlay must start at y465 and end at y568: pale-gray top half y465..516, neutral-gray lower half y517..568. Current upper edge is y440, too high; lower it25px while keeping bottom at568, use thin clean shallow joints and no blue tint in this upper inlay. The single diagonal paving join must be one straight projected line from x0,y535 to x1050,y0, crossing the upper inlay near the left edge. Current line wrongly runs from x120,y565 to x890,y0; correct its slope/intercepts to the original aligned geometry Image5. No extra diagonal or grid. Preserve LOWER blue-gray band around y735..785, gold scroll/railing, building and every lower feature exactly; never move lower band. Broad quiet natural pale-gray ground, no polygon/diamond/cellular mesh or cracks. Native1254 square identical crop.\n',encoding='utf-8')
a=T/'repairs-resume-20261012/V2-roof-rim-v01/integrated/assembly.json'
subprocess.run([sys.executable,'-X','utf8',str(B/'pipeline-tools/root-local-repair-20261012.py'),'prepare','r12_c06',name,str(a),'2957','0',str(p)],check=True)
d=T/'repairs-resume-20261012'/name;r=json.loads((d/'request.json').read_text(encoding='utf-8'))
r['references'][0]={'file':str(v1/'native.png'),'sha256':sha(v1/'native.png'),'role':'actual builtin native candidate to edit, identical context crop; original assembly crop retained as input.png'}
g=v1/'aligned-layout-guidance.png';r['references'][4]={'file':str(g),'sha256':sha(g),'role':'aligned original layout guidance, no final pixels or material pattern'}
r['referenced_image_paths']=[v['file'] for v in r['references']]
r['prompt']=r['prompt'].replace('Image 5 is quiet smooth natural stone surface finish only; copy no geometry, seams or red paper.','Image 5 is aligned original local geometry only, not surface pattern or final artwork.')
(d/'prompt.txt').write_text(r['prompt'],encoding='utf-8');r['promptSha256']=sha(d/'prompt.txt');r['editBaseGeneration']={'file':str(v1/'generation.json'),'sha256':sha(v1/'generation.json')};r['plannedNativeSelectionWindow']=[0,0,1254,700]
(d/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r))

