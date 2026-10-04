import json,hashlib,datetime
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2]
p=root/'review-parts/combat-W.json'; obj=json.loads(p.read_text(encoding='utf-8-sig'))
by={r['slot']:r for r in obj['frames']}
notes={1:'凝神起手，右手抬至胸前。',2:'右掌向前引导，左手完整持弓。',3:'恢复上一轮已返回未导出原图，右手空手回到箭筒。',4:'右手取出一支实体箭，仍未搭弦。',5:'弦V、箭尾与右手指尖汇合，但初搭弦拉距过深，需要缩短，不能作为浅搭弦验收。',6:'箭与弦连接成立，但初拉弦仍偏深，05到06拉距不够连续，06到07右手跃迁待修。',7:'弦V与箭尾合一，右手后拉、膝屈加深；脸/头/靴位置较06移动，动态需复核。',8:'右手比07略后拉，满弦接近就位。',9:'满弦箭尾与右手同点，08到09姿态差值小；需动态确认聚力停顿自然。',10:'松弦释放，右手张开后随，箭已消失，弦回直。',11:'空手后随，左弓臂伸展，弦直，双靴清楚。',12:'右手回胸、左肘开始弯回，脚距收窄偏快待动态检查。',13:'降弓及右手回腰，左手完整长弓。',14:'右手下降，双靴回拢，外衣和马尾衰减。',15:'右手侧腰自然下垂，无再次取箭。',16:'独立警戒收势，脚位和弓长保持近15；首尾待机衔接需核验。'}
notes[5]='已二次局部AI修正：双手集中弓把前方，右手与脸之间留出空隙，弓弦浅折并与箭尾同点，初搭弦单帧机制修正成立。修正后弓/体位置与04及07动态连续性仍待复核。'
notes[6]='第三轮局部AI修正以正确05为参考，实际双手间距从05约85px增至约140px（1024视图估计），弦V深度有逐步增长；弦两段、箭尾、右指同点。小幅初拉姿态已改善，06到07根位/弓位的连续性仍待动态复核。'
for n in range(1,17):
 fp=root/'runtime/cast/W'/f'{n:02}.png'
 by[f'cast/W/{n:02}']={'slot':f'cast/W/{n:02}','status':'needs_review','sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'evidence':'实际查看独立生成图。'+notes[n]+' 未作整段动态通过声明。'}
for n in (5,6):
 by[f'hit/W/{n:02}']['status']='needs_review'
 by[f'hit/W/{n:02}']['evidence']='独立受击恢复帧，双脚回收站定；相机较01–04更侧，整段相机连续性待动态复核。'
for slot,row in by.items():
 action,_,index=slot.split('/');n=int(index)
 fp=root/'runtime'/action/'W'/f'{n:02}.png'
 row['sha256']=hashlib.sha256(fp.read_bytes()).hexdigest()
 row['localToeAxisCheck']='passed'
 row['toeKneeAnkleEvidence']='实际查看09当前正式图下肢：前靴鞋尖向前偏左，后靴向前偏左至前下；膝踝与靴面朝向连续，未见鞋尖向身体外侧横撇或踝部反扭。W为定点战斗姿态，不套用跑步双脚相位。'
 if action=='hit':contact='双脚支撑的受力/恢复姿态；靴底平，未把受击屈膝画成长期双脚悬空。'
 elif action=='attack':contact='03到04开立、04到08弓步受力，09收回、10到12双脚站定；两靴底有支撑朝向，脚距变化的节奏仍需整段复核。'
 else:contact='起手双脚站定，05到12开立拉弓并屈膝受力，13收回、14到16站定；靴底平而非鞋底朝前。'
 row['groundContactEvidence']=contact
obj['frames']=list(by.values());obj['sequences']=[{'action':a,'direction':'W','status':'needs_review','frameSha256':[r['sha256'] for r in obj['frames'] if r['slot'].startswith(a+'/W/')],'evidence':'独立帧已齐，脚尖/膝踝/靴底接触静态复核未发现明确外八错误。cast05浅搭弦及06小幅初拉已修正，整段相机/根位/弓长/脚距动态连续性尚未通过。'} for a in ['hit','attack','cast']]
obj['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();obj['note']='W战斗34独立帧齐；cast05浅搭弦及06小幅初拉已定点修正，整段相机/根位/弓位连续性仍待动态复核；PNG完整不等于动画验收。'
obj['toeReview']={'status':'local_static_passed','sources':'provenance/run-SW/toe-comparison-sources.json','basis':'独立查看09当前图。07仅为普通只读对照，用户撤回07及垂直方向正确判断，没有以它作为通过标杆。','newFootEdits':'未发现需进一步重画的明确外撇，保留正常透视。'}
p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
for action,total,ms in [('hit',6,40),('attack',12,30),('cast',16,45)]:
 frames=[]; sheet=Image.new('RGB',(1024,282*((total+3)//4)),(238,241,235))
 for n in range(1,total+1):
  fp=root/'runtime'/action/'W'/f'{n:02}.png'; im=Image.open(fp).convert('RGBA')
  canvas=Image.new('RGBA',(1024,1024),(238,241,235,255));canvas.alpha_composite(im); frames.append(canvas.convert('RGB').resize((512,512)))
  tile=canvas.convert('RGB').resize((256,256));x=(n-1)%4*256;y=(n-1)//4*282
  sheet.paste(tile,(x,y));ImageDraw.Draw(sheet).text((x+8,y+258),f'{action}/W/{n:02}',fill=(30,50,30))
 out=root/'provenance/combat-W';sheet.save(out/f'{action}-contact.png')
 frames[0].save(out/f'{action}-normal.gif',save_all=True,append_images=frames[1:],duration=ms,loop=0)
 frames[0].save(out/f'{action}-slow.gif',save_all=True,append_images=frames[1:],duration=ms*4,loop=0)
print('W 34 frames; review notes and diagnostic previews written. GIF cast45ms is quantized; main HTML exact timing authoritative.')

