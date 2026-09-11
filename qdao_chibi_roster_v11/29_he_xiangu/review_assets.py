from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, importlib.util
import numpy as np
char=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('rp',char.parent/'process_roster.py');rp=importlib.util.module_from_spec(spec);spec.loader.exec_module(rp)
dirs=rp.DIRECTIONS
review=Image.new('RGB',(1100,8*270),(233,231,224));draw=ImageDraw.Draw(review)
allhash=[];gifdur={};frames={};review_paths=[]
portrait=Image.open(char/'portrait.png');assert portrait.size==(1024,1024) and portrait.mode=='RGBA'
for row,d in enumerate(dirs):
    draw.text((5,row*270+115),d,fill=(20,60,50))
    frames[d]=[]
    for i in range(4):
        im=Image.open(char/'walk'/d/f'{i+1:02}.png');assert im.size==(512,512) and im.mode=='RGBA'
        assert rp.foot_anchor(im)[1]==471
        bb=im.getbbox();assert bb[0]>0 and bb[1]>0 and bb[2]<512 and bb[3]<512
        a=np.asarray(im);assert np.any(a[:,:,3]==0) and np.any(a[:,:,3]>240)
        allhash.append(hashlib.sha256(im.tobytes()).hexdigest());frames[d].append(im.copy())
        bg=Image.new('RGBA',(512,512),(233,231,224,255));bg.alpha_composite(im);bg.thumbnail((256,256));review.paste(bg.convert('RGB'),(55+i*260,row*270));draw.text((55+i*260,row*270+256),f'{d} {i+1}',fill=(20,60,50))
    strip=Image.open(char/'walk'/d/'strip.png');assert strip.size==(2048,512) and strip.mode=='RGBA'
    gif=Image.open(char/'walk'/d/'walk.gif');assert gif.n_frames==4
    dur=[]
    for i in range(gif.n_frames):
        gif.seek(i);dur.append(gif.info['duration'])
    assert dur==[120]*4;gifdur[d]=dur
assert len(set(allhash))==32
review.save(char/'processing'/'visual-review.jpg',quality=94)
gifframes=[]
for i in range(4):
    sheet=Image.new('RGBA',(4*256,2*280),(233,231,224,255));draw=ImageDraw.Draw(sheet)
    for n,d in enumerate(dirs):
        im=frames[d][i].resize((256,256),Image.Resampling.LANCZOS);sheet.alpha_composite(im,((n%4)*256,(n//4)*280));draw.text(((n%4)*256+10,(n//4)*280+260),d,fill=(20,60,50,255))
    gifframes.append(sheet.convert('RGB'))
gifframes[0].save(char/'processing'/'walk-preview.gif',save_all=True,append_images=gifframes[1:],duration=120,loop=0,disposal=2)
result={'portrait':'1024x1024 RGBA','independent_walk_frames':32,'unique_frame_hashes':32,'frame_size':[512,512],'directions':8,'strips':'2048x512 RGBA','gifs':8,'gif_frames_each':4,'duration_ms':120,'all_feet_y':471}
(char/'processing'/'artifact-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
