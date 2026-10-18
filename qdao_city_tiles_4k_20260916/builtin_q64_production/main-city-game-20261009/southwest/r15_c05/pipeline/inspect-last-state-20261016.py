from pathlib import Path
import json
p=Path('C:/Users/luyua/.codex/sessions/2026/10/13/rollout-2026-10-13T12-32-48-01a1361c-0335-7161-bea3-a1f58f9ca8b6.jsonl')
with p.open('rb') as f:
 f.seek(max(0,p.stat().st_size-16*1024*1024));s=f.read().decode('utf-8','replace')
for line in s.splitlines():
 try:o=json.loads(line)
 except Exception:continue
 pl=o.get('payload',{})
 if not isinstance(pl,dict):continue
 if o.get('type')=='response_item' and pl.get('type') not in ['reasoning','message']:
  text=str(pl.get('input',pl.get('output',pl.get('arguments',''))))
  print(o.get('timestamp'),pl.get('type'),pl.get('name'),pl.get('namespace'),text[:1400] if not text.startswith('gAAAA') else '[encrypted body unavailable]')
 elif o.get('type')=='event_msg' and pl.get('type')=='item_completed':
  item=pl.get('item',{})
  if item.get('type') in ['McpToolCall','CustomToolCall','ToolCall']:print(o.get('timestamp'),'EVENT',json.dumps(item,ensure_ascii=False)[:1200])
