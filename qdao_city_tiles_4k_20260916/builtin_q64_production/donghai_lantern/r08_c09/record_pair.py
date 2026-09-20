from pathlib import Path
import subprocess,sys,json,hashlib
root=Path(__file__).resolve().parent
ids=sys.argv[1].split(',')
sources=sys.argv[2].split(',')
refs=json.loads(Path(sys.argv[3]).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for i,(ident,source) in enumerate(zip(ids,sources)):
 subprocess.run([sys.executable,str(root/'record_native.py'),ident,source,sys.argv[4]],check=True)
 p=root/'native'/f'{ident}.record.json'
 r=json.loads(p.read_text(encoding='utf-8'))
 r['actualInputReferences']=[{'imageIndex':j+1,'path':p,'sha256':sha(p)} for j,p in enumerate(refs)]
 r['selectedGeometryImageIndex']=i*2+1
 r['selectedAppearanceImageIndex']=i*2+2
 r['inputCount']=4
 r['otherImagesRole']='adjacent context only'
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')

