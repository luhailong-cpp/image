from pathlib import Path
from PIL import Image
import json
root=Path(r'E:\work\image\qdao_chibi_roster_v12');out=root/'review/he_xiangu_natural_walk';out.mkdir(parents=True,exist_ok=True)
p=root/'29_he_xiangu/source/idle-corrected.png';im=Image.open(p);cell=443;im.crop((0,cell,cell,cell*2)).save(out/'identity-reference-S.png')
status={'status':'art_revision_in_progress','reason':'root saw remaining high-knee marching and decorative short costume after positioning; user requested plain Taoist chibi and natural walking','preserve':'young He Xiangu identity, dark low bun, white lotus hair ornament, lotus identification, eight genuine walk frames per direction plus independent idle','planned_costume':'ivory cross-collar cloth robe, pale teal simple short over-robe, dark teal cloth sash, loose pale-green trousers and flat cloth shoes; small restrained lotus accessory; no glow','previous_candidate':'candidate-stable-body/29_he_xiangu has matched E/W idle and phase rotation but has NOT passed final movement/style visual review and is not published'}
(out/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
q=root/'candidate-stable-body/29_he_xiangu/qc.json';qc=json.loads(q.read_text());qc['visual_review']='requires_style_and_natural_gait_revision';qc['visual_review_findings']=['High knee/precontact marching remains in front/side intermediate phases; foot-only alignment cannot fix it.','Retain lotus identity and revise decorative short costume into plain white/teal cloth Taoist clothes matching explicit user direction.'];q.write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding='utf-8')
print('Preserved identity reference; candidate visual approval held for actual art revision')
