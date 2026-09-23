"""Bounded Windows-exclusive cleanup of second rejected probe: 5 exact PNGs."""
from pathlib import Path
from datetime import datetime,timezone
import ctypes,json,hashlib,os,msvcrt,stat
from ctypes import wintypes
D=Path(__file__).resolve().parent;P=D.parent;B=D/'probe-aligned-halo-v2';C=B/'cleanup-rejected-20260923'
assert os.name=='nt'
def now():return datetime.now(timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(o):return (json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def newfile(p,b):
 with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def dump(p,o):newfile(p,enc(o))
def rec(p):return {'file':str(p),'sha256':sha(p.read_bytes())}
expected={
 B/'native-r04_c02.png':'7e5a69ee7aff3bf34aa6f3f0b83b22907fcd8b4f13149ac97279cb6d6f096a37',
 B/'qa/halo-comparison-generated-top-neighbor-bottom.png':'75997b8b6e40af9505adf57a01e6182979a036e1b34afe8b3f9c322c14cbb13e',
 B/'qa/hypothetical-core-to-bottom-seam-native.png':'8a38c4126a23f5cc17105f08348c33f8e81c99a84e84dc5d7ad958007dfccbc0',
 B/'qa/generated-y1139-context-native.png':'5f8d896cf72fcfd3cc79bc5a10e3f83d4b069055033dad4477b776c925f5b787',
 B/'qa/right-band-originals-v-output.png':'8b512ed50a737c5c9dfe1f72d610d8385495dcfb0f798d1447a40dbf58fe9047'}
texts=[P/'HANDOFF.md',B/'handoff.json',B/'README.md',B/'native-r04_c02.png.generation.json',B/'local-review.json',B/'qa/derived-review-images.json',B/'qa/right-band-originals-v-output.derived.json']
preserve=[B/n for n in ['actual-request.json','actual-prompt.txt','config-snapshot.json','tool-receipt.json','preflight.json','static-layout-observation.json','registered-reference-only.derived.json','calibration-proposal.json']]+[D/'audit.json',P/'plan.json',P/'layout-record.json']
def safe(p):
 resolved=p.resolve(strict=True);assert resolved.is_relative_to(P.resolve()) and resolved!=P.resolve(),str(p)
 assert resolved==p.absolute(),f'Alias: {p}'
 q=p
 while True:
  assert not (getattr(q.stat(follow_symlinks=False),'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT),f'Reparse: {q}'
  if q==P:break
  q=q.parent
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE];kernel.CreateFileW.restype=wintypes.HANDLE
kernel.SetFileInformationByHandle.argtypes=[wintypes.HANDLE,ctypes.c_int,wintypes.LPVOID,wintypes.DWORD];kernel.SetFileInformationByHandle.restype=wintypes.BOOL
kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
class DISPOSITION(ctypes.Structure):_fields_=[('DeleteFile',wintypes.BOOLEAN)]
def locked(p,access,mode):
 safe(p);h=kernel.CreateFileW(str(p),access,0,None,3,0x80,None)
 if h==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
 try:return os.fdopen(msvcrt.open_osfhandle(int(h),os.O_BINARY|(os.O_RDWR if '+' in mode else os.O_RDONLY)),mode),h
 except Exception:kernel.CloseHandle(h);raise
assert not C.exists(),'Do not rerun cleanup'
for p in [*expected,*texts,*preserve]:safe(p)
C.mkdir();(C/'text-before').mkdir();(C/'text-after').mkdir()
receipt={'startedAtUtc':now(),'status':'preflight','deleted':[],'updatedText':[],'imageBackupsMade':False,'sharedJSONWritten':False,'hostCacheTouched':False,'oldImagesRestored':False}
handles=[]
try:
 image_handles=[];rows=[];before={};text_handles={}
 for p,digest in expected.items():
  f,h=locked(p,0x80000000|0x00010000,'rb');handles.append(f);raw=f.read();assert sha(raw)==digest,f'SHA changed: {p}'
  row={'file':str(p),'sha256':digest,'bytes':len(raw),'action':'delete_root_rejected_v2_probe_or_its_failed_qa','safeRoot':str(B)}
  assert p.resolve().is_relative_to(B.resolve());rows.append(row);image_handles.append((p,f,h,row))
 for i,p in enumerate(texts):
  f,h=locked(p,0x80000000|0x40000000,'r+b');handles.append(f);raw=f.read();before[p]=raw;text_handles[p]=f
  newfile(C/'text-before'/f'{i:02d}-{p.name}.before',raw)
 preserved={str(p):sha(p.read_bytes()) for p in preserve}
 preserved_images={str(p):sha(p.read_bytes()) for p in P.rglob('*.png') if p not in expected}
 failure={'recordedAtUtc':now(),'authority':'Root explicit rejection of second controlled-halo probe','reason':'Invented transverse beveled joint absent from original master/plaza, and floral contours displaced at the actual lower-tile contact. Correct halo placement did not ensure native continuation.','failedNative':rows[0],'boundaryGlobalY':32768,'flowerGlobalXRegion':[37773,38423],'falseJointGlobalInspectLTRB':[38723,32629,39027,32829],'selectedNativeCount':0,'nextAction':'Local contour/control-point calibration required; preserve current alignment/reference design and calibration-proposal text; do not rerun same prompt.'}
 dump(C/'failure-conclusion.json',failure)
 manifest={'schemaVersion':1,'plannedAtUtc':now(),'authorization':'User retention policy plus root explicit bounded cleanup instruction','safeRoot':str(B),'files':rows,'totalBytes':sum(r['bytes'] for r in rows),'imageBackupsMade':False,'hostCacheTouched':False,'sharedJSONWritten':False,'failureConclusion':rec(C/'failure-conclusion.json'),'textBackups':[{'file':str(p),'sha256':sha(before[p]),'backup':str(C/'text-before'/f'{i:02d}-{p.name}.before')} for i,p in enumerate(texts)]}
 dump(C/'manifest.json',manifest);manifestrec=rec(C/'manifest.json')
 disposal={'status':'root_rejected_native_and_failed_qa_deleted','recordedAtUtc':now(),'manifest':manifestrec,'failureConclusion':rec(C/'failure-conclusion.json'),'currentSourceStatus':'deleted_by_user_not_reverified_after_cleanup','selectedNativeCount':0}
 gen=json.loads(before[texts[3]].decode('utf-8-sig'));gen['currentFileState']='deleted_by_user_not_reverified_after_cleanup';gen['disposition']=disposal;gen['selected']=False
 review=json.loads(before[texts[4]].decode('utf-8-sig'));review['historicalRetentionAtReview']=review.get('retention');review['retention']='Root rejected; workspace native probe and its4 failedQA images deleted. Source SHA, request, receipt, current designs and calibration text retained.';review['disposition']=disposal;review['rootRejected']=True
 for item in [review['native'],*review['viewedQA'],review['additionalQAForRoot']]:item['currentFileState']='deleted_by_user_not_reverified_after_cleanup'
 derived=json.loads(before[texts[5]].decode('utf-8-sig'));derived['disposition']=disposal
 for entry in derived['entries']:entry['image']['currentFileState']='deleted_by_user_not_reverified_after_cleanup'
 side=json.loads(before[texts[6]].decode('utf-8-sig'));side['output']['currentFileState']='deleted_by_user_not_reverified_after_cleanup';side['disposition']=disposal
 updated={texts[3]:enc(gen),texts[4]:enc(review),texts[5]:enc(derived),texts[6]:enc(side)}
 hand=json.loads(before[texts[1]].decode('utf-8-sig'));hand['status']='root_rejected_original_and_failed_qa_deleted';hand['image']['currentFileState']='deleted_by_user_not_reverified_after_cleanup';hand['disposition']=disposal
 hand['generationRecord']['sha256']=sha(updated[texts[3]]);hand['localReview']['sha256']=sha(updated[texts[4]]);hand['selectedNativeCount']=0;hand['stopped']=True
 updated[texts[1]]=enc(hand)
 prefix='''# 最新状态：第二次对齐探片拒选，原图与失败 QA 已清理

2026-09-23 主任务确认：正确贴入 y1139..1254 的底邻 halo 后，输出仍有花瓣错位，并新增原城没有的横向倒角砖缝，因此第二次探片拒选。仅删除 `alignment-20260923T132520Z/probe-aligned-halo-v2/` 本轮原生图及 4 张失败 QA；无图片备份。

当前 c10 选用 native=0，完整 4096 候选=0，正式验收=0。真实请求／配置／回执、来源 SHA、原字节文字备份与拒选结论保留；删除清单和执行回执见 `alignment-20260923T132520Z/probe-aligned-halo-v2/cleanup-rejected-20260923/`。已删来源状态为 deleted_by_user_not_reverified，不能按历史观察声称现在仍可复验像素。

当前布局、共享 halo 对照和 registered-reference-only 设计输入保留。下一步以 `alignment-20260923T132520Z/probe-aligned-halo-v2/calibration-proposal.json` 的浮雕轮廓／控制点校准方案为准，先解决局部几何接续，不重复同一提示词。未恢复旧图，未写共享五 JSON，未改导航和宿主缓存。

---

以下为此前交接记录，按历史保留：

'''
 updated[texts[0]]=prefix.encode('utf-8')+before[texts[0]]
 updated[texts[2]]='''# r08_c10 / r04_c02 对齐试验：root 拒选，原图已退役删除

第二次试验仅一次 builtin 调用，曾生成原生 1254×1254 PNG，SHA `7e5a69ee7aff3bf34aa6f3f0b83b22907fcd8b4f13149ac97279cb6d6f096a37`。正确 halo 对齐仍出现花瓣错位，以及 master／plaza 均不存在的横向倒角砖缝。主任务确认拒选。

本轮原图和 4 张失败 QA 已逐文件核 exact path、SHA 和安全根并删除，没有图片备份。当前选用 native=0。历史逐图型号／请求／来源文字、真实回执与失败结论保留；删除后状态为 deleted_by_user_not_reverified，不等于当前像素已复验。

`registered-reference-only.png`、上层共享 halo 对照和当前几何／风格参考保留，均是设计输入而非成品。`calibration-proposal.json` 保留为后续局部控制点校准方案，不授权重复原提示词刷图。

逐图记录 `native-r04_c02.png.generation.json` 与 `handoff.json` 已标退役。删除 manifest、原字节文字备份和 receipt 位于 `cleanup-rejected-20260923/`。无共享 JSON、导航或宿主缓存修改，未恢复旧失败图片。实际型号／质量仍为 null。
'''.encode('utf-8')
 for i,p in enumerate(texts):newfile(C/'text-after'/f'{i:02d}-{p.name}.after',updated[p])
 for p,f in text_handles.items():f.seek(0);assert f.read()==before[p],f'CAS precheck failed:{p}'
 receipt['status']='deleting_verified_exact_files'
 for p,f,h,row in image_handles:
  f.seek(0);assert sha(f.read())==row['sha256'],f'Image SHA changed:{p}'
  flag=DISPOSITION(1)
  if not kernel.SetFileInformationByHandle(h,4,ctypes.byref(flag),ctypes.sizeof(flag)):raise ctypes.WinError(ctypes.get_last_error())
  f.close();assert not p.exists(),f'Deletion incomplete:{p}'
  entry={**row,'deletedAtUtc':now(),'status':'deleted_by_user_not_reverified_after_cleanup'};receipt['deleted'].append(entry)
  with (C/'deleted-files.jsonl').open('a',encoding='utf-8') as log:log.write(json.dumps(entry,ensure_ascii=False)+'\n');log.flush();os.fsync(log.fileno())
 receipt['status']='updating_text_with_byte_backup_cas'
 for p in texts:
  f=text_handles[p];f.seek(0);assert f.read()==before[p],f'CAS writecheck failed:{p}'
  f.seek(0);f.write(updated[p]);f.truncate();f.flush();os.fsync(f.fileno());f.seek(0);assert f.read()==updated[p]
  receipt['updatedText'].append({'file':str(p),'beforeSha256':sha(before[p]),'afterSha256':sha(updated[p])})
 for p,digest in preserved.items():assert sha(Path(p).read_bytes())==digest,f'Preserved text changed:{p}'
 for p,digest in preserved_images.items():assert sha(Path(p).read_bytes())==digest,f'Preserved reference changed:{p}'
 receipt.update(status='complete_exact_five_images_deleted_seven_text_updates_verified',completedAtUtc=now(),deletedBytes=sum(r['bytes'] for r in rows),selectedNativeCount=0,preservedTextChecks=len(preserved),preservedDesignImageChecks=len(preserved_images),manifest=manifestrec)
except BaseException as exc:
 receipt.update(status='failed_or_partial_inspect_receipt',error=repr(exc),failedAtUtc=now());raise
finally:
 for f in handles:
  if not f.closed:f.close()
 dump(C/'receipt.json',receipt)
print(json.dumps(receipt,ensure_ascii=False,indent=2))
