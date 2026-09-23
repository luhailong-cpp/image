import sys,json,pathlib,datetime,hashlib
root=pathlib.Path(__file__).resolve().parents[4]
folder=pathlib.Path(__file__).resolve().parent
payload=json.load(sys.stdin)
p=folder/'review-20260923.json'
doc=json.loads(p.read_text(encoding='utf-8-sig'))
for attempt,info in payload.items():
    raw=root/'qdao_original_roster_v14_hd/recovery-20260921/10-generation'/attempt/'raw.png'
    info['rawSHA256']=hashlib.sha256(raw.read_bytes()).hexdigest()
    doc['observations'][attempt]=info
    slot=attempt.split('-')[0]
    if info['decision'].startswith('provisional'):
        direct='NW' if slot.startswith('NW') else 'W'
        sp=folder/f'selection-{direct}-review.json'
        selection=json.loads(sp.read_text()) if sp.exists() else {}
        selection[slot]={'archive':attempt,'review':info['decision']+': '+info['note']+'; full cycle, edges, proportions and seam review pending','rawSHA256':info['rawSHA256']}
        sp.write_text(json.dumps(dict(sorted(selection.items())),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doc['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Recorded',list(payload))
