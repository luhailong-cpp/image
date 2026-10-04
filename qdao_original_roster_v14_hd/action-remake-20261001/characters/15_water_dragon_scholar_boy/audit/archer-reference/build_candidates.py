from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib
B=Path(__file__).resolve().parents[2]
A=B/'audit'/'archer-reference'
SEL={"NW":[3,2,1,1,1,3,1,1,2,1,2,4,4,2,1,1],"SW":[3,1,1,2,3,2,0,1,1,1,0,2,1,1,1,1]}
native={x['slot']:x for x in json.loads((A/'native-input-map.json').read_text(encoding='utf-8-sig'))}
out=A/'preview'
out.mkdir(exist_ok=True)
rows=[]
for d,versions in SEL.items():
    frames=[]
    for n,v in enumerate(versions,1):
        slot=f'run/{d}/{n:02d}'
        key=f'run-{d}-{n:02d}-archer-v{v}' if v else None
        source=B/'sources/new'/f'{key}.png' if v else B/'runtime/run'/d/f'{n:02d}.png'
        if not source.exists():
            print('PENDING',key);continue
        im=Image.open(source).convert('RGBA')
        if v:
            assert im.size==(1254,1254), (key,im.size)
            rt=Image.new('RGBA',(1024,1024)); rt.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
        else: rt=im
        rt.save(out/f'{d}-{n:02d}.png')
        bg=Image.new('RGB',(1024,1024),(230,237,239)); bg.paste(rt,mask=rt.getchannel('A'))
        dr=ImageDraw.Draw(bg);dr.line((0,942,1024,942),fill=(186,207,207),width=2)
        dr.text((25,20),f'{d} {n:02d} / '+(f'archer v{v}' if v else 'retained'),fill=(25,45,65),font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27))
        frames.append(bg)
        rows.append({'slot':slot,'candidateKey':key,'file':str(source).replace('\\','/'),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'generationRecord':f'provenance/generation/{key}.json' if v else native[slot]['originalGenerationRecord'],'reusedOriginal':native[slot],'export':{'native':1254,'scaleCanvasTo':940,'offset':[42,49],'canvas':1024} if v else {'retainedRuntime':True},'staticCandidateReviewed':False,'clientIntegrated':False})
    if len(frames)==16:
        contact=Image.new('RGB',(1600,1680),(230,237,239))
        for i,fr in enumerate(frames): contact.paste(fr.resize((400,400)),((i%4)*400,(i//4)*420))
        contact.save(out/f'{d}-contact.png')
        gif=[fr.resize((512,512)) for fr in frames]
        gif[0].save(out/f'{d}-1200ms.gif',save_all=True,append_images=gif[1:],loop=0,duration=[70,80]*8,disposal=2)
        gif[0].save(out/f'{d}-slow.gif',save_all=True,append_images=gif[1:],loop=0,duration=180,disposal=2)
        for start in range(0,16,4):
            c=Image.new('RGB',(1600,950),(230,237,239))
            for j in range(4):
                fr=frames[start+j]; c.paste(fr.resize((400,400)),(j*400,0))
                crop=fr.crop((160,580,970,1024)); crop.thumbnail((400,520))
                c.paste(crop,(j*400,420))
            c.save(out/f'{d}-{start+1:02d}-{start+4:02d}-details.png')
json.dump({'schemaVersion':1,'scope':'NW/SW local candidate only','cycleMs':1200,'frameMs':75,'dynamicPlaybackObserved':False,'clientIntegrated':False,'rows':rows},(A/'nw-sw-selection.json').open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('rows',len(rows))

