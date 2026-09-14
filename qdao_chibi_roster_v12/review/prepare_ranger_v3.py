from pathlib import Path
import subprocess,sys,json,hashlib
r=Path(r'E:\work\image\qdao_chibi_roster_v12');s=r/'27_ink_kite_ranger/source';c=r/'candidate-stable-body/27_ink_kite_ranger';c.mkdir(parents=True,exist_ok=True)
if (c/'manifest.json').exists():raise SystemExit('Candidate already exists; inspect before rebuilding')
sources={k:s/n for k,n in [('s-e','pair-s_e.png'),('n-w','pair-n_w.png'),('ne-sw','pair-ne_sw.png'),('nw-se','pair-nw_se.png'),('idle','idle.png')]}
(c/'alignment-only-provenance.json').write_text(json.dumps({'status':'raw proportion issues expected; do not publish','sources':{k:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in sources.items()},'scale':0.997624703087886},indent=2))
cmd=[sys.executable,'-X','utf8',str(r/'process_roster.py'),'--character-dir',str(c),'--alignment-version','3','--common-scale','0.997624703087886','--portrait-raw',str(s/'portrait-daoist.png'),'--component-padding','0']
for k,p in sources.items():cmd+=['--'+k,str(p)]
result=subprocess.run(cmd);print('processor_exit',result.returncode)
if (c/'walk/N/01.png').exists():subprocess.run([sys.executable,str(r/'review/lu_natural_walk_sample/build_final_review.py'),'--character',c.name],check=True)

