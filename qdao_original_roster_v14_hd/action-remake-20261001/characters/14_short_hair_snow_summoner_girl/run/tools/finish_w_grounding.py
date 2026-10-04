from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,importlib.util
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location('exp',R/'tools/export_frame.py');e=importlib.util.module_from_spec(sp);sp.loader.exec_module(e)
selected={1:'v1',2:'v1',3:'v2',4:'v1',5:'v1',6:'v3',7:'v4',8:'v4',9:'v2',10:'v2',11:'v2',12:'v2',13:'v2',14:'v3',15:'v3',16:'v2'}
changes={6:525,7:537,8:523,14:525,15:515,16:542}
reg=json.loads((R/'run/W/registration.json').read_text(encoding='utf-8-sig'))
for n,x in changes.items():
 src=R/'run/staging'/f'run-W-{n:02}-{selected[n]}.png';dst=R/'run/W'/f'{n:02}.png'
 e.run(src,dst)
 rr=reg['frames'][n-1];rr.update(sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),srcRoot=[x,984],basis='新六帧同批画布位置：x人工按髋/支撑中心，y统一984由08/16平底接触平面判断，保留06/14折腿腾空高度；未按逐帧alpha底部贴地。',confidence='manual approx +/-12px; registered playback pending')
reg['method']='人工髋/支撑中心；原始10帧固定虚拟地面960，新6帧固定984，由其08/16接触平面共同判断；不逐帧贴最低像素、不bbox缩放。'
reg['revisionAt']=datetime.now(timezone.utc).isoformat()
reg['updatedSourceFrames']=[f'run/W/{n:02}.png' for n in changes]
(R/'run/W/registration.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8')
review={'status':'hand_foot_static_review_complete_registered_dynamic_review_pending','technical':{'frames':16,'size':[1024,1024],'mode':'RGBA','sixChangedFrames':list(changes),'sixRawExportsOnly':True,'otherTenRegisteredExportsUntouched':True},'observed':{'grounding':'02/10屈膝压低承重，03/11抬膝过身且一脚支撑，04/12后伸蹬地；06/14双膝折叠短暂腾空，07/15伸膝下降，08/16平底落地，接01/09。','hands':'近左臂抱狐连续；远右臂持蓝雪晶，06/07/08已从错误前摆定向修回后摆，没有第三空袖。14/15/16保持前摆。','feet':'鞋尖和膝踝沿侧向跑步平面；落地鞋平底向画面左，回收脚为矢状面跖屈，未见V形外八或单独拧踝。','alternation':'03与11、06与14的前抬大腿粗细及与袍下遮挡关系不同：首半步前腿较远，后半步前腿较近；部分髋部仍被短袍遮挡，须注册后连续播放核对，未仅按prompt宣告完整动态通过。','identity':'16按01短发短袍修复；近左雪花头饰与紫眼等未交换。'},'reviewedAt':datetime.now(timezone.utc).isoformat(),'registration':'run/W/registration.json','remaining':['parent apply six raw exports with updated registration','parent verify 720ms dynamic feet contact, alternating legs and 16-to-01 continuity'],'frames':reg['frames']}
(R/'run/W/review-final-subtask.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
out=R/'run/W/preview-review';out.mkdir(exist_ok=True)
sheet=Image.new('RGB',(1280,1400),'#e4e8e8');sd=ImageDraw.Draw(sheet);feet=Image.new('RGB',(1600,900),'#e4e8e8');fd=ImageDraw.Draw(feet);ani=[]
for n in range(1,17):
 im=Image.open(R/'run/staging'/f'run-W-{n:02}-{selected[n]}.png').convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
 x,y=reg['frames'][n-1]['srcRoot'];tx=512-.8*x;ty=942-.8*y
 shown=im.transform((1024,1024),Image.Transform.AFFINE,(1/.8,0,-tx/.8,0,1/.8,-ty/.8),Image.Resampling.BICUBIC)
 frame=Image.new('RGB',(512,512),'#e4e8e8');fr=shown.resize((512,512),Image.Resampling.LANCZOS);frame.paste(fr,(0,0),fr);ImageDraw.Draw(frame).line((0,471,511,471),fill='#607a72');ImageDraw.Draw(frame).text((10,10),f'W{n:02} - 720ms cycle',fill='#203040');ani.append(frame)
 thumb=shown.resize((320,320));cx=(n-1)%4*320;cy=(n-1)//4*350;sheet.paste(thumb,(cx,cy),thumb);sd.line((cx,cy+294,cx+319,cy+294),fill='#607a72');sd.text((cx+8,cy+323),f'W{n:02}',fill='#203040')
 crop=shown.crop((150,650,850,1024)).resize((400,214));cx=(n-1)%4*400;cy=(n-1)//4*225;feet.paste(crop,(cx,cy),crop);fd.text((cx+5,cy+3),f'W{n:02}',fill='#203040')
sheet.save(out/'grounding-contact.jpg',quality=94);feet.save(out/'grounding-feet.jpg',quality=95);ani[0].save(out/'grounding-720ms.gif',save_all=True,append_images=ani[1:],duration=45,loop=0,disposal=2)
print(json.dumps({'replaced':list(changes),'registration':str(R/'run/W/registration.json'),'preview':str(out/'grounding-contact.jpg')}))

