"""Root's final visual review of the four added pages and eleven replacement portraits."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
s=json.loads((OUT/'supplement.json').read_text(encoding='utf-8'))
rows=[]
for r in s['records']:
    n=int(r['id'][1:])
    if not 48<=n<=111:continue
    if n==48 or n>=105:
        verdict='technical';reason='已实看新增Unity切片排布或曝光前后比较图；属于验证/审查排布，不作为独立正式美术。';action='保留审查用途。';tags=['review-sheet']
    elif n==49:
        verdict='minor';reason='吊穗已单独拆出，与原暖金红穗风格一致；顶端仍带窄矩形背景片，需按实际连接位置处理。';action='贴到关闭按钮时复核顶端接缝，必要时清理残底。';tags=['cutout-contamination']
    else:
        verdict='historical';reason='v9人物多样化来源/处理副本，已在联系表查看。身形、脸型、年龄感和职业配色变化属于该版本设计方向；洋红母底和过程GIF不当作正式切图失败。';action='保留来源身份，以相应正式PNG为交付；同屏统一尺寸与地面锚点。';tags=['v9-source','not-final-asset']
    rows.append({'id':r['id'],'verdict':verdict,'reason':reason,'action':action,'issue_tags':tags})
(OUT/'supplement-extra-findings.json').write_text(json.dumps({'owner':'supplement-extra','reviewed_pages':[f'contacts/supplement/{i:02d}.jpg' for i in range(4,8)],'records':rows,'findings':[],'notes':['root实际查看全部4页：64个新增独立内容。仅审阅本补扫快照，不延伸至并行任务之后的新文件。']},ensure_ascii=False,indent=2),encoding='utf-8')
revisions=json.loads((OUT/'revisions.json').read_text(encoding='utf-8'))
rows=[]
for r in revisions['records']:
    if not r['path'].startswith('q_daoist_character_pack_4096/'):continue
    verdict='match';tags=['v9-diversity','revised-current']
    reason='当前正式人物已替换为v9差异化造型。面孔、身形与年龄感更有区分，仍保留Q版头身、道家服饰/法器和细腻手绘材质。不能将其误判为旧版人物或要求全部变回同脸道童。'
    action='保留差异化身份，后续在同一选角场景统一人物占屏尺寸与锚点；确认客户端prepared副本同步到正确版本。'
    if r['id'] in {'A0515','A0521'}:
        verdict='minor';tags+=['proportion-review','hard-shading']
        reason='v9刺客/风刃造型更修长、脸部和发丝的动漫硬边更明显；职业差异合理，但同屏与圆润道童相比呈现更成熟且更锐的画法。'
        action='保留身形差异和身份；只在同屏比较后适度统一光影柔和度与人物占屏尺度，不强制改为同脸短胖比例。'
    rows.append({'id':r['id'],'verdict':verdict,'reason':reason,'action':action,'issue_tags':tags,'revision_sha256':r['sha256'],'rechecked':True})
(OUT/'revision-actors-findings.json').write_text(json.dumps({'owner':'revision-actors','reviewed_pages':['contacts/revisions/02.jpg'],'records':rows,'findings':[],'notes':['root实际查看11张变动后的正式人物联系表并与相应v9来源页交叉核对。旧版冰剑和水龙的判断不沿用于已经被覆盖的新画。']},ensure_ascii=False,indent=2),encoding='utf-8')
print({'supplement_extra':64,'revision_actors':len(rows)})
