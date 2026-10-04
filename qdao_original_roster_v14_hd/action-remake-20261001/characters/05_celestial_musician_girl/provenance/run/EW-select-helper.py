from pathlib import Path
import json,sys
r=Path(__file__).resolve().parents[2]
a,d,n,v,status,notes=sys.argv[1:];n=int(n);v=int(v)
file=f'staging/run/{d}/{n:02d}-v{v}.native.png' if a=='run' else f'staging/{a}/{d}-{n:02d}-v{v}.png'
record=f'provenance/run/{d}{n:02d}-v{v}.generation.json' if a=='run' else file+'.generation.json'
dest=r/('provenance/run/selection-EW.json' if a=='run' else 'provenance/attack/selection-W.json')
rows=json.loads(dest.read_text(encoding='utf-8-sig')) if dest.exists() else []
rows=[x for x in rows if not(x['action']==a and x['direction']==d and x['frame']==n)]
rows.append(dict(action=a,direction=d,frame=n,file=file,generationRecord=record,reviewStatus=status,notes=notes))
rows.sort(key=lambda x:(x['direction'],x['frame']))
dest.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
j=json.loads((r/record).read_text(encoding='utf-8-sig'));j['visualReview']=notes;j['status']=status
(r/record).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(file)

