"""Derived preview-only assets from complete selected candidate directions."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def provenance(out,frames,operation):
    data={'file':str(out.relative_to(ROOT)),'sha256':sha(out),'derivedAt':datetime.now(timezone.utc).isoformat(),'derivedFrom':[{'file':str(p.relative_to(ROOT)),'sha256':sha(p),'generationRecord':str(p.relative_to(ROOT))+'.generation.json'} for p in frames],'operation':operation,'newModelGeneration':False,'visualAcceptance':False}
    Path(str(out)+'.generation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    outdir=ROOT/'preview';outdir.mkdir(exist_ok=True)
    counts={}
    for direction in manifest['directions']:
        rows=[r for r in manifest['frames'] if r['direction']==direction]
        if len([r for r in rows if r.get('candidateStatus')=='present_structurally_valid'])!=16:
            counts[direction]='incomplete_no_animation_created';continue
        paths=[ROOT/r['candidate'] for r in rows]
        original=[Image.open(p).convert('RGBA') for p in paths]
        for label,size,ms in [('normal',128,30),('slow',384,120)]:
            images=[]
            for im in original:
                image=Image.new('RGBA',(size,size),(226,229,235,255));image.alpha_composite(im.resize((size,size),Image.Resampling.LANCZOS));images.append(image)
            out=outdir/f'{direction}-{label}.png'
            images[0].save(out,save_all=True,append_images=images[1:],duration=ms,loop=0,disposal=0,blend=0,format='PNG')
            provenance(out,paths,{'type':'APNG preview','frameCount':16,'durationMilliseconds':ms,'loopMilliseconds':16*ms,'displayPixels':size,'canvasRescaleOnly':True,'poseInterpolation':False})
        contact=Image.new('RGB',(1024,1120),(238,240,245));d=ImageDraw.Draw(contact)
        for i,im in enumerate(original):
            x=(i%4)*256;y=(i//4)*280
            thumb=im.resize((256,256),Image.Resampling.LANCZOS);contact.paste(thumb,(x,y),thumb)
            d.text((x+8,y+259),f'{direction}/{i+1:02d}  t={i*30:03d}ms',fill=(20,25,35))
        out=outdir/f'{direction}-contact.png';contact.save(out)
        provenance(out,paths,{'type':'contact sheet for review','frameCount':16,'columns':4,'noPoseEdits':True})
        counts[direction]='16-frame APNGs and contact sheet created, not visually accepted'
    print(json.dumps(counts))
if __name__=='__main__':main()
