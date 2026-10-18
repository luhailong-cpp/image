from pathlib import Path
import json
root=Path('C:/Users/luyua/.codex/sessions/2026/10/13')
for name in ['rollout-2026-10-13T12-32-48-01a1361c-0335-7161-bea3-a1f58f9ca8b6.jsonl','rollout-2026-10-13T12-24-55-01a13614-ce7c-75b3-acf3-4eae68bfd935.jsonl']:
 p=root/name
 with p.open('rb') as f:
  header=f.readline().decode('utf-8','replace')
  f.seek(max(0,p.stat().st_size-16*1024*1024));data=f.read().decode('utf-8','replace')
 print('FILE',name,'HEADER',header[:1500])
 for line in data.splitlines():
  try:o=json.loads(line)
  except Exception:continue
  pl=o.get('payload',{})
  typ=pl.get('type')
  if typ=='function_call' and ('image' in str(pl.get('name')) or 'p03_01' in str(pl.get('arguments'))):
   print('CALL',o.get('timestamp'),json.dumps(pl,ensure_ascii=False)[:6000])
  elif typ=='function_call_output':
   s=str(pl.get('output',''))
   if any(t in s for t in ['output_hint','revoked','权限','Script running']):print('RETURN',o.get('timestamp'),s[:2500])
  elif typ=='message' and pl.get('role')=='assistant':
   cs=pl.get('content',[])
   text=''.join(x.get('text','') for x in cs if isinstance(x,dict))
   if text: print('MESSAGE',o.get('timestamp'),text[:1500])
