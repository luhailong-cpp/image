from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
d=json.loads((OUT/'revisions.json').read_text(encoding='utf-8'))
base={r['id']:r for name in ['client_designs','supplement'] for r in json.loads((OUT/f'{name}-findings.json').read_text(encoding='utf-8'))['records']}
rows=[]
resolved={'X0005','X0008','X0010','X0011','X0015','X0019','X0028','X0029'}
for r in d['records']:
    if r['id'] not in base:continue
    a=dict(base[r['id']]);a['revision_sha256']=r['sha256'];a['rechecked']=True
    if r['id'] in resolved:
        a.update(verdict='match',reason='审查期间新版本已修复前次问题：独立边界/卡片残线/头像取景/透明标题按对应单件得到整理；当前联系表复核符合深玉细金方向。',action='保留新版本；旧缩略图仅作过程对照。',issue_tags=['resolved-during-audit'])
    elif r['id'] in {'A0286','A0287'}:
        a.update(verdict='match',reason='属性界面截图已改用v2-painted深玉绿标题、米白纸面和细金边，前次亮绿厚框版本被替换；当前属性窗口与用户参考更一致。',action='保留新属性皮肤，后续核对小切片局部质量。',issue_tags=['resolved-during-audit'])
    elif r['id']=='A0291':
        a.update(verdict='deviates',reason='当前结算截图按钮已改为带云饰绿钮，但大面积深棕木纹主面板仍与已确认米白纸面/深玉标题风格不同。',action='保留按钮改进，将结算主面板统一为同一皮肤。',issue_tags=['legacy-result-panel','screenshot-evidence'])
    elif r['id']=='X0012':
        a.update(verdict='minor',reason='头像框已去掉厚绿直线块，但左侧角饰/上边仍有细小断续和残点；细金框整体方向正确。',action='只清理角接残点和线条连续性。',issue_tags=['cutout-reconstruction'])
    elif r['id']=='X0027':
        a.update(verdict='minor',reason='选中竖页签保持深玉金边，但去字区仍可见重复的深绿水平条和局部矩形接补。',action='从连续无字玉纹重建内芯，保留边饰。',issue_tags=['cutout-reconstruction','banding'])
    elif r['id']=='X0026':
        a.update(verdict='match',reason='竖页签纸面、细金线及侧边连接符合对应布局，当前去字版整体连贯。',action='保留；按侧边页签用途使用。',issue_tags=[])
    elif r['id']=='X0031':
        a.update(verdict='match',reason='新版米白纸面、细金线和局部角饰接近参考；已去除多余背景角块。',action='保留框板。',issue_tags=[])
    rows.append(a)
(OUT/'revision-client-findings.json').write_text(json.dumps({'owner':'revision-client','reviewed_pages':['contacts/revisions/01.jpg','contacts/revisions/02.jpg'],'records':rows,'resolved_ids':sorted(resolved|{'A0286','A0287'}),'notes':['只覆盖32张变动文件中的21张客户端/属性图，其余11张正式人物由人物审查代理复核。','本文件覆盖对应原ID旧判断；未被改动的旧像素副本继续保留原判断。']},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(rows))
