import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'runtime/run/E/15.png'; new=ROOT/'runtime/run/E/14.png'
assert old.is_file() and not new.exists()
old.rename(new)
a=old.with_name(old.name+'.generation.json'); b=new.with_name(new.name+'.generation.json')
r=json.loads(a.read_text(encoding='utf-8')); r['file']='runtime/run/E/14.png';r['visualReview']='按实际姿态重排入E14：右足前伸准备落地、左牌前右杖后。原请求E07、曾暂选E15；新E14请求返回更接近触地，安排至E15以接E00。完整动态待复审。'
b.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');a.unlink()
p=ROOT/'work/run_E_07_v2.png.generation.json';r=json.loads(p.read_text(encoding='utf-8'));r['exportPath']='runtime/run/E/14.png';r['visualReview']='实际姿态选入E14候选：右足前伸准备落地、前左牌后右杖；原生成请求E07，选帧重排按实际姿态如实记录。';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Reassigned independent source run_E_07_v2 to E14; E15 now empty.')

