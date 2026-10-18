from pathlib import Path
import sys
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import workflow_20261016 as w
p=w.p;a=p.read(T/'external-core-anchors.json')
for pid,ident,h,x in [('s01_03','s01_03_fix03','5b9ba58da15a3e703b07e82f65b23db640938be40448d8876aff81bbe177254e',30720),('s01_04','s01_04_native01','45e932b8349ce156f2131ab3ca6e5c00f41fff994c1536cfbc81e5920b3b8a96',31744)]:
 f=T.parent/'r06_c08/native'/(ident+'.png');assert p.sha(f)==h
 assert str(p.selected_path(f.parent.parent,pid)).replace('\\','/')==str(f).replace('\\','/')
 a['sources'].append(dict(file=str(f),sha256=h,tile='r06_c08',patch=pid,worldBox=[x,20480,x+1024,21504],sourceOffset=[115,115]))
p.write_json(T/'external-core-anchors-v2-20261017.json',a,replace=False)
print('registry saved')

