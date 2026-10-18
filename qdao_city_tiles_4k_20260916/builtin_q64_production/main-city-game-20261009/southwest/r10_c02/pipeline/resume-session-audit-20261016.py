import json
from pathlib import Path
root=Path('C:/Users/luyua/.codex/sessions')
hits=[]
for day in ['2026/10/13','2026/10/14','2026/10/16']:
    for p in (root/day).glob('*.jsonl'):
        with p.open('rb') as f:
            d=f.read(16384).decode('utf-8','replace')
        if 'sw_left_continue_20261013c' in d:
            hits.append({'file':str(p),'bytes':p.stat().st_size})
print(json.dumps(hits,ensure_ascii=False))
for h in hits:
    p=Path(h['file'])
    with p.open('rb') as f:
        f.seek(max(0,h['bytes']-6000000))
        d=f.read().decode('utf-8','replace')
    rows=d.splitlines()[1:]
    events=[]
    for line in rows:
        try: v=json.loads(line)
        except: continue
        payload=v.get('payload',{})
        text=json.dumps(payload,ensure_ascii=False)
        if any(k in text for k in ['p02_03','output_hint','revoked','撤销','network','Network','imagegen','Permission']):
            if len(text)>20000: text=text[:20000]
            events.append({'timestamp':v.get('timestamp'),'type':v.get('type'),'payload':text})
    print(json.dumps(events[-14:],ensure_ascii=False))
