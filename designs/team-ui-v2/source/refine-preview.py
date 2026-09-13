from pathlib import Path
import re,json,shutil,hashlib
root=Path('E:/work/image'); d=root/'designs/team-ui-v2'
for src,dest in [('qdao_chibi_game_pack_v4/hero-transparent_1024.png','hero-headband.png'),('q_daoist_character_pack_4096/03_lotus_healer_girl_transparent_4096.png','lotus-healer.png')]:
    shutil.copyfile(root/src,d/'assets'/dest)
    manifest=json.loads((d/'asset-manifest.json').read_text(encoding='utf-8-sig'))
    manifest['assets'].append({'file':'assets/'+dest,'source':src,'sha256':hashlib.sha256((d/'assets'/dest).read_bytes()).hexdigest(),'copiedWithoutModification':True})
    (d/'asset-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
p=d/'app.js'; s=p.read_text(encoding='utf-8-sig')
s=s.replace('const portraits = ["24_lu_dongbin", "29_he_xiangu", "30_han_xiangzi", "25_lion_drum_guard", "27_ink_kite_ranger"];','const portraits = ["hero-headband", "29_he_xiangu", "24_lu_dongbin", "lotus-healer", "27_ink_kite_ranger"];')
s=s.replace('level:85,school:"剑修"','level:28,school:"道童"').replace('level:82,school:"丹修"','level:26,school:"灵修"').replace('level:84,school:"法修"','level:30,school:"剑修"').replace('level:80,school:"体修"','level:27,school:"医师"').replace('level:83,school:"剑修"','level:29,school:"符师"')
s=re.sub(r'(<button id="approve-[\s\S]*?</button>)(<button id="reject-[\s\S]*?</button>)',r'\2\1',s)
s=s.replace('虚位以待','空余席位')
p.write_text(s,encoding='utf-8')
p=d/'index.html'; s=p.read_text(encoding='utf-8-sig').replace('入队申请 <span','申请列表 <span').replace('<summary>演示状态</summary>','<summary>示例数据 · 演示状态</summary>');p.write_text(s,encoding='utf-8')
p=d/'styles.css'; s=p.read_text(encoding='utf-8-sig'); s+='''
/* Clarity pass: body stays readable after the 2560-wide canvas is scaled. */
.section-subtitle,.application-footnote{display:none}
@media(min-width:901px){
.section-heading{height:70px}.section-heading h2{font-size:40px}
.member-row{height:92px;grid-template-columns:82px minmax(0,1fr) 100px 100px 110px}.avatar{width:76px;height:76px}
.member-name{font-size:36px;line-height:1.1}.role-tag{font-size:24px;line-height:1.2;margin-top:5px}.self-tag{font-size:22px;line-height:28px}
.member-level,.member-school{font-size:30px}.online-state{font-size:28px}.member-row.empty{grid-template-columns:82px 1fr auto}.empty-name{font:30px var(--sans);color:#746950}.empty-detail{font-size:24px;color:#746950}
.application-card{grid-template-columns:102px minmax(0,1fr);padding:20px}.application-card .avatar{width:96px;height:96px}.application-name{font-size:36px}.application-details{font-size:28px}.application-actions{gap:18px}.application-actions .button{height:64px;min-width:176px;font:30px var(--sans);letter-spacing:2px}
.status-message{font-size:28px}.refresh-button{height:62px;font:30px var(--sans)}
.applications-section.has-pagination .application-card{grid-template-columns:78px minmax(0,1fr) 200px;padding:12px 15px}.applications-section.has-pagination .application-card .avatar{width:72px;height:72px}.applications-section.has-pagination .application-name{font-size:29px}.applications-section.has-pagination .application-details{font-size:24px}.applications-section.has-pagination .button{min-width:96px;height:52px;font-size:25px;padding:0 10px}.applications-section.has-pagination .application-actions{gap:6px}
.members-section.has-pagination .member-row{height:82px}.members-section.has-pagination .avatar{width:65px;height:65px}.members-section.has-pagination .member-name{font-size:32px}.members-section.has-pagination .role-tag{font-size:21px}
.pagination button{min-height:44px}.pagination{font-size:24px}
}
@media(max-width:900px){.section-heading{height:48px}.demo-controls{position:relative;left:auto;bottom:auto;margin:0 12px 20px;max-width:none}.application-actions .button{font-family:var(--sans);font-size:20px}.close-button{width:44px;height:44px}.refresh-button{height:44px}.pagination button{min-height:44px}.applications-section.has-pagination .button{height:44px}.demo-controls button{min-height:44px}.empty-name{font-family:var(--sans);font-size:18px;color:#746950}.empty-detail{color:#746950}}
''';p.write_text(s,encoding='utf-8')
