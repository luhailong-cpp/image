from pathlib import Path
import hashlib,json,datetime,sys
S=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(S/'continuation-20260923/checkpoint-merge'))
from merge_checkpoint import WinLockedFile
T=S/'next_tile_r08_c07'
now=datetime.datetime.now(datetime.timezone.utc)
out=T/'continuation-20260923'/('handoff-update-'+now.strftime('%Y%m%dT%H%M%S%fZ'))
out.mkdir()
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(o):return (json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()
sel=T/'latest-candidate.json'
cleanup=T/'continuation-20260923/cleanup-selected-c07/receipt.json'
refs={'selection':{'file':'latest-candidate.json','sha256':sha(sel.read_bytes())},'cleanup':{'file':cleanup.relative_to(T).as_posix(),'sha256':sha(cleanup.read_bytes())}}
paths=[T/'handoff-state.json',T/'HANDOFF.md']
before={p:p.read_bytes() for p in paths}
for p,b in before.items():(out/(p.name+'.before')).write_bytes(b)
d=json.loads(before[paths[0]].decode('utf-8-sig'))
d.setdefault('historicalCheckpoints',[]).append({'file':(out/(paths[0].name+'.before')).relative_to(T).as_posix(),'sha256':sha(before[paths[0]]),'meaning':'Previous frozen handoff, not current counts'})
d.update(updatedAtUtc=now.isoformat(),status='selected_4096_candidate_partial_local_review_not_production_accepted',compiledBy='root current disk and exact SHA review',selectedPatchCount=16,targetPatchCount=16,retainedNativePngCountIncludingRejected=0,currentCandidate=refs['selection'],currentRetention=refs['cleanup'],selectedPatchCountMeaning='16 historical native detail inputs exported into current candidate; source PNGs retired after verified export',selectedPatchesMeaning='Historical source provenance preserved; these source bytes were deleted under current user retention policy',formalArtAcceptancePassed=False,clientRuntimeAccepted=False)
prefix='''> **2026-09-23 当前状态：已补齐并选用 4096² 候选。** 读取 [latest-candidate.json](latest-candidate.json) 的路径及 SHA，不再按下方旧 9/16 进度重做。16 个块内原像素区域、6 条内部完整缝、9 个内部交点和底边已检查；另 3 条外边、4 个外部四块交点、整城布局/导航及客户端实机仍未通过，正式验收为 0。
>
> 当前采用 repaired-v1，PNG SHA `7e60bc705c1b750cad18bffa9f486f7be680835c1ee3bf0f692f0202325699e6`。按用户新保留规则，已核对导出与当前引用后删除 115 个原图/旧过程文件（166632257 字节），无图片备份；保留 12 张选用图、必要设计和同版本验收证据。历史模型/请求/回执/来源 SHA 文本保留，删除来源不可再声称当前字节复验。见 [清理回执](continuation-20260923/cleanup-selected-c07/receipt.json)。
>
> **下方是保留的旧交接历史。**

'''
after={paths[0]:enc(d),paths[1]:prefix.encode()+before[paths[1]]}
locks=[];committed=[]
try:
    for p in paths:locks.append((p,WinLockedFile(p,True)))
    for p,l in locks:assert l.read()==before[p],f'Concurrent edit: {p}'
    for p,l in locks:
        l.write(after[p]);assert l.read()==after[p];committed.append(str(p))
finally:
    (out/'receipt.json').write_bytes(enc({'updatedAtUtc':now.isoformat(),'committed':committed,'beforeSha':{p.name:sha(b) for p,b in before.items()},'afterSha':{p.name:sha(b) for p,b in after.items()}}))
    for _,l in reversed(locks):l.close()
print(json.dumps({'backupAndReceipt':str(out),'updated':committed}))
