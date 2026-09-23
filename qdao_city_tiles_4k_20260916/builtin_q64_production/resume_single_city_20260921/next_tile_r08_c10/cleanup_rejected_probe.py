"""Delete exactly four rejected probe images after SHA/root checks.

Uses Windows exclusive handles; preserves raw bytes of text metadata only.
Never traverses/deletes directories, generated host cache or shared ledgers.
"""
from pathlib import Path
from datetime import datetime,timezone
import ctypes,json,hashlib,os,msvcrt,stat
from ctypes import wintypes

P=Path(__file__).resolve().parent
B=P/'probe-r04_c02-20260923T125732Z'
C=B/'cleanup-rejected-probe-20260923'
assert os.name=='nt'
def now():return datetime.now(timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(o):return (json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def newfile(p,b):
    with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def dump(p,o):newfile(p,encode(o))
def record(p):return {'file':str(p),'sha256':sha(p.read_bytes())}

expected={
 P/'native/r04_c02.probe-20260923T125732Z.png':'1129a25b56ca3d4946c27b38a88108c5700a3411371947cb1f2db7468233873c',
 B/'qa/halo-comparison-generated-top-neighbor-bottom.png':'410a4c0d81ecef3cecb1421cfceb71245d79b3c197cdd95c37b0dec9c6b63ac7',
 B/'qa/hypothetical-core-to-bottom-seam-native.png':'1d6610ff0cd27b202d7f305e2552281f7c3610995a780fe215046e86e033e286',
 B/'qa/generated-y1139-context-native.png':'df77117bed5e9d915403ca0e3ddb98ae52f22409bcf98f4fc4e05a793d518faf'
}
texts=[P/'HANDOFF.md',B/'handoff-probe.json',B/'README.md',P/'native/r04_c02.probe-20260923T125732Z.png.generation.json',B/'local-review.json',B/'qa/derived-review-images.json']
preserve=[B/'actual-request.json',B/'actual-prompt.txt',B/'config-snapshot.json',B/'tool-receipt.json',B/'preflight.json',B/'root-layout-observation.json',P/'plan.json',P/'layout-record.json',P/'prepare_inputs.py']

def ensure_safe(p):
    resolved=p.resolve(strict=True)
    assert resolved.is_relative_to(P.resolve(strict=True)) and resolved!=P.resolve(),str(p)
    assert resolved==p.absolute(),f'Unexpected resolved alias: {p}'
    q=p
    while True:
        st=q.stat(follow_symlinks=False)
        assert not (getattr(st,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT),f'Reparse point: {q}'
        if q==P:break
        q=q.parent

kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
kernel.CreateFileW.restype=wintypes.HANDLE
kernel.SetFileInformationByHandle.argtypes=[wintypes.HANDLE,ctypes.c_int,wintypes.LPVOID,wintypes.DWORD]
kernel.SetFileInformationByHandle.restype=wintypes.BOOL
kernel.CloseHandle.argtypes=[wintypes.HANDLE]
kernel.CloseHandle.restype=wintypes.BOOL
INVALID=ctypes.c_void_p(-1).value
class DISPOSITION(ctypes.Structure):_fields_=[('DeleteFile',wintypes.BOOLEAN)]
def locked(p,access,mode):
    ensure_safe(p)
    h=kernel.CreateFileW(str(p),access,0,None,3,0x80,None)
    if h==INVALID:raise ctypes.WinError(ctypes.get_last_error())
    try:
        flags=os.O_BINARY|(os.O_RDWR if '+' in mode else os.O_RDONLY)
        fd=msvcrt.open_osfhandle(int(h),flags)
        return os.fdopen(fd,mode),h
    except Exception:
        kernel.CloseHandle(h);raise

assert not C.exists(),'Cleanup directory exists; do not rerun'
for p in [*expected,*texts,*preserve]:ensure_safe(p)
C.mkdir()
(C/'text-before').mkdir()
(C/'text-after').mkdir()
handles=[];before={};image_rows=[];receipt={'startedAtUtc':now(),'status':'preflight','deleted':[],'updatedText':[],'imageBackupsMade':False,'sharedJSONWritten':False,'hostCacheTouched':False}
try:
    # Acquire every intended mutation handle before any deletion or update.
    image_handles=[]
    for p,digest in expected.items():
        f,h=locked(p,0x80000000|0x00010000,'rb');handles.append(f)
        raw=f.read();assert sha(raw)==digest,f'SHA changed: {p}'
        row={'file':str(p),'sha256':digest,'bytes':len(raw),'resolvedWithin':str(P),'action':'delete_rejected_probe_or_failed_qa','role':'native_probe' if p.parent.name=='native' else 'failed_qa'}
        image_rows.append(row);image_handles.append((p,f,h,row))
    text_handles={}
    for i,p in enumerate(texts):
        f,h=locked(p,0x80000000|0x40000000,'r+b');handles.append(f)
        raw=f.read();before[p]=raw;text_handles[p]=f
        newfile(C/'text-before'/f'{i:02d}-{p.name}.before',raw)
    preserved_before={str(p):sha(p.read_bytes()) for p in preserve}
    images_untouched={str(p):sha(p.read_bytes()) for d in [P/'guides',P/'references',P/'review'] for p in d.glob('*.png')}
    failure={
      'recordedAtUtc':now(),'authority':'Root explicit rejection after personally viewing hypothetical-core-to-bottom-seam-native',
      'conclusion':'Rejected. Floral petal position and curved-boundary continuity show an obvious horizontal discontinuity at selected r09_c10 external-v8; bottom seam failed.',
      'candidate':image_rows[0],'nativeSelectionCountAfterCleanup':0,
      'nextStep':'Resolve local geometry continuity between original master and selected neighbor before another probe; do not rerun the same prompt.',
      'preserve':'16-patch prepared geometry, design/style/material references, configuration, actual request, receipt and provenance text',
      'formalArtAcceptancePassed':False,'clientRuntimeAccepted':False
    }
    dump(C/'failure-conclusion.json',failure)
    manifest={'schemaVersion':1,'plannedAtUtc':now(),'authorization':'User retention policy and root bounded cleanup instruction','safeRoot':str(P),'files':image_rows,'totalBytes':sum(x['bytes'] for x in image_rows),'imageBackupsMade':False,'hostCacheTouched':False,'sharedJSONWritten':False,'failureConclusion':record(C/'failure-conclusion.json'),'textBackups':[{'file':str(p),'sha256':sha(before[p]),'backup':str(C/'text-before'/f'{i:02d}-{p.name}.before')} for i,p in enumerate(texts)]}
    dump(C/'manifest.json',manifest)
    manifestrec=record(C/'manifest.json')
    disposition={'status':'rejected_original_and_failed_qa_deleted_by_user_policy','recordedAtUtc':now(),'manifest':manifestrec,'failureConclusion':record(C/'failure-conclusion.json'),'nativeSelectionCount':0,'sourceReverification':'deleted_by_user_not_reverified_after_cleanup'}
    genpath=texts[3];gen=json.loads(before[genpath].decode('utf-8-sig'))
    gen['historicalSourceRetentionAtGeneration']=gen.get('sourceRetention')
    gen['sourceRetention']='Workspace rejected native probe deleted by explicit user policy; provenance remains. Host cache outside cleanup scope and untouched.'
    gen['currentFileState']='deleted_by_user_not_reverified_after_cleanup';gen['disposition']=disposition;gen['localReview']='root_rejected_bottom_geometry_and_material_discontinuity'
    reviewpath=texts[4];review=json.loads(before[reviewpath].decode('utf-8-sig'))
    review['historicalRetentionAtReview']=review.get('retention');review['retention']='Rejected native probe and failed QA images deleted; text evidence and exact source SHAs retained.'
    review['disposition']=disposition;review['rootRejected']=True
    for item in [review['candidate'],review['bottomExactPair']['newProbe'],*review['reviewedEvidence']]:item['currentFileState']='deleted_by_user_not_reverified_after_cleanup'
    derivedpath=texts[5];derived=json.loads(before[derivedpath].decode('utf-8-sig'));derived['disposition']=disposition
    for item in derived['entries']:item['image']['currentFileState']='deleted_by_user_not_reverified_after_cleanup'
    updated={genpath:encode(gen),reviewpath:encode(review),derivedpath:encode(derived)}
    handpath=texts[1];hand=json.loads(before[handpath].decode('utf-8-sig'));hand['disposition']=disposition
    hand['nativeImage']['currentFileState']='deleted_by_user_not_reverified_after_cleanup'
    hand['generationRecord']['sha256']=sha(updated[genpath]);hand['localReview']['sha256']=sha(updated[reviewpath])
    hand['nativeSelectionCount']=0;hand['rootRejected']=True;hand['nextStep']=failure['nextStep']
    updated[handpath]=encode(hand)
    prefix='''# 当前状态：r04_c02 探片拒选并已清理

2026-09-23 主任务亲看原像素接边，确认浮雕花瓣位置／弧形边界存在明显横断层，正式拒选。仅删除本探片原图与 3 张失败 QA 图，无图片备份；16 格准备几何、当前设计、风格与材质参考保留。当前选用 native 为 0，4096 候选为 0，正式验收为 0。

删除清单及原 SHA：`probe-r04_c02-20260923T125732Z/cleanup-rejected-probe-20260923/manifest.json`；执行结果见同目录 `receipt.json`。真实请求、配置、回执和来源文字保留。历史 SHA 不代表原图仍可读取，删除后的来源状态为 deleted_by_user_not_reverified。

下一步须处理原城 master 与已选底邻的局部几何接续；不要重复相同提示词刷图。没有更改共享五份 JSON，也没有处理宿主缓存。

---

以下是生图前准备记录，作为历史保留：

'''
    updated[texts[0]]=prefix.encode('utf-8')+before[texts[0]]
    readme='''# r08_c10 / r04_c02：拒选，原图与失败 QA 已删除

主任务亲看原像素拼接，确认花瓣位置和弧形边界有明显横断层，正式拒选。按最新用户保留规则，仅删除原生探片及本次生成的 3 张失败 QA 图；没有图片备份，未处理宿主缓存。

原图曾为原生 1254×1254 PNG，SHA `1129a25b56ca3d4946c27b38a88108c5700a3411371947cb1f2db7468233873c`。原像素观察保留为文本；图已删除，不能将历史观察当作现在的像素复验。

原生选用数 0，4096 候选 0，正式美术、导航、客户端验收均未通过。下一步先处理 master／已选底邻的局部几何接续，不重复同一提示词。

实际请求、四张参考 SHA、当次配置、真实回执和来源记录均保留。仅调用一次 builtin image_gen，clock 2026-09-23 12:59:25 UTC 至 13:00:53 UTC；实际型号／质量仍为 null。

删除 manifest、失败结论、原字节文字备份及执行回执位于 `cleanup-rejected-probe-20260923/`。活动索引 `handoff-probe.json` 已注明拒选删除；源图及失败 QA 的 exact path + SHA 可在 manifest 核对，状态为 deleted_by_user_not_reverified。
'''
    updated[texts[2]]=readme.encode('utf-8')
    for i,p in enumerate(texts):newfile(C/'text-after'/f'{i:02d}-{p.name}.after',updated[p])
    # CAS check all metadata using the already exclusive file handles.
    for p,f in text_handles.items():f.seek(0);assert f.read()==before[p],f'Concurrent text edit: {p}'
    receipt['status']='deleting_exact_verified_files'
    for p,f,h,row in image_handles:
        f.seek(0);assert sha(f.read())==row['sha256'],f'Image changed: {p}'
        flag=DISPOSITION(1)
        if not kernel.SetFileInformationByHandle(h,4,ctypes.byref(flag),ctypes.sizeof(flag)):raise ctypes.WinError(ctypes.get_last_error())
        f.close()
        assert not p.exists(),f'Deletion not completed: {p}'
        entry={**row,'deletedAtUtc':now(),'status':'deleted_by_user_not_reverified_after_cleanup'}
        receipt['deleted'].append(entry)
        with (C/'deleted-files.jsonl').open('a',encoding='utf-8') as log:log.write(json.dumps(entry,ensure_ascii=False)+'\n');log.flush();os.fsync(log.fileno())
    receipt['status']='updating_text_with_raw_byte_backup_and_cas'
    for p in texts:
        f=text_handles[p];f.seek(0);assert f.read()==before[p],f'Concurrent text edit at commit: {p}'
        f.seek(0);f.write(updated[p]);f.truncate();f.flush();os.fsync(f.fileno());f.seek(0);assert f.read()==updated[p]
        receipt['updatedText'].append({'file':str(p),'beforeSha256':sha(before[p]),'afterSha256':sha(updated[p])})
    for p,digest in preserved_before.items():assert sha(Path(p).read_bytes())==digest,f'Preserved record changed: {p}'
    for p,digest in images_untouched.items():assert sha(Path(p).read_bytes())==digest,f'Prepared reference changed: {p}'
    receipt.update(status='complete_exact_four_images_deleted_six_text_updates_verified',completedAtUtc=now(),deletedBytes=sum(r['bytes'] for r in receipt['deleted']),nativeSelectionCount=0,remainingNativePngCount=len(list((P/'native').glob('*.png'))),preservedRecordChecks=len(preserved_before),preservedPreparedImageChecks=len(images_untouched),manifest=manifestrec)
except BaseException as exc:
    receipt.update(status='failed_or_partial_inspect_receipt',error=repr(exc),failedAtUtc=now())
    raise
finally:
    for f in handles:
        if not f.closed:f.close()
    dump(C/'receipt.json',receipt)
print(json.dumps(receipt,ensure_ascii=False,indent=2))
