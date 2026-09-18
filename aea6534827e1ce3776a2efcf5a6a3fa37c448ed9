from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
root=Path(r'E:\work\image\qdao_original_roster_v13');out=root/'candidate/00_reference_topright_boy';review=root/'review/00_reference_topright_boy'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((out/'manifest.json').read_text(encoding='utf-8-sig'));q=json.loads((out/'qc.json').read_text(encoding='utf-8-sig'))
notes=json.loads((review/'final-notes-by-direction.json').read_text(encoding='utf-8-sig'))
files=[out/'review'/f'{d}-contact.png' for d in notes]
files+=[review/f'{d}-full-contact.jpg' for d in notes]
files+=sorted(p for p in (review/'browser-final-candidate').iterdir() if p.suffix.lower() in ['.png','.jpg','.json'])
files+=[review/'all-eight-directions-normal.gif',review/'all-eight-directions-half-speed.gif',review/'animated-review-provenance.json']
data={'status':'passed','reviewer':'extra_character actual source/contact/browser inspection; root independent final mutual review incorporated','reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'reviewed_input_manifest_sha256':sha(out/'manifest.json'),'reviewed_input_qc_sha256':sha(out/'qc.json'),'reviewed_artifacts':{x['path']:x['sha256'] for x in m['files']},'reviewed_directions':list(notes),'notes_by_direction':notes,'normal_size_review':True,'enlarged_review':True,'seam_15_16_01_review':True,'anatomical_contacts_01_09_review':True,'inspection_method':'Actual real-source cells and all16 contact sheets visually inspected; actual Edge browser captures at normal and enlarged canvas sizes, enlarged01/05/09/13 and15/16/01 boards inspected. Live requestAnimationFrame timing and UI controls measured by Playwright; no claim of recorded video viewing. Every final resource response SHA matched current manifest in browser-sequence-report. Earlier numeric validation before W03 is explicitly archived and not final evidence.','mutual_review_notes':'Root independently approved repaired NE size/phase, N11, NW1/9/10/12/14, E6/12, SW3/15, then final W03 and SE13 on current full-contact files. Final seal only occurs after these repairs.','evidence':[{'path':str(p),'sha256':sha(p)} for p in files]}
dest=out/'review/fresh-review-input.json';dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
working='# 00 道童最终视觉检查记录\n\n128张新实绘行走 + 8独立站立 + 8 strip + 保留原版肖像，共145PNG。每帧30ms、16帧480ms；仅同一common_scale=0.88。root互审要求的所有定点修复已完成；未用镜像/变形/重复旧图造新动作。\n\n'+'\n\n'.join(f'- {d}：{n}' for d,n in notes.items())+'\n\n浏览器：41项行为检查通过；最终136资源响应SHA匹配，256张normal/large实际canvas截图。不是Unity运行证据。W03修复前的数字验证归档为validation-before-W03-20260917T1250.json，不用于最终发布。\n\n最终视觉输入 candidate/00_reference_topright_boy/review/fresh-review-input.json 绑定当前145PNG、manifest、qc及全部审阅证据；封存由approve.py重新全量重建两次。等待该命令成功后才报告passed。\n'
(review/'visual-review-working.md').write_text(working,encoding='utf-8')
print(json.dumps({'fresh_review':str(dest),'evidence_count':len(files),'manifest_sha256':data['reviewed_input_manifest_sha256'],'pngs':len(m['files'])}))
