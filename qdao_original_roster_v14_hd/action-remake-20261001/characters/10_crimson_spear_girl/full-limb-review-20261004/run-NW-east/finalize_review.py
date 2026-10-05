from pathlib import Path
import json,hashlib
R=Path("D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl");D=R/'full-limb-review-20261004/run-NW-east'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((D/'frames.json').read_text(encoding='utf8'))
notes={
'02':'下杆/金尾已从支撑腿外侧移回上黑杆延长线；可见杆从裙前经过并遮住原低腿局部，两手和上杆未移动，原低腿支撑/高腿后屈保持。02-v1/v2仍偏右拒用。',
'03':'下杆由裙下出现，金尾位于低腿前方，黑杆与上段方向连续；双膝屈伸、两靴位置及双手保持。',
'05':'下杆位于裙下、高靴内侧，金尾部分被高靴遮挡，沿上黑杆延长方向；原低左靴支撑、高右靴回摆保持。',
'06':'下杆/金尾从高靴外侧移到内侧，消除原右偏；杆由裙口连续下降到金尾，高靴和低支撑靴姿态保持。06-v1仍偏右拒用。'
}
for f in rows:
 n=f['slot'].split('/')[-1]
 assert sha(R/f['original'])==f['originalSHA256'],'runtime changed'
 assert sha(R/f['selected'])==f['selectedSHA256'],'candidate changed'
 f.update(reviewStatus='passed',reviewMethod='actual native view plus fixed full-canvas before/after and fixed lower-limb crop; no source normalization by alpha bounds',notes=notes[n],globalTransform='none',handsAndUpperBody='preserved in static comparison',legSupportAndPose='preserved in static comparison',weaponAxis='accepted visual continuation of upper black shaft',runtimeModified=False)
 native=R/f['selected'];out=R/f['reviewExport']
 record={'file':f['reviewExport'],'sha256':sha(out),'operation':'whole-canvas LANCZOS resize 1254 to1024; no translation or alpha-bounds crop','source':f['selected'],'sourceSHA256':sha(native),'sourceRecord':str(native.relative_to(R))+'.generation.json','sourceRecordSHA256':sha(Path(str(native)+'.generation.json')),'reviewOnly':True}
 Path(str(out)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (native.parent/'review.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(D/'frames.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
selection={'slots':{f['slot']:f['selected'] for f in rows},'status':'accepted-after-current-local-static-review','review':'full-limb-review-20261004/run-NW-east/frames.json','frameMs':75,'runtimeModified':False}
(D/'selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report='NW02/03/05/06 下枪杆定点修复，当前静态接受四张：02-v3、03-v1、05-v1、06-v2。\n\n实际逐张查看原图、新原生1254全图以及固定1024画布前后对比和下肢放大；没有按脚底对齐、没有技术注册、没有生成重复运动帧。新图仅全画布缩至1024供预览，正式发布仍由根代理执行。\n\n'
for n in notes:report+='- '+n+'：'+notes[n]+'\n'
report+='\n透明1254原生、逐图prompt/request/receipt/configSnapshot/input SHA和来源记录齐全；实际model/quality保持null，未声称工具锁定配置目标。所有四张原runtime SHA复查一致。每个连续接地点两张独立姿态与75ms节奏不变。02新杆可见遮挡跨度比原图增加，是恢复直杆投影后位于裙前，须在根代理相邻播放中一并看遮挡连续性。\n'
(D/'REVIEW.md').write_text(report,encoding='utf8')
print(json.dumps(selection,ensure_ascii=False))

