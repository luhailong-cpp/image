from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
roots={'E':[579,558,558,558,550,548,550,550,537,541,546,546,541,548,547,550],'W':[534,528,548,510,528,502,490,501,521,535,524,521,511,516,518,520]}
records=[]
for d in ['E','W']:
 sheet=Image.new('RGB',(1600,900),'#dfe4e4');draw=ImageDraw.Draw(sheet)
 for n in range(1,17):
  p=R/'cast'/d/f'{n:02}.png';im=Image.open(p).convert('RGBA')
  assert im.size==(1024,1024) and im.getextrema()[3][0]==0
  rec=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
  records.append({'file':f'cast/{d}/{n:02}.png','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'srcRoot':[roots[d][n-1],975 if d=='E' else 965],'basis':'人工按髋部与支撑平衡中心估计x；同向全组使用固定虚拟地面，保留蹲伸与抬脚，不按每帧最低像素贴地。','confidence':'manual approx +/-15px; parent must check registered playback'})
  crop=im.crop((250,740,850,1024)).resize((400,189));x=(n-1)%4*400;y=(n-1)//4*225
  sheet.paste(crop,(x,y),crop);draw.text((x+8,y+193),f'{d}{n:02} toes aligned travel direction',fill='#203040')
 sheet.save(R/'cast'/d/'preview-review/feet.jpg',quality=95)
assert len({x['sha256'] for x in records})==32
reg={'schemaVersion':1,'coordinateSpace':'current whole-canvas 1024x1024 exports, before global normalization','globalScale':0.8,'targetRoot':[512,942],'applyTransform':False,'method':'人工髋与支撑中心注册，E全组地面975、W全组965；固定全局0.80，禁止逐图bbox归一化。','frames':records}
(R/'cast/registration.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8')
review={'reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'cast E/W 32 final raw frames','technical':{'count':32,'canvas':[1024,1024],'mode':'RGBA','uniqueSha256':32,'perImageProvenance':True},'visualReview':{'E':'近侧解剖右肩袖口连接雪晶右手；远侧左手胸前抱狐。E05-16已针对原错接前臂重新生成。E06/07精确请求映射未确认，见恢复记录。','W':'近侧左臂胸前抱狐，远侧右臂持雪晶；上举、伸出、收手可读。','feet':'E鞋尖均随身体向画面右；W鞋尖均向画面左；逐帧未见膝踝相反旋转或V字外八。W06-10后脚提起、前脚承重；E08/09站姿较开但两鞋未向相反方向外转。','loop':'首尾都是回收持物姿态；注册后720ms以外的cast独立时长由根任务播放验收。'},'status':'static visual reviewed; registration and final playback pending parent','registration':'cast/registration.json','contactSheets':['cast/E/preview-review/contact.jpg','cast/W/preview-review/contact.jpg','cast/E/preview-review/feet.jpg','cast/W/preview-review/feet.jpg'],'remaining':['parent apply global registration and verify final playback']}
(R/'cast/review-final-subtask.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'count':32,'registration':str(R/'cast/registration.json'),'review':str(R/'cast/review-final-subtask.json')}))

