from pathlib import Path
import json,hashlib,datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw
B=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
versions={3:2,5:2,6:2,7:2,9:3,12:2,13:2,15:2}
notes={
1:'右侧支撑、左腿后回收；盘手较低。需动态复核接地。',
2:'右侧承重缓冲候选，双手持物完整。',
3:'局部重新安排支撑与回收腿，替换原相位偏差。',
4:'右支撑末期候选，抬跟/换脚幅度需动态检查。',
5:'换脚前段局部修正；依实图保留双腿分离及同向靴。',
6:'短腾空候选；左右领先/鞋底露出需动态重点确认。',
7:'左脚将着地、右腿回收；局部腿部修正。',
8:'左支撑着地候选、右后抬；左右持物未交换。',
9:'左脚支撑关键帧，右后抬；由旧walk NE06局部修出。',
10:'左脚缓冲承重候选，膝踝连通。',
11:'左脚支撑末期候选、右膝前移，鞋向NE。',
12:'替换原换手稿：只改下肢而保留正确持手。',
13:'替换原持手歧义稿：只改低腾空下肢。',
14:'右腿领先下降候选；三卡单盘完整。',
15:'替换原持手歧义稿：只改右脚落地前下肢。',
16:'右脚初接触闭环候选；保留三卡单盘。'}
frames=[];errors=[]
sheet=Image.new('RGB',(1152,1232),(218,225,232));draw=ImageDraw.Draw(sheet)
legs=Image.new('RGB',(1600,800),(218,225,232));ld=ImageDraw.Draw(legs)
for n in range(1,17):
 rel=f'generation/run/NE/{n:02}-v{versions.get(n,1)}.png';p=B/rel;rp=B/(rel+'.generation.json')
 if not p.exists() or not rp.exists():errors.append(f'Missing {rel}');continue
 rec=json.loads(rp.read_text(encoding='utf-8'));im=Image.open(p).convert('RGBA')
 if im.width<1024 or im.height<1024 or Image.open(p).mode!='RGBA':errors.append(f'Native invalid {rel}')
 if rec.get('sha256')!=sha(p):errors.append(f'Record SHA invalid {rel}')
 if sha(B/rec['prompt'])!=rec.get('promptSha256'):errors.append(f'Prompt SHA invalid {rel}')
 for ref in rec.get('references',[]):
  if not Path(ref['path']).exists() or sha(Path(ref['path']))!=ref['sha256']:errors.append(f'Reference SHA invalid {rel}: {ref["path"]}')
 if rec.get('actualModel') is not None or rec.get('actualQuality') is not None:errors.append(f'Unexpected confirmed model-quality {rel}')
 if not (B/rec['evidence']['receipt']).exists():errors.append(f'Missing receipt {rel}')
 row={'action':'run','direction':'NE','frame':n,'source':rel,'generationRecord':rel+'.generation.json','sourceSha256':sha(p),'nativeSize':list(im.size),'status':'candidate','visualReview':'static_checked_candidate','dynamicReview':'not_verified','footReview':'static_direction_checked_dynamic_pending','reviewNote':notes[n]}
 frames.append(row)
 preview=im.resize((288,288),Image.Resampling.LANCZOS);x=(n-1)%4*288;y=(n-1)//4*308;sheet.paste(preview,(x,y),preview);draw.text((x+8,y+290),f'NE {n:02} v{versions.get(n,1)}',fill=(10,10,10))
 crop=im.crop((300,850,950,1254));crop.thumbnail((200,180));x=(n-1)%8*200;y=(n-1)//8*400;legs.paste(crop,(x,y+45),crop);ld.text((x+6,y+10),f'NE {n:02} v{versions.get(n,1)}',fill=(10,10,10))
 refs=rec.get('references',[])
 if refs:rec['editSource']={'path':refs[0]['path'],'sha256':refs[0]['sha256'],'generationRecord':refs[0]['path']+'.generation.json','operation':'宿主内置单帧局部AI编辑；旧walk来源沿此记录递归关联；没有镜像/复制/插值凑帧'}
 rec['review']={'status':'static_checked_candidate','staticViewed':True,'staticResult':'candidate_pending_dynamic','note':notes[n],'dynamicAcceptance':False,'realTimePlaybackVerified':False,'clientPlaybackVerified':False}
 rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stamp=datetime.datetime.now(ZoneInfo('America/New_York')).isoformat()
