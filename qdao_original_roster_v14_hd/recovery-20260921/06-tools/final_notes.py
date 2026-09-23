"""Write final delivery guidance after the offline review, preserving its limits."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;REC=HERE.parent;FINAL=REC/'06-final';ROOT=REC.parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(FINAL/'manifest.json');restored=m.get('legacy_final_copies_ai_restored',False)
dirs=['N','NE','E','SE','S','SW','W','NW']
for mode,bg in [('dark',(30,38,46)),('light',(240,238,228))]:
 sheet=Image.new('RGB',(2048,1120),bg)
 for n,d in enumerate(dirs):
  original_im=Image.open(FINAL/f'runtime/idle/{d}.png');im=original_im.resize((512,512),Image.Resampling.LANCZOS);x=n%4*512;y=n//4*560
  sheet.paste(im,(x,y+32),im);ImageDraw.Draw(sheet).text((x+15,y+10),d+' / independent idle / '+str(original_im.width)+'px',fill='white' if mode=='dark' else 'black')
 sheet.save(FINAL/f'preview/idle-contact-{mode}.png')
out=(FINAL/'provenance');out.mkdir(exist_ok=True)
for base,fn in [('work-NE-final','NE_DELIVERY.json'),('work-N-NE','N_DELIVERY.json'),('work-W-NW','WNW_DELIVERY.json')]:
 p=HERE/base/fn
 if p.exists():shutil.copy2(p,out/fn)
for base,prefix in [('work-NE-final','NE'),('work-N-NE','N'),('work-W-NW','W-NW')]:
 for name in ['README.md','REVIEW.md','VERIFICATION.json']:
  p=HERE/base/name
  if p.exists():shutil.copy2(p,out/(prefix+'-'+name))
 for name in ['visual-review.json','numeric-verification.json']:
  p=HERE/base/'review'/name
  if p.exists():shutil.copy2(p,out/(prefix+'-'+name))
shutil.copy2(REC/'06-work/candidate/06_thunder_caster_boy/review/reconstruction-E.json',out/'E-reconstruction.json')
readme='''# 06 雷法少年：最终动作与离线预览

本目录是本窗口选定的交付入口。`runtime/walk/{N,NE,E,SE,S,SW,W,NW}/01.png` 至 `16.png` 共128张真实行走图；`runtime/idle/方向.png` 共8张独立站立图。打开 [index.html](index.html) 查看八方向30ms循环、逐帧、深浅底、正常/放大及15→16→01→02接缝。

112张行走图为原生1254×1254完整单帧导出的1024×1024透明PNG；南向16张和独立站立8张沿用既有512×512原字节，未放大冒充高清。每帧图像唯一；旧站立图不是行走帧替代。`manifest.json` 保存逐帧SHA、尺寸与选用来源，`provenance/selected-sources.json` 保存完整文字来源、提示词、请求/回执、处理参数、原图尺寸与SHA。实际模型/质量未由内置入口披露的保持未确认，配置目标不作为实际返回证据；收费API为0。

接入时每方向顺序为01→16→01，30ms/帧，480ms/圈。1024图的脚点为[512,942]，512旧图为[256,471]；等世界尺寸显示可对应104/52 PPU。脚点归一化约[0.5,0.919921875]（图像左上原点），Unity等左下原点约[0.5,0.080078125]，具体导入器坐标约定须核对。不得对每帧按人物包围盒单独缩放。GIF仅作预览，不作为游戏透明资源。

角色正式设计仍在 [4096肖像](../../../q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png)，身份与风格未更换。`preview/idle-contact-*.png` 是站立总览，八方向深浅GIF均含16帧×30ms。

验收范围与旧图保留限制见 [REVIEW.md](REVIEW.md)。本窗口只完成素材制作和离线检查；没有进行Unity导入、正式客户端运行或发布，没有Git提交/推送，没有启动其他角色。原图、拒稿、回退与中间图在成品和文字证据核验后按用户授权精简，结果见`cleanup-result.json`。
'''
(FINAL/'README.md').write_text(readme,encoding='utf-8')
if restored:
 readme=readme.replace('112张行走图为原生1254×1254完整单帧导出的1024×1024透明PNG；南向16张和独立站立8张沿用既有512×512原字节，未放大冒充高清。','最终136张动作全部为1024×1024透明PNG，分别由136张原生1254×1254完整单帧导出。其中南向16张与独立站立8张以原512图为姿势参考，经内置AI逐图修边重绘；不是将旧512栅格直接放大冒充高清。原24张512文件仍在原V13路径逐字节保留，SHA基线见provenance/preserved-old-byte-baseline.json；游戏接入选用本目录的新修复版。')
 readme=readme.replace('1024图的脚点为[512,942]，512旧图为[256,471]；等世界尺寸显示可对应104/52 PPU。','本包1024图的脚点统一[512,942]，对应104 PPU；保留在旧路径的512原文件不属于本包选用动作。')
 (FINAL/'README.md').write_text(readme,encoding='utf-8')
print(json.dumps({'written':'README and idle contacts','final':str(FINAL)}))
