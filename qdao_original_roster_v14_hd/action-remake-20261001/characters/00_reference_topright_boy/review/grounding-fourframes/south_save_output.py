from pathlib import Path
import json,sys,re,subprocess
root=Path(__file__).resolve().parents[2];direction,stem=sys.argv[1:]
folder=root/'generation/run'/direction;receipt=json.loads((folder/(stem+'.receipt.json')).read_text(encoding='utf-8'))
reqpath=folder/(stem+'.request.json');req=json.loads(reqpath.read_text(encoding='utf-8'))
req['startedAt']=receipt['startedAt'];req['status']='returned_success';reqpath.write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
src=re.search(r'as (.+?\.png) by default',receipt['output_hint']).group(1)
rel='generation/run/'+direction+'/'+stem
subprocess.run([sys.executable,str(root/'tools/ingest_generated.py'),'--source',src,'--output',rel+'.png','--request',rel+'.request.json','--receipt',rel+'.receipt.json'],check=True)

