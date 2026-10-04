from pathlib import Path
import json,sys,re,subprocess
root=Path(__file__).resolve().parents[2]
stem=sys.argv[1]
folder=root/'generation/run/SE'
receipt=json.loads((folder/(stem+'.receipt.json')).read_text(encoding='utf-8'))
reqpath=folder/(stem+'.request.json')
req=json.loads(reqpath.read_text(encoding='utf-8'))
req['startedAt']=receipt['startedAt'];req['status']='returned_success'
reqpath.write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
src=re.search(r'as (.+?\.png) by default',receipt['output_hint']).group(1)
subprocess.run([sys.executable,str(root/'tools/ingest_generated.py'),'--source',src,'--output','generation/run/SE/'+stem+'.png','--request','generation/run/SE/'+stem+'.request.json','--receipt','generation/run/SE/'+stem+'.receipt.json'],check=True)

