from pathlib import Path
import json,hashlib
root=Path(r'E:\work\image\qdao_chibi_roster_v12');e=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\eight-natural-current-code-20260916-retry')
for filename in ['README.md','CLIENT_CONTRACT.md','review/record_final_preview_delivery.py']:
 p=root/filename;t=p.read_text(encoding='utf-8').replace('及 8 张行走条带，共 648 张 PNG','及 8 张行走条带，每人 81 张、八人共 648 张 PNG').replace('八张主城截图已逐一视审','八人主城外观已逐一视审');p.write_text(t,encoding='utf-8')
p=root/'review/site/delivery-status.json';x=json.loads(p.read_text(encoding='utf-8'));v=e/'root-visual-runtime-review.json';r=json.loads(v.read_text());assert r['status']=='passed' and len(r['reviewed_character_ids'])==8;x['root_city_visual_review_evidence']=str(v);x['root_city_visual_review_sha256']=hashlib.sha256(v.read_bytes()).hexdigest();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Verified root city review and clarified per-character versus roster totals')
