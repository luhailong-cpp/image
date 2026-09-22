"""Assemble a labelled diagnostic preview; never an approved runtime assembly."""
import argparse,base64,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CHAR='04_mountain_guardian_boy'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--frame04',type=Path);p.add_argument('--frame16',type=Path);p.add_argument('--equipment-fixed',action='store_true');a=p.parse_args()
 out=a.output.resolve();assert out.is_relative_to((ROOT/'recovery-20260921').resolve()) and not out.exists();out.mkdir(parents=True)
 rows=[];world=[]
 for n in range(1,17):
  if n in (1,5,9,13):source=ROOT.parent/'qdao_original_roster_v13/candidate'/CHAR/f'walk/NW/{n:02d}.png';kind='preserved V13 512'
  elif n in (2,3,4):source=ROOT/'candidate'/CHAR/f'walk/NW/{n:02d}.png';kind='canonical V14 candidate'
  else:source=HERE/'staging/candidate'/CHAR/f'walk/NW/{n:02d}.png';kind='new isolated staging'
  if n==4 and a.frame04:source=a.frame04.resolve();kind='isolated NW04 revised edge candidate'
  if n==16 and a.frame16:source=a.frame16.resolve();kind='isolated NW16 revised pose candidate'
  im=Image.open(source).convert('RGBA');source_size=list(im.size);w=im.resize((1024,1024),Image.Resampling.LANCZOS) if im.size!=(1024,1024) else im.copy();world.append(w)
  aa=np.array(w)[:,:,3];y,x=np.where(aa>8)
  issue='staff disk wrongly transparent' if n in (12,14,15,16) and not (a.equipment_fixed and n in (12,14,15)) and not (n==16 and a.frame16) else 'edge review pending' if n==4 and not a.frame04 else 'loop review pending'
  if n==16 and not a.frame16:issue+='; both boots lifted; support lost'
  if n==15:issue+='; descent phase needs review'
  row={'frame':n,'path':str(source.resolve()),'sha256':sha(source),'source_size':source_size,'source_kind':kind,'preview_world_size':[1024,1024],
       'display_only_resampling':source_size!=[1024,1024],'height_in_equal_world_pixels':int(y.max()-y.min()+1),
       'body_scale':float(np.sqrt(np.count_nonzero(aa[:,256:768])/(1024*1024))),'issue':issue,'approval':'pending_or_rejected_diagnostic_only'}
  rows.append(row)
 for mode,color in [('dark',(30,38,46)),('light',(240,238,228))]:
  text='white' if mode=='dark' else 'black'
  sheet=Image.new('RGB',(2048,2240),color);draw=ImageDraw.Draw(sheet)
  loops=[]
  for i,im in enumerate(world):
   display=Image.new('RGB',(1024,1024),color);display.paste(im,(0,0),im)
   x=(i%4)*512;y=(i//4)*560;sheet.paste(display.resize((512,512),Image.Resampling.LANCZOS),(x,y+32))
   draw.text((x+8,y+8),f'NW{i+1:02d} | {rows[i]["source_size"][0]}px | '+('REVISE' if i+1 in (12,14,15,16) else 'pending'),fill=text)
   loop=display.resize((512,512),Image.Resampling.LANCZOS);loops.append(loop)
  sheet.save(out/f'NW-contact-{mode}.png')
  loops[0].save(out/f'NW-diagnostic-30ms-{mode}.gif',save_all=True,append_images=loops[1:],duration=[30]*16,loop=0,optimize=False,disposal=2)
  seam=Image.new('RGB',(2560,600),color);sd=ImageDraw.Draw(seam)
  for col,n in enumerate((13,14,15,16,1)):
   display=Image.new('RGB',(1024,1024),color);display.paste(world[n-1],(0,0),world[n-1]);seam.paste(display.resize((512,512),Image.Resampling.LANCZOS),(col*512,48));sd.text((col*512+12,16),f'NW{n:02d} '+rows[n-1]['issue'],fill=text)
  seam.save(out/f'NW-seam13-14-15-16-01-{mode}.png')
  # Full-size lower-body comparison keeps 1024-world-pixel geometry for pose judgment.
  feet=Image.new('RGB',(5120,440),color);fd=ImageDraw.Draw(feet)
  for col,n in enumerate((13,14,15,16,1)):
   patch=world[n-1].crop((0,650,1024,1024));feet.paste(patch,(col*1024,48),patch);fd.text((col*1024+12,16),f'NW{n:02d} actual lower body / equal world scale',fill=text)
  feet.save(out/f'NW-feet13-14-15-16-01-{mode}.png')
 embedded=[dict(row,image='data:image/png;base64,'+base64.b64encode(Path(row['path']).read_bytes()).decode('ascii')) for row in rows]
 html=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>04 NW 诊断预览：未批准</title><style>body{margin:24px;background:#eee9dc;color:#173833;font:16px system-ui}h1{font-size:24px}button,select{font:inherit;margin:8px;padding:8px}canvas{width:min(74vw,720px);height:auto;background:#20262e;border:1px solid #777}#frames{display:flex;flex-wrap:wrap;max-width:780px}#frames button.active{background:#175d57;color:white}pre{white-space:pre-wrap;max-width:900px}</style><h1>04 山岳守卫 · NW 16帧诊断预览（未批准）</h1><p>30毫秒/帧，480毫秒/周期。旧512帧只按相同世界尺寸显示；导出素材未放大或修改。此页只供诊断。逐帧问题见下方记录，装备修复不代表步态批准。</p><button id="play">播放</button><button id="prev">上一帧</button><button id="next">下一帧</button><select id="speed"><option value="30">30 ms / 帧</option><option value="120">120 ms / 帧诊断</option></select><select id="bg"><option value="#20262e">深底</option><option value="#f0eee4">浅底</option></select><br><canvas id="canvas" width="1024" height="1024"></canvas><div id="frames"></div><pre id="info"></pre><script>const timeline=document.getElementById('frames'),play=document.getElementById('play'),prev=document.getElementById('prev'),next=document.getElementById('next'),speed=document.getElementById('speed'),bg=document.getElementById('bg'),info=document.getElementById('info');const data=__DATA__;let frame=0,playing=false,last=0,elapsed=0;const c=document.getElementById('canvas'),ctx=c.getContext('2d'),ims=data.map(r=>{const im=new Image();im.src=r.image;return im;});const buttons=data.map((r,i)=>{const b=document.createElement('button');b.textContent=String(r.frame).padStart(2,'0');b.onclick=()=>{frame=i;draw()};timeline.appendChild(b);return b;});function draw(){ctx.clearRect(0,0,1024,1024);ctx.drawImage(ims[frame],0,0,1024,1024);const r=data[frame];info.textContent='NW'+String(r.frame).padStart(2,'0')+' | '+r.source_size.join('×')+' | '+r.source_kind+'\n'+r.issue+'\nSHA256: '+r.sha256+'\n'+r.path;buttons.forEach((b,i)=>b.className=i===frame?'active':'')}play.onclick=()=>{playing=!playing;play.textContent=playing?'暂停':'播放';elapsed=0};prev.onclick=()=>{frame=(frame+15)%16;draw()};next.onclick=()=>{frame=(frame+1)%16;draw()};bg.onchange=()=>c.style.background=bg.value;function tick(t){if(last&&playing){elapsed+=t-last;const ms=+speed.value;if(elapsed>=ms){const step=Math.floor(elapsed/ms);frame=(frame+step)%16;elapsed-=step*ms;draw()}}last=t;requestAnimationFrame(tick)}Promise.all(ims.map(im=>im.decode())).then(()=>{draw();requestAnimationFrame(tick)});</script></html>'''.replace('__DATA__',json.dumps(embedded,ensure_ascii=False))
 (out/'index.html').write_text(html,encoding='utf-8')
 gif_checks=[]
 for name in ('dark','light'):
  f=out/f'NW-diagnostic-30ms-{name}.gif';im=Image.open(f);durations=[]
  for n in range(im.n_frames):im.seek(n);durations.append(im.info['duration'])
  assert im.n_frames==16 and durations==[30]*16
  gif_checks.append({'path':str(f),'sha256':sha(f),'frames':im.n_frames,'durations_ms':durations,'cycle_ms':sum(durations)})
 write(out/'diagnostic-manifest.json',{'schema':'qdao-nw-diagnostic-v1','created_at_utc':datetime.now(timezone.utc).isoformat(),'status':'diagnostic_only_not_approved','character':CHAR,'direction':'NW','frame_duration_ms':30,'cycle_duration_ms':480,'frames':rows,'gif_checks':gif_checks,'runtime_assembly':False,'source_assets_modified':False,'known_rework_slots':([15] + ([] if a.frame16 else [16])) if a.equipment_fixed else [12,14,15,16]})
 print(json.dumps({'output':str(out),'frame_count':len(rows),'known_rework_slots':([15] + ([] if a.frame16 else [16])) if a.equipment_fixed else [12,14,15,16],'approval':False},indent=2))
if __name__=='__main__':main()
