from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
keys={('N',7):'run-N-07-archer-v1',('N',8):'run-N-08-archer-v1',('N',11):'run-N-11-archer-v2',('N',14):'run-N-14-archer-v1',('N',15):'run-N-15-archer-v1',('S',2):'run-S-02-archer-v3',('S',3):'run-S-03-archer-v1',('S',10):'run-S-10-archer-v1',('S',11):'run-S-11-archer-v1',('S',14):'run-S-14-archer-v1'}
reasons={('N',7):'屏右脚预落地足底翻转过晚，纠正膝踝至朝N鞋跟视图，保留腾空。',('N',8):'屏右脚在N08仍整底向后，接N09突然翻转，改为近地鞋跟视图。',('N',11):'右持扇臂横向外展跳跃，调整为N10到N12之间紧凑前后摆弧。',('N',14):'屏左下一支撑腿仍向后踢，纠正左膝踝预落地和右腿后摆关系。',('N',15):'屏左足底在预接触仍正对后方，纠正为朝N的鞋跟近地姿态。',('S',2):'屏右承重脚仍是抬趾露底前踢，纠正为平底朝S支撑及膝踝承重。',('S',3):'屏右过渡支撑仍正面露整底，纠正为膝踝相连的支撑鞋面。',('S',10):'屏左承重足整底朝镜头，改为平底朝S并保留反侧后腿。',('S',11):'屏左支撑前踢露底且低于地面，纠正为朝S平底支撑及收回底线。',('S',14):'屏左后摆膝踝足轴向左外甩，纠正为纵向后摆，保留空中动作。'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
s={'character':'15_water_dragon_scholar_boy','reviewedAt':now,'reviewer':'continue_cast','status':'10_static_reviewed_candidates_parent_review_pending','notFormalSelection':True,'reference':'09_bamboo_archer_girl current runtime, pose structure only','frames':[],'previewTiming':{'frameMs':75,'cycleMs':1200,'slowFrameMs':300,'authority':'root latest direction 2026-10-04','clientConfirmed':False}}
for (di,n),key in keys.items():
 rec=f'provenance/generation/{key}.json';r=json.loads((b/rec).read_text(encoding='utf-8'))
 src=f'sources/new/{key}.png';im=Image.open(b/src)
 assert im.size==(1254,1254) and im.mode=='RGBA' and sha(b/src)==r['sha256']
 assert all(Path(ref['file']).exists() and sha(ref['file'])==ref['sha256'] for ref in r['references'])
 assert (b/r['prompt']).exists() and (b/r['evidence']['toolResult']).exists()
 a=im.getchannel('A').point(lambda x:255 if x>=128 else 0);bbox=a.getbbox()
 s['frames'].append({'action':'run','direction':di,'frame':n,'source':src,'generationRecord':rec,'sha256':r['sha256'],'supersedes':r['supersedes'],'reason':reasons[(di,n)],'review':{'status':'static_checked_pending_parent_sequence_review','reviewer':'continue_cast','reviewedAt':now,'nativeAlphaBBox':bbox,'bboxUsedForTransform':False,'hands':'RIGHT fan, LEFT empty; anatomical sides preserved','footAxis':'沿自身N/S运动纵向判断，预落地脚底朝地；后摆/腾空脚允许露底','wholeBodyTransform':'未人为平移/逐帧缩放；复用1254→940 at(42,49)固定导出','limitations':['生成局部编辑仍有少量衣缘/脸发轮廓变化，不能声称像素级完全未变','动态和用户验收仍待主线程，静态选用不等于通过']},'retainedTransform':r['retainedTransform']})
(out/'ns-selection.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
for di in ['N','S']:
 full=Image.new('RGB',(1120,1200),(32,40,51));fd=ImageDraw.Draw(full)
 feet=Image.new('RGB',(1280,880),(32,40,51));dd=ImageDraw.Draw(feet);seq=[];rows=[]
 for n in range(1,17):
  key=keys.get((di,n))
  if key:
   src=b/'sources/new'/f'{key}.png';im=Image.open(src).convert('RGBA')
   alpha=im.getchannel('A').point(lambda x:0 if x<=8 else x);im.putalpha(alpha)
   canvas=Image.new('RGBA',(1024,1024));canvas.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
  else:src=b/'runtime/run'/di/f'{n:02d}.png';canvas=Image.open(src).convert('RGBA')
  tag=f'{di}{n:02d} '+('NEW' if key else 'keep')
  x=(n-1)%4*280;y=(n-1)//4*300
  panel=Image.new('RGBA',(280,280),(32,40,51,255));panel.alpha_composite(canvas.resize((280,280)));full.paste(panel.convert('RGB'),(x,y))
  fd.line((x,y+258,x+280,y+258),fill=(160,114,69));fd.text((x+8,y+280),tag,fill=(110,225,190) if key else 'white')
  crop=canvas.crop((200,660,824,1020));crop.thumbnail((320,184))
  x=(n-1)%4*320;y=(n-1)//4*220
  pane=Image.new('RGBA',(320,196),(32,40,51,255));pane.alpha_composite(crop,((320-crop.width)//2,0));feet.paste(pane.convert('RGB'),(x,y+24))
  dd.text((x+8,y+5),tag,fill=(110,225,190) if key else 'white')
  view=Image.new('RGBA',(384,420),(32,40,51,255));view.alpha_composite(canvas.resize((384,384)));dr=ImageDraw.Draw(view);dr.line((0,353,384,353),fill=(160,114,69));dr.text((8,393),f'{tag} 1200ms normal / 4800ms slow',fill='white');seq.append(view)
  rows.append({'slot':f'{di}{n:02d}','source':str(src),'sha256':sha(src),'isNew':bool(key)})
 full.save(out/f'ns-{di}-updated-contact.png');feet.save(out/f'ns-{di}-updated-feet.png')
 seq[0].save(out/f'ns-{di}-1200ms.apng',save_all=True,append_images=seq[1:],duration=75,loop=0,format='PNG')
 seq[0].save(out/f'ns-{di}-slow.apng',save_all=True,append_images=seq[1:],duration=300,loop=0,format='PNG')
 (out/f'ns-{di}-preview-sources.json').write_text(json.dumps({'sources':rows,'operation':'new native1254 only uses fixed940 canvas offset42,49; kept old runtime unchanged; diagnostic thumbnails','frameMs':75,'cycleMs':1200,'slowMs':300,'dynamicReviewed':False},ensure_ascii=False,indent=2),encoding='utf-8')
originals=json.loads((out/'ns-visual-inputs.json').read_text(encoding='utf-8'))['sources']
assert all(sha(r['file'])==r['sha256'] for r in originals),'Read-only inputs changed'
report={'verifiedAt':now,'selected':10,'uniqueSHA':len(set(f['sha256']for f in s['frames'])),'native1254':True,'sourcesRecordsReferencesVerified':True,'original64RuntimeUnchanged':True,'mainSelectionManifestRuntimeNotWritten':True,'passed':True,'scope':'technical integrity only'}
(out/'ns-integrity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':report,'bounds':[{k:f[k]for k in ['direction','frame','source']}|{'bbox':f['review']['nativeAlphaBBox']}for f in s['frames']]},ensure_ascii=False))

