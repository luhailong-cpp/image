"""Assemble final roster index and visual review from accepted generated sprites."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib
ROOT=Path(__file__).resolve().parent
ROSTER=[('23_lantern_courier','灯穗小使'),('24_crane_hermit','云鹤散人'),('25_lion_drum_guard','狮鼓护卫'),('26_osmanthus_healer','桂香药婆'),('27_ink_kite_ranger','墨鸢游侠'),('28_moon_rabbit_artificer','月兔机关师')]
DIRS=['S','SW','W','NW','N','NE','E','SE']
LABELS={'S':'正面','SW':'左前','W':'向左','NW':'左后','N':'背面','NE':'右后','E':'向右','SE':'右前'}
def font(n):
    return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def fit(im,sz):
    im=im.convert('RGBA'); box=im.getbbox()
    if box: im=im.crop(box)
    im.thumbnail(sz,Image.Resampling.LANCZOS)
    return im

def find_frame(base,d,n):
    for p in [base/'walk'/d/f'{n:02d}.png',base/'walk'/d.lower()/f'{n:02d}.png',base/'walk'/d.lower()/f'frame-{n:02d}.png']:
        if p.exists(): return p
    raise FileNotFoundError(f'{base.name} {d} {n}')

def main():
    overview=Image.new('RGB',(1500,1200),'#f3efe3'); draw=ImageDraw.Draw(overview)
    draw.text((60,30),'五行奇谈 · 六位新伙伴',font=font(40),fill='#243e35')
    draw.text((60,88),'独立造型 / 直发 / 道家 Q 版 / 八方向真实行走帧',font=font(21),fill='#647266')
    entries=[]
    for i,(slug,name) in enumerate(ROSTER):
        base=ROOT/slug; p=base/'portrait.png'
        assert p.exists(),str(p)
        x=35+(i%3)*490; y=150+(i//3)*500
        draw.rounded_rectangle((x,y,x+470,y+474),radius=18,fill='#e8e4d6',outline='#d6d0bd',width=1)
        im=fit(Image.open(p),(420,388)); overview.paste(im,(x+(470-im.width)//2,y+16+388-im.height),im)
        draw.text((x+24,y+419),f'{slug[:2]}  {name}',font=font(27),fill='#243e35')
        groups={}; all_hash=[]; frame_count=0
        for d in DIRS:
            files=[]; hashes=[]
            for n in range(1,5):
                f=find_frame(base,d,n); im=Image.open(f)
                assert im.mode=='RGBA' and im.size==(512,512),(f,im.mode,im.size)
                alpha=im.getchannel('A'); assert alpha.getextrema()==(0,255),f
                b=alpha.getbbox(); assert b and b[0]>0 and b[1]>0 and b[2]<512 and b[3]<512,(f,b)
                digest=hashlib.sha256(f.read_bytes()).hexdigest()
                hashes.append(digest); all_hash.append(digest); files.append(f.relative_to(ROOT).as_posix()); frame_count+=1
            assert len(set(hashes))==4, f'{slug} {d} duplicated frames'
            groups[d]={'frames':files,'duration_ms':120,'loop':True}
        assert len(set(all_hash))==32, f'{slug} duplicated directional frames'
        entries.append({'id':slug[:2],'slug':slug,'name_zh':name,'portrait':p.relative_to(ROOT).as_posix(),'frame_count':frame_count,'directions':groups,'cell_size':[512,512],'foot_origin_top_left':[256,471]})
    overview.save(ROOT/'roster-overview.jpg',quality=94,subsampling=0)
    # This canvas only composes accepted generated frames; it draws no character art.
    review=[]
    for d in DIRS:
        for cycle in range(2):
            for n in range(1,5):
                page=Image.new('RGB',(900,650),'#eeebdf'); dc=ImageDraw.Draw(page)
                dc.text((28,16),f'八方向移动  ·  {LABELS[d]}  {d}',font=font(27),fill='#243e35')
                for i,(slug,name) in enumerate(ROSTER):
                    x=(i%3)*300; y=65+(i//3)*285
                    im=Image.open(find_frame(ROOT/slug,d,n)).convert('RGBA').resize((260,260),Image.Resampling.LANCZOS)
                    page.paste(im,(x+20,y),im)
                    dc.text((x+82,y+245),name,font=font(20),fill='#344e44')
                review.append(page)
    review[0].save(ROOT/'movement-overview.gif',save_all=True,append_images=review[1:],duration=120,loop=0,optimize=False,disposal=2)
    payload={'title':'五行奇谈 · 六位新伙伴','date':'2026-09-10','status':'image_assets_delivered','generator':'built-in image_gen','model_and_quality_forced':False,'characters':entries,'total_portraits':6,'total_unique_movement_frames':192,'direction_order':DIRS,'client_integration':'Not performed. Existing client expects eight frames and a single hardcoded role; consume these four-frame manifests explicitly.'}
    (ROOT/'manifest.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'portraits':6,'movement_frames':192,'all_directional_frames_unique':True,'overview':str(ROOT/'roster-overview.jpg'),'animation':str(ROOT/'movement-overview.gif')},ensure_ascii=False))
if __name__=='__main__':main()
