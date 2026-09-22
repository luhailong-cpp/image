"""Keep review-set-v2 selections, replacing only NW15 with root-selected pose-v3."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
source=HERE/'selections-review-set-v2.json'
selection=json.loads(source.read_text(encoding='utf-8'))
key='walk/NW/15.png'
expected='30f6e596a78df07994d9431ea1ac815873a183aa3c63cb1634fd6a87edcef96a'
path=Path(selection['overrides'][key]['path'])
assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
selection['overrides'][key].update(sha256=expected,selected_revision='NW15-pose-v3',visual_status='root_selected_unapproved')
selection['expected_sources'][key]['sha256']=expected
selection['known_rework_slots']=[]
selection['review_notes']={key:'已换为 NW15-pose-v3，仍待完整循环与素材验收。','walk/SW/16.png':'SW16-pose-v3 静态接缝改善；15→16 主体高度上升22px，待动态检查起伏。原图主体占高92.5%，未完全符合89%提示目标，未裁切。'}
selection['selection_evidence']['supersedes_selection_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
selection['selection_evidence']['root_instruction']='Keep all review-set-v2 selections except NW15, use exact NW15-pose-v3 PNG SHA; approval remains pending.'
dest=HERE/'selections-review-set-v3.json'
assert not dest.exists()
dest.write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(dest)
