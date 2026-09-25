from pathlib import Path
import json,re
REC=Path(__file__).resolve().parents[1]
log=next(Path('C:/Users/Administrator/.codex/sessions/2026/09/23').glob('*01a0ce09-1862-7392-8b00-d94f5576ccb9*'))
mapping={1:'NE01-v2',2:'NE02-v3',14:'NE14-v2',16:'NE16-v2'}
for line in log.read_text(encoding='utf-8').splitlines():
 o=json.loads(line)
 if o.get('type')!='event_msg':continue
 item=o.get('payload',{}).get('item',{})
 if item.get('type')!='Extension' or not item.get('savedPath'):continue
 prompt=item.get('revisedPrompt','')
 m=re.search(r'WALK frame (\d+)/16',prompt)
 if not m:continue
 name=mapping.get(int(m[1]))
 if not name:continue
 arc=REC/'14-generation'/name
 req=json.loads((arc/'request.json').read_text(encoding='utf-8'))
 assert req['actual_request']['prompt']==prompt,'Exact recorded prompt mismatch'
 item={k:v for k,v in item.items() if k!='result'}
 saved=Path(item['savedPath']);assert saved.is_file()
 evidence={'timestamp':o['timestamp'],'ordinal':o['ordinal'],'item':item,'started_at_ms':o['payload'].get('started_at_ms'),'completed_at_ms':o['payload'].get('completed_at_ms')}
 (arc/'host-generation-receipt.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 out={'output_hint':'Actual savedPath recovered from host completed image generation event: '+str(saved),'exactReturnedOutputHintUnavailable':True,'receiptRecovery':{'reason':'Image generation succeeded; local result archive step used unsupported JavaScript btoa and failed before writing. Recovered actual host completion event, exact matching prompt, and original saved image; no regeneration.','evidence':'host-generation-receipt.json','sourceLog':str(log),'eventOrdinal':o['ordinal'],'promptExactMatch':True}}
 (arc/'tool-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(name,str(saved))
