from pathlib import Path
import json,hashlib,shutil,subprocess,sys
r=Path(r'E:\work\image\qdao_chibi_roster_v12');c=r/'candidate-stable-body/30_han_xiangzi';out=c/'review/edge-before'
m=json.loads((c/'manifest.json').read_text());assert hashlib.sha256((c/'manifest.json').read_bytes()).hexdigest()=='fa9777534ff7fbc669195102553b5f88b139e3fdddddc114a9ece9e75ed116a1'
if out.exists():raise SystemExit('Existing edge snapshot needs inspection before overwrite')
out.mkdir(parents=True)
for d in ['N','NE','E','SE','S','SW','W','NW']:
 for rel in [Path('idle')/(d+'.png')]+[Path('walk')/d/(f'{i:02d}.png') for i in range(1,9)]:
  p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(c/rel,p)
for n in ['manifest.json','qc.json','validation.json']:shutil.copyfile(c/n,out/n)
cmd=[sys.executable,'-X','utf8',str(r/'process_roster.py'),'--character-dir',str(c),'--alignment-version','3','--common-scale',str(m['alignment']['common_scale']),'--component-padding','0','--despill-magenta-edge','--despill-radius','4','--portrait',str(r/'30_han_xiangzi/portrait.png')]
for k,s in m['sources'].items():
 assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256'];cmd+=['--'+k.replace('_','-'),s['path']]
subprocess.run(cmd,check=True)
p=r/'review/lu_natural_walk_sample/verify_final_edges.py';v=c/'review/verify_final_edges.py';v.write_text(p.read_text(encoding='utf-8-sig').replace('24_lu_dongbin','30_han_xiangzi'),encoding='utf-8');subprocess.run([sys.executable,str(v)],check=True)
subprocess.run([sys.executable,str(r/'verify_delivery.py'),'--character-dir',str(c),'--allow-pending-visual'],check=True)
subprocess.run([sys.executable,str(r/'review/lu_natural_walk_sample/build_final_review.py'),'--character',c.name],check=True)
print('30 edge cleanup completed with all72 alpha/G/geometry/protected colors verified')

