from pathlib import Path
from PIL import Image
import json,hashlib,datetime
root=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy')
pairs=[('SE/01-v5.png','SE/01-v4.png'),('SE/02-v3.png','SE/02-v1.png'),('N/12-v7.png','N/14-v2.png'),('N/14-v2.png','N/06-v5.png')]
rows=[]
for f,ref in pairs:
 p=root/'generation/run'/f;q=root/'generation/run'/ref
 def read(p):
  im=Image.open(p);return {'source':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'mode':im.mode,'upperAlphaBounds':list(im.getchannel('A').crop((0,0,1254,500)).point(lambda a:255 if a>32 else 0).getbbox())}
 a=read(p);b=read(q)
 finding=('鞋头位于脚踝右下，鞋掌随东南跑向；未见鞋体过大或头身比例重绘硬伤。' if f.startswith('SE') else '只见左鞋完整鞋底；右脚显示后跟/后帮，未翻出第二只完整鞋底。头身与参考母版一致，未见整人缩放或平移硬伤。')
 rows.append({**a,'reference':b,'finding':finding,'staticVerdict':'recommend_keep','dynamicApproved':False})
out=root/'review/moon-comparison/root-candidate-independent-review.json'
out.write_text(json.dumps({'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewScope':'实际独立看原生图；鞋向、单左鞋底/右鞋跟、头身固定检查；不代表动态通过。','frames':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=True))

