"""Evidence audit for character 14, independent of visual approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
import numpy as np
REC=Path(__file__).resolve().parents[1]
OUT=REC/'14-delivery-preview'; ASSETS=OUT/'assets'; GEN=REC/'14-generation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 rows=[];errors=[];sources={};pixels={};selected=set()
 for p in sorted(ASSETS.rglob('*.png')):
  meta=read(Path(str(p)+'.generation.json'));arc=GEN/meta['sourceArchive'];selected.add(arc.name)
  req=read(arc/'request.json');actual=req.get('actual_request',req.get('request',req));receipt=read(arc/'tool-result.json');raw=arc/'raw.png'
  checks={
   'exactPrompt':(arc/'prompt.txt').read_text(encoding='utf-8-sig')==actual['prompt'],
   'receiptPresent':bool(receipt.get('output_hint')),
   'rawPresent':raw.is_file(),
   'rawShaMatches':raw.is_file() and sha(raw)==meta['derivedFrom']['sha256'],
   'assetShaMatches':sha(p)==meta['sha256'],
   'builtinOnly':meta['route']=='builtin' and meta['paid_api_calls']==0,
   'actualModelNotFabricated':meta.get('actualModel') is None and meta.get('actualQuality') is None,
  }
  im=Image.open(p);a=np.asarray(im);native=Image.open(raw)
  checks.update({'nativeAtLeast1024':min(native.size)>=1024,'nativeIsCompleteSingleSquare':native.width==native.height,'final1024RGBA':im.size==(1024,1024) and im.mode=='RGBA','hasRealTransparency':bool((a[:,:,3]==0).any() and (a[:,:,3]==255).any()),'soleAnchor942':int(np.where(a[:,:,3]>8)[0].max())==942,'noUpscale':meta['operation']['scale']<=1,'alphaPreservedByCleanup':all(x['alphaUnchanged'] and x['alphaSHA256Before']==x['alphaSHA256After'] for x in meta.get('colorCleanup',[]))})
  digest=hashlib.sha256(a.tobytes()).hexdigest();rsha=sha(raw)
  checks['uniqueRaw']=rsha not in sources; checks['uniquePixels']=digest not in pixels
  sources[rsha]=str(p.relative_to(ASSETS));pixels[digest]=str(p.relative_to(ASSETS))
  row={'file':str(p.relative_to(ASSETS)).replace('\\','/'),'sourceArchive':arc.name,'checks':checks,'rawSHA256':rsha,'finalSHA256':sha(p),'pixelSHA256':digest,'nativeSize':list(native.size)};rows.append(row)
  errors.extend([{'file':row['file'],'check':k} for k,v in checks.items() if not v])
 unselected=[];pending=[]
 for arc in sorted(GEN.iterdir()):
  if not arc.is_dir():continue
  if (arc/'raw.png').is_file() and arc.name not in selected:unselected.append(arc.name)
  if (arc/'request.json').is_file() and not (arc/'raw.png').is_file():pending.append({'archive':arc.name,'hasReceipt':(arc/'tool-result.json').is_file()})
 report={'character':'14_short_hair_snow_summoner_girl','checkedAt':datetime.now(timezone.utc).isoformat(),'selectedCount':len(rows),'walkCount':sum(r['file'].startswith('walk/') for r in rows),'idleCount':sum(r['file'].startswith('idle/') for r in rows),'sourceAuditPass':not errors and len(rows)==136,'errors':errors,'selected':rows,'unselectedArchivesNotCounted':unselected,'requestsWithoutArchivedRaw':pending,'visualApproval':'separate review required','clientIntegration':'not performed','sourceRetention':'Latest user instruction requires actual originals and exact per-image evidence; retained.'}
 (OUT/'source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k not in ('selected','unselectedArchivesNotCounted')},ensure_ascii=False))
if __name__=='__main__':main()
