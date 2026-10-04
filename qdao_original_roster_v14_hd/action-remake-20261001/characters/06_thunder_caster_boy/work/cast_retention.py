import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
audit=json.loads((ROOT/'review/cast_audit_20261003.json').read_text(encoding='utf-8'))
assert len(audit['frames'])==32
current={}
for fr in audit['frames']:
 p=ROOT/fr['file'];assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==fr['sha256']
 r=json.loads((ROOT/fr['generationRecord']).read_text(encoding='utf-8'))
 for src in r['derivedFrom']:
  nr=ROOT/src['generationRecord'];assert nr.exists()
  current[(ROOT/src['file']).resolve()]=fr
targets=list((ROOT/'work').glob('cast_*.png'))
removed=[]
for p in targets:
 p=p.resolve()
 assert p.is_relative_to((ROOT/'work').resolve()) and p.name.startswith('cast_')
 rp=p.with_name(p.name+'.generation.json')
 assert rp.exists(),p
 r=json.loads(rp.read_text(encoding='utf-8'))
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 if p in current:
  fr=current[p];reason='已导出正式runtime且SHA/逐图记录验证齐全；按用户仅保留最终图片要求删除原生加工副本'
  retained={'file':fr['file'],'sha256':fr['sha256'],'generationRecord':fr['generationRecord']}
 elif p.name=='cast_E_09_v1.png':
  reason='已被E09v3重画替代的拒稿，手臂归属风险；保留文本哈希与被引用历史';retained={'file':'runtime/cast/E/09.png'}
 else:raise ValueError('unreviewed work image '+str(p))
 r['retention']={'imageRemoved':True,'at':now,'reason':reason,'retainedArtifact':retained,'nativeMetadataAndSourceEvidencePreserved':True}
 rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 p.unlink()
 removed.append({'file':p.relative_to(ROOT).as_posix(),'sha256':r['sha256'],'generationRecord':rp.relative_to(ROOT).as_posix(),'reason':reason})
removed_paths={str((ROOT/x['file']).resolve()).lower() for x in removed}
for rp in (ROOT/'work').glob('cast_*.png.generation.json'):
 r=json.loads(rp.read_text(encoding='utf-8'));changed=False
 for ref in r.get('references',[]):
  p=Path(ref['path']).resolve()
  if str(p).lower() in removed_paths:
   ref['historicalSourceRetention']='原参考图生成时存在并传入，后已按用户保留规则删除；记录中的原始SHA及来源generation.json保留，不改写为后继图'
   changed=True
 if changed:rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'records/cast_retention_20261003.json').write_text(json.dumps({'at':now,'scope':'character work/cast_*.png only','removedImages':removed,'formalFrameCountRetained':32,'note':'宿主generated_images不在本角色写入边界，未操作；原生实际尺寸/C2PA摘录/原始SHA仍保存在逐图文字记录'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'removed':len(removed),'remainingWorkCastImages':len(list((ROOT/'work').glob('cast_*.png'))),'runtimeCast':len(list((ROOT/'runtime/cast').glob('*/*.png')))},ensure_ascii=False))
