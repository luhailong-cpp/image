from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image
ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
OUT=(ROOT/'r09_c08/early-east-qa').resolve()
assert OUT.is_relative_to(ROOT)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
notes={
 'east-r01':'两条近水平弧形石槽在东邻拼接处连续，未见槽口跳位、垂直曝光带或新增物体。低对比宽笔触保持一致。',
 'guide-x3981-r01':'guide 过渡切口处两条槽线连续，石面未见沿切口形成的竖直色带。',
 'east-r02':'中段石槽在拼接处延续，未见断槽或竖直色带。',
 'guide-x3981-r02':'单条横向槽线与底材连续，未见 guide 切口印痕。',
 'east-r03':'安静石面与宽幅低对比斜笔触延续，未见拼接线曝光阶跃。',
 'guide-x3981-r03':'无结构物穿过该切口，宽笔触未形成固定 x 位置的曝光带。',
 'east-r04':'上部槽线在显示 x256 附近（本块 x4096 边界、row4 局部 y约145）斜率由向右下倾转为向右微上倾，形成浅 V 折角。补看 128×112 原像素细节后确认暗槽存在小台阶与厚度变化；RGB 均值低于160的深色上缘在相邻 x255→256 从 y140 到 y149，约9 px阶跃。无露白缺口，但属于需要局部修复 / 复核的几何不连续。其余石面无明显曝光带。',
 'guide-x3981-r04':'斜槽线经过 guide 切口连续，未见断槽或沿切口竖直色带。东邻边界折角不在本 scope 内。',
 'internal-y1024-c04':'槽线位于实际水平拼接线以上；拼接线两侧石面与笔触连续，未见横向曝光带。',
 'guide-y1139-c04':'安静石面未见水平 guide 过渡条带。',
 'internal-y2048-c04':'宽幅斜笔触连续，未见水平亮度阶跃或画布边线。',
 'guide-y2163-c04':'斜笔触穿过过渡区保持低对比，未见水平边界线。',
 'internal-y3072-c04':'斜向石槽穿过水平拼接线处连续，边缘和阴影无可见跳位；无横向曝光带。',
 'guide-y3187-c04':'弧形石槽和石面连续穿过过渡区，未见横向断槽或曝光条带。'
}
reviews=[]
for s in manifest['scopes']:
 p=Path(s['path']); assert sha(p)==s['sha256']
 rgb=Image.open(p).convert('RGB'); assert hashlib.sha256(rgb.tobytes()).hexdigest()==s['rgbSha256']
 reviews.append({'scopeId':s['id'],'path':s['path'],'sha256':s['sha256'],'rgbSha256':s['rgbSha256'],'sourceMappings':s['sourceMappings'],'actualViewCompleted':True,'viewTool':'tools.view_image','viewDetail':'original','viewCount':1,'status':'needs-parent-geometry-review' if s['id']=='east-r04' else 'no-actionable-defect-seen','observation':notes[s['id']]})
im=np.asarray(Image.open(OUT/'east-r04.png').convert('RGB'),dtype=float)
gray=im.mean(axis=2)
ys=50+gray[50:200,:].argmin(axis=0)
measurement={'method':'Supporting only: darkest RGB-mean pixel in display y50..199 for each x. Not an automatic visual verdict.','leftFitX':[160,240],'leftSlopeDyDx':float(np.polyfit(np.arange(160,240),ys[160:240],1)[0]),'rightFitX':[272,352],'rightSlopeDyDx':float(np.polyfit(np.arange(272,352),ys[272:352],1)[0]),'darkestYAtSampleX':{str(x):int(ys[x]) for x in [160,200,240,255,256,272,312,352]}}
review={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'tile':'r09_c08','reviewer':'/root/c08_east_qa','manifestPath':str(OUT/'manifest.json'),'manifestSha256':sha(OUT/'manifest.json'),'scopeCount':14,'actualViewCount':14,'scopesWithNoActionableDefectSeen':13,'openGeometryReviewItems':1,'imageEditsPerformed':False,'automaticAcceptance':False,'entireTileAccepted':False,'scopeLimit':'Only already complete c04 native column and its east neighbor; no north y115 guide strip included. Remaining columns and full tile still require review.','openItem':{'scopeId':'east-r04','severity':'localized visible direction kink; continuous groove, no gap','displayLocation':[256,145],'tileBoundaryX':4096,'tileYApprox':3217,'requestedAction':'Parent inspect the exact source join and decide intended corner versus unintended direction mismatch before closing.','supportingMeasurement':measurement},'views':reviews}
detail=OUT/'east-r04-kink-detail.png'
detailim=Image.open(detail).convert('RGB')
assert detailim.tobytes()==Image.open(OUT/'east-r04.png').convert('RGB').crop((192,88,320,200)).tobytes()
review['actualViewCount']=15
review['uniquePrimaryScopeCount']=14
review['supplementaryDiagnosticViewCount']=1
review['supplementaryDiagnostic']={'path':str(detail),'sha256':sha(detail),'width':128,'height':112,'rgbSha256':hashlib.sha256(detailim.tobytes()).hexdigest(),'parentScopeId':'east-r04','sourceImagePath':str(OUT/'east-r04.png'),'sourceImageSha256':sha(OUT/'east-r04.png'),'sourceCrop':[192,88,320,200],'destinationBox':[0,0,128,112],'operation':'Integer crop only; no resampling or edits. Underlying native/east source mapping inherited exactly from east-r04 scope.','actualViewCompleted':True,'viewTool':'tools.view_image','viewDetail':'original','viewCount':1}
review['openItem']['severity']='Localized groove direction kink and dark-channel vertical step; no white gap.'
review['openItem']['requestedAction']='Resolve the local groove step and slope mismatch, then re-export/review affected east-r04 plus guide and horizontal scopes if pixels change there. This review does not authorize accepting the defect.'
review['openItem']['supportingMeasurement']['thresholdEvidence']={'method':'RGB mean <160 within y50..199; supplemental geometry measurement, not automatic acceptance.','darkSpanAtX255':[140,147],'darkSpanAtX256':[149,159],'topEdgeJumpPixels':9}
(OUT/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reviewPath':str(OUT/'review.json'),'reviewSha256':sha(OUT/'review.json'),'actualViewCount':15,'uniquePrimaryScopeCount':14,'openItems':1,'measurement':measurement},ensure_ascii=False,indent=2))
