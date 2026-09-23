from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
from ctypes import wintypes
import ctypes, hashlib, json, msvcrt, os, re, sys
RUN=Path(__file__).resolve().parent; P=RUN.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p):return {'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(p,v):
 with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def copy_exclusive(src,dst):
 with Path(src).open('rb') as a,Path(dst).open('xb') as b:
  while chunk:=a.read(1024*1024):b.write(chunk)
 assert sha(src)==sha(dst)
ident=sys.argv[1];stem=ident+'.v2'
receiptpath=RUN/f'{stem}.tool-response.json';receipt=read(receiptpath);requestpath=RUN/f'{stem}.request.json';request=read(requestpath)
preflightpath=RUN/f'{stem}.preflight.json';preflight=read(preflightpath)
assert request==receipt['request']
assert all(sha(x['file'])==x['sha256'] for x in preflight['references'])
src=Path(re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint'],re.S).group(1))
with Image.open(src) as im:
 im.load();assert im.size==(1254,1254) and im.format=='PNG'
 assert im.mode=='RGB' or (im.mode=='RGBA' and im.getextrema()[3]==(255,255))
 mode=im.mode
dst=P/'native'/f'{stem}.png';copy_exclusive(src,dst)
promptpath=P/'prompts'/f'{stem}.actual-prompt.txt'
with promptpath.open('x',encoding='utf-8',newline='\n') as f:f.write(request['prompt'])
native_receipt=P/'native'/f'{stem}.tool-response.json';copy_exclusive(receiptpath,native_receipt)
refs=[dict(x,path=x['file']) for x in preflight['references']]
record={'schemaVersion':4,'file':str(dst),'sha256':sha(dst),'nativeFile':str(dst),'nativeSha256':sha(dst),'nativePixels':[1254,1254],'width':1254,'height':1254,'format':'PNG','imageMode':mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':preflight['configSnapshot'],'configSnapshotFile':preflight['configSnapshotFile'],'modelCapabilityEvidence':preflight['modelCapabilityEvidence'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'Host-managed tool exposed no model, quality or size selectors; returned image_url and output_hint with no verifiable backend model/quality/time.','generatedAt':None,'observedCompletionAt':receipt['observedCompletionAt'],'observedCompletionAtMeaning':'Current tool completion observed through clock.curr_time, not server generation timestamp','savedAtUtc':now(),'prompt':info(promptpath),'promptFile':str(promptpath),'promptSha256':sha(promptpath),'actualRequest':request,'request':info(requestpath),'preflight':info(preflightpath),'references':refs,'submittedImages':refs,'evidence':info(native_receipt),'originalToolReceipt':info(receiptpath),'toolOutputPath':str(src),'toolOutputSha256':sha(src),'toolOutputBytes':src.stat().st_size,'editBefore':{'file':refs[0]['file'],'sha256':refs[0]['sha256'],'role':'Existing layout-only guide, not deleted rejected artwork','layoutRecord':info(P/'layout-record.json')},'resampled':False,'finalArtUpscaled':False,'originalNativeBytesPreserved':True,'visualStatus':'pending_native_review_assembly_and_QA','productionAccepted':False,'accepted':False,'runtimePublished':False,'retentionPurpose':'Necessary native work in progress until final intended game tile is saved and current references complete; then follow latest user cleanup policy.'}
recordpath=P/'native'/f'{stem}.generation.json';write(recordpath,record)
planpath=P/'plan.json';before=planpath.read_bytes();before_sha=hashlib.sha256(before).hexdigest();plan=json.loads(before)
patch=next(x for x in plan['patches'] if x['id']==ident)
patch.update({'status':'native_saved_pending_QA','outputFile':f'native/{stem}.png','generationRecord':info(recordpath),'nativeSha256':sha(dst)})
plan['status']='native_detail_generation_in_progress'
backup=RUN/f'plan-before-{stem}-{before_sha[:12]}.json'
with backup.open('xb') as f:f.write(before)
new=(json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
k.CreateFileW.restype=wintypes.HANDLE
h=k.CreateFileW(str(planpath),0x80000000|0x40000000,0,None,3,0x80,None)
if h==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
fd=msvcrt.open_osfhandle(h,os.O_RDWR|os.O_BINARY)
with os.fdopen(fd,'r+b') as locked:
 current=locked.read()
 assert hashlib.sha256(current).hexdigest()==before_sha,'Concurrent plan change; saved new PNG/records but did not overwrite plan'
 locked.seek(0);locked.write(new);locked.truncate();locked.flush();os.fsync(locked.fileno())
assert sha(planpath)==hashlib.sha256(new).hexdigest()
write(RUN/f'{stem}.save-receipt.json',{'savedAtUtc':now(),'image':info(dst),'generation':info(recordpath),'originalByteEqual':sha(src)==sha(dst),'inputRefsUnchanged':all(sha(x['file'])==x['sha256'] for x in preflight['references']),'planBeforeBackup':info(backup),'planBeforeSha256':before_sha,'planAfter':info(planpath),'concurrencyGuard':'Pre-write SHA compare while holding exclusive Windows CreateFile share-none handle','formalAccepted':False})
print(json.dumps({'image':info(dst),'record':info(recordpath),'planUpdatedWithBackupAndCAS':True}))

