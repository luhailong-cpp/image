from pathlib import Path
import json,shutil
r=Path(r'E:\work\image\qdao_chibi_roster_v12');p=r/'review/he_xiangu_natural_walk';c=r/'candidate-natural-body/29_he_xiangu';fix=p/'idle-proportion-fixes'
shutil.copyfile(fix/'E-W-idle-candidate-raw.png',fix/'E-W-idle-final-raw.png')
overrides={}
for i,d in enumerate(['N','S','SE','SW']):overrides[d]={'path':str(fix/'N-S-SE-SW-idle-final-raw.png'),'cols':2,'rows':2,'index':i}
for i,d in enumerate(['E','W']):overrides[d]={'path':str(fix/'E-W-idle-final-raw.png'),'cols':2,'rows':1,'index':i}
(p/'idle-overrides.json').write_text(json.dumps(overrides,indent=2)+'\n')
backup=c/'review/before-idle-proportion-correction';backup.mkdir(exist_ok=True)
for d in ['N','NE','E','SE','S','SW','W','NW']:
 for i in range(1,9):
  rel=Path('walk')/d/(f'{i:02d}.png');dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(c/rel,dst)
for f in ['manifest.json','qc.json','validation.json']:shutil.copyfile(c/f,backup/f)
f=p/'assemble_natural_candidate.py';t=f.read_text(encoding='utf-8')
t=t.replace("parser.add_argument('--process',action='store_true');args=parser.parse_args()","parser.add_argument('--process',action='store_true');parser.add_argument('--idle-only',action='store_true');args=parser.parse_args()")
t=t.replace("for d,plan in plans.items():\n required=", "for d,plan in plans.items():\n if args.idle_only:\n  dest=SRC/f'walk-{d}-raw.png';data=json.loads(dest.with_suffix('.assembly.json').read_text());assert sha(dest)==data['output_sha256'];paths[d]=dest;allrecords[d]=data['sources'];continue\n required=")
t=t.replace(" subprocess.run([sys.executable,str(ROOT/'assemble_raw.py')"," if args.idle_only:continue\n subprocess.run([sys.executable,str(ROOT/'assemble_raw.py')")
t=t.replace("idle=Image.new('RGBA',(2508,1254),(255,0,255,255));records=[]","idle=Image.new('RGBA',(2508,1254),(255,0,255,255));records=[]\noverrides=json.loads((P/'idle-overrides.json').read_text()) if (P/'idle-overrides.json').exists() else {}")
t=t.replace(" p=P/'directions'/d/'idle-source-cell.png';pose,record=cell(p,1,1,0);idle.paste(pose,(i%4*627,i//4*627));record.update(direction=d);records.append(record)"," if d in overrides:\n  o=overrides[d];p=Path(o['path']);pose,record=cell(p,o['cols'],o['rows'],o['index']);record['revision']='independently redrawn neutral idle matched to same-direction walk03 head size'\n else:\n  p=P/'directions'/d/'idle-source-cell.png';pose,record=cell(p,1,1,0)\n idle.paste(pose,(i%4*627,i//4*627));record.update(direction=d);records.append(record)")
t=t.replace("'--portrait-raw',str(P/'master-raw.png')]","'--portrait-raw',str(P/'master-raw.png'),'--despill-magenta-edge','--despill-radius','4']")
f.write_text(t,encoding='utf-8')
print('Six authored idle overrides configured; original64 walk snapshots saved; idle-only rebuild preserves all original walk sources')

