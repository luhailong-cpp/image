from pathlib import Path
import json,hashlib,shutil,datetime,re,argparse
root=Path(r'E:\work\image\qdao_chibi_roster_v12');site=root/'review/site';game=Path(r'E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV12')
roles={'23_lantern_courier':'灯穗小使','24_lu_dongbin':'吕洞宾','25_lion_drum_guard':'狮鼓护卫','26_osmanthus_healer':'桂香药婆','27_ink_kite_ranger':'墨鸢游侠','28_moon_rabbit_artificer':'月兔机关师','29_he_xiangu':'何仙姑','30_han_xiangzi':'韩湘子'}
p=argparse.ArgumentParser();p.add_argument('--include',nargs='+',required=True,choices=list(roles));p.add_argument('--overview',action='store_true');args=p.parse_args()
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
reportfile=site/'preview-source-verification.json';old=json.loads(reportfile.read_text(encoding='utf-8'));ids={x['character_id'] for x in old['characters']}|set(args.include);records=[]
for cid in roles:
 if cid not in ids:continue
 c=root/('candidate-natural-body' if cid=='29_he_xiangu' else 'candidate-stable-body')/cid
 m=json.loads((c/'manifest.json').read_text(encoding='utf-8'));q=json.loads((c/'qc.json').read_text(encoding='utf-8'));a=json.loads((game/cid/'appearance.json').read_text(encoding='utf-8'))
 assert q['status']=='passed' and q['visual_review']=='passed'
 assert m['alignment']['version']==3 and a['alignmentVersion']==3 and a['manifest_sha256']==sha(c/'manifest.json')
 files=[f for f in m['files'] if f['path'].endswith('.png')];assert len(files)==81
 for f in files:assert sha(c/f['path'])==f['sha256'] and sha(game/cid/f['path'])==f['sha256']
 dest=site/'assets/v12'/cid;backup=site/'assets/pre-natural'/cid
 changed=[f for f in files if not (dest/f['path']).exists() or sha(dest/f['path'])!=f['sha256']]
 if changed:
  if dest.exists() and not backup.exists():shutil.copytree(dest,backup)
  for f in files:
   d=dest/f['path'];d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(c/f['path'],d)
 for f in files:assert sha(dest/f['path'])==f['sha256']
 records.append({'character_id':cid,'source':str(c),'manifest_sha256':sha(c/'manifest.json'),'png_count':81,'changed_png_count':len(changed),'site_and_game_hashes_match':True,'previous_site_backup':str(backup)})
now=datetime.datetime.now(datetime.timezone.utc).isoformat();pending=[x for x in roles if x not in ids];names='、'.join(roles[x] for x in roles if x in ids)
report={'status':'passed','verified_utc':now,'scope':'site assets and published PNG hashes; runtime tests are separate','characters':records,'pending':pending}
reportfile.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if pending:notice=names+'已完成本轮道家 Q 版与自然步态修正并接入游戏项目。'+'、'.join(roles[x] for x in pending)+'仍在收尾。'
else:notice='八位道家 Q 版角色的造型与自然步态修正已完成并接入游戏素材。吕洞宾、何仙姑、韩湘子保留各自身份和器物，八人使用不同服装与轮廓。'
status=f'已完成 {len(ids)} / 8 位：每人八方向、每方向 8 张行走帧，另有独立站立图。新批次游戏运行验证仍在进行。'
p=site/'index.html';t=p.read_text(encoding='utf-8');t=re.sub(r'<div class="notice">.*?</div>',f'<div class="notice">{notice}</div>',t,count=1);t=re.sub(r'<p class="deployment">.*?</p>',f'<p class="deployment">{status}</p>',t,count=1)
for cid in ids:t=re.sub(r"(id:'"+re.escape(cid)+r"',name:'[^']+',)exported:(?:false|true),integrated:(?:false|true)",r'\1exported:true,integrated:true',t)
p.write_text(t,encoding='utf-8')
state='2026-09-16 当前状态：'+notice+'每人 64 张真实行走、8 张独立站立和 1 张肖像，含 8 张行走条带共 81 张 PNG，全部按对齐 v3 发布。站点与已发布素材逐文件 SHA 核对一致。新批次的游戏运行验证仍在进行，既有失败记录保留。内部检查通过不等于用户已认可整批美术。'
current='游戏当前实际接入 V12 的有 '+names+'。'+(('、'.join(roles[x] for x in pending)+'仍使用同 ID 的 V11。') if pending else '八人均已完成素材接入。')
for filename in ['README.md','CLIENT_CONTRACT.md']:
 p=root/filename;t=p.read_text(encoding='utf-8');paras=t.split('\n\n');assert '当前状态：' in paras[1];paras[1]=state;paras[2]=current;t='\n\n'.join(paras)
 t=t.replace('本轮六位已接入，另两位继续收尾。',f'本轮 {len(ids)} 位已接入。'+('其余角色继续收尾。' if pending else ''))
 if not pending:t=t.replace('游戏当前实际接入V12的有23灯穗小使、24吕洞宾、25狮鼓护卫、26桂香药婆、29何仙姑、30韩湘子；27墨鸢游侠、28月兔机关师仍使用同ID的V11。已接入的角色也在本次造型、步态和比例复核范围内，不能把已接入状态表述为用户已认可。',current+'素材接入不代表用户已认可美术。')
 p.write_text(t,encoding='utf-8')
if args.overview:
 assert not pending,'Final portrait overview requires all eight published characters'
 from PIL import Image,ImageDraw,ImageFont
 # Contact board only: intact source canvases at the same display scale; no retouching.
 width,height=1600,1440;canvas=Image.new('RGB',(width,height),'#edf1f3');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',25);small=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',19)
 sources=[]
 for i,(cid,name) in enumerate(roles.items()):
  x=(i%4)*400;y=(i//4)*720;draw.text((x+16,y+12),cid[:2]+' '+name,font=font,fill='#243540')
  for j,version in enumerate(['v11','v12']):
   src=site/'assets'/version/cid/'portrait.png';im=Image.open(src).convert('RGBA');im.thumbnail((330,250),Image.Resampling.LANCZOS)
   top=y+58+j*328;draw.rectangle((x+10,top,x+390,top+312),fill='#e0ddd0');canvas.paste(im,(x+(400-im.width)//2,top+12),im);draw.text((x+22,top+277),'旧版 V11' if j==0 else '新版 V12 · 已接入',font=small,fill='#243540')
   sources.append({'character_id':cid,'version':version,'source':str(src),'sha256':sha(src),'treatment':'whole source canvas uniformly scaled into fixed portrait contact tile'})
 dest=site/'portrait-comparison.jpg';backup=site/'portrait-comparison-before-final.jpg'
 if dest.exists() and not backup.exists():shutil.copyfile(dest,backup)
 canvas.save(dest,quality=92)
 (site/'portrait-comparison-sources.json').write_text(json.dumps({'created_utc':now,'sources':sources},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','characters':len(records),'png_count':len(records)*81,'pending':pending,'overview':args.overview},ensure_ascii=False))