selection={'schema':1,'character':'20_star_formation_master_girl','scope':'NE only; NW handed to root for separate run-NW-selection.json','updatedAt':stamp,'expectedFrames':16,'availableFrames':len(frames),'exportTransform':{'size':[922,922],'offset':[51,40],'pivot':[512,922]},'dynamicAcceptance':False,'realTimePlaybackVerified':False,'clientPlaybackVerified':False,'frames':frames,'unresolved':['NE05-07低腾空与换脚应在正常倍速检查，不凭提示词认定实际相位','右承重组与左承重组头身位置有差异，须在统一完整画幅变换下检查比例/地面，不允许逐帧贴底','NE16->01闭环与盘手摆臂过渡待实际播放','正常节奏640/720/800ms均为试播值；客户端未接入'],'verificationErrors':errors}
selection['normalFrameMs']=75
selection['normalCycleMs']=1200
selection['timingBasis']='2026-10-03 最新用户经root明确：正常跑步16×75ms=1200ms；旧快档取消'
selection['unresolved'][-1]='正常1200ms、均匀75ms由root统一预览；此处未实播且客户端未接入'
selection['readonlyMotionReference']={'character':'09_bamboo_archer_girl','viewed':['preview/qa/run-NE-contact.png','runtime/run/NE/01.png','runtime/run/NE/05.png','runtime/run/NE/09.png','runtime/run/NE/13.png'],'application':'同向膝踝鞋轴、短前掌、后跟显示、支撑/短腾空/异侧承重；不借用外形或帧号；保留星阵盘卡持手'}
if len(frames)==16:
 frames[4],frames[5]=frames[5],frames[4]
 frames[4]['sourceRequestedSlot']=6
 frames[4]['frame']=5
 frames[4]['reviewNote']='根据实图将原请求06的低腾空放在05；鞋底露出来自抬脚，当前持物完整；1200ms动态待审。'
 frames[5]['sourceRequestedSlot']=5
 frames[5]['frame']=6
 frames[5]['reviewNote']='根据实图将原请求05放在06下降/前掌接近地面位置；接07异侧落地，保留真实原提示词。'
(B/'run-NENW-selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sheet=Image.new('RGB',(1152,1232),(218,225,232));draw=ImageDraw.Draw(sheet)
legs=Image.new('RGB',(1600,500),(218,225,232));ld=ImageDraw.Draw(legs)
for row in frames:
 n=row['frame'];im=Image.open(B/row['source']).convert('RGBA')
 thumb=im.resize((288,288),Image.Resampling.LANCZOS);x=(n-1)%4*288;y=(n-1)//4*308
 sheet.paste(thumb,(x,y),thumb);draw.text((x+8,y+290),f"NE {n:02} <- {Path(row['source']).stem}",fill=(10,10,10))
 crop=im.crop((300,850,950,1254));crop.thumbnail((200,180));x=(n-1)%8*200;y=(n-1)//8*250
 legs.paste(crop,(x,y+40),crop);ld.text((x+6,y+10),f"NE {n:02} <- {Path(row['source']).stem}",fill=(10,10,10))
sheet.save(B/'provenance/run-NENW-NE-selected-contact.jpg')
legs.save(B/'provenance/run-NENW-NE-selected-feet.jpg')
audit={'updatedAt':stamp,'selectedCount':len(frames),'uniqueSelectedSha256':len(set(x['sourceSha256'] for x in frames)),'nativeValidation':not errors,'errors':errors,'reviewScope':'原生生成图逐张静态查看及联系表；未进行动态实播','excluded':{'generation/run/NE/09-v1.png':'请求左支撑但实际右支撑，未纳入本选择','generation/run/NE/09-v2.png':'重复右支撑未纳入','generation/run/NE/03-v1.png':'相位偏差，v2局部修复','generation/run/NE/05-v1.png':'异侧过渡未落实，v2局部修复','generation/run/NE/06-v1.png':'异侧过渡未落实，v2局部修复','generation/run/NE/07-v1.png':'异侧过渡未落实，v2局部修复','generation/run/NE/12-v1.png':'左右持物交换，拒稿','generation/run/NE/13-v1.png':'持手结构歧义，v2保留原上身修下肢','generation/run/NE/15-v1.png':'持手结构歧义，v2保留原上身修下肢'},'NW':'已移交root，未写NW选择'}
(B/'provenance/run-NENW-NE-static-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frames':len(frames),'unique':audit['uniqueSelectedSha256'],'errors':errors},ensure_ascii=False))

