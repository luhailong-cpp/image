"""Prepare native context and reference-only geometry inside this task directory."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
from PIL import Image
import numpy as np

TASK = Path(__file__).resolve().parent
ROOT = next(p for p in TASK.parents if (p/'config/image-generation.json').is_file())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p, obj):
    p.resolve().relative_to(TASK)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def info(p):
    p=Path(p).resolve()
    return {'file':str(p),'sha256':sha(p)}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bottom',type=Path,required=True)
    ap.add_argument('--bottom-sha',required=True)
    ap.add_argument('--fragment',type=Path,required=True)
    ap.add_argument('--fragment-sha',required=True)
    ap.add_argument('--patch',default='r04_c03')
    ap.add_argument('--fragment-box',type=int,nargs=4,default=[909,2957,2163,4096])
    ap.add_argument('--version',default='v1')
    ap.add_argument('--source-checkpoint',type=Path)
    args=ap.parse_args()
    h=read(TASK/'handoff.json')
    if not h['readyForProduction']:
        assert args.source_checkpoint, 'A verified task-local checkpoint is required after upstream interruption'
        args.source_checkpoint.resolve().relative_to(TASK)
        checkpoint=read(args.source_checkpoint)
        assert checkpoint['resumeAuthorizedByUser'] and checkpoint['sourcePairVerified']
        assert checkpoint['bottom']['sha256']==args.bottom_sha
        assert checkpoint['fragment']['sha256']==args.fragment_sha
    assert sha(args.bottom)==args.bottom_sha and sha(args.fragment)==args.fragment_sha
    row,col=int(args.patch[1:3]),int(args.patch[5:7])
    assert 1<=row<=4 and 1<=col<=4
    out=TASK/'r08_c10'/f'{args.patch}-{args.version}'
    out.mkdir(parents=True,exist_ok=False)
    bx,by=(col-1)*1024-115,(row-1)*1024-115
    global_box=[36864+bx,28672+by,36864+bx+1254,28672+by+1254]
    canvas=Image.new('RGBA',(1254,1254),(0,0,0,0))
    def paste_global(source, source_box):
        lx,ty=max(bx,source_box[0]),max(by,source_box[1])
        rx,bt=min(bx+1254,source_box[2]),min(by+1254,source_box[3])
        if lx>=rx or ty>=bt: return
        im=Image.open(source).convert('RGBA')
        assert im.size==(source_box[2]-source_box[0],source_box[3]-source_box[1])
        canvas.paste(im.crop((lx-source_box[0],ty-source_box[1],rx-source_box[0],bt-source_box[1])),(lx-bx,ty-by))
    paste_global(args.fragment,args.fragment_box)
    paste_global(args.bottom,[0,4096,4096,8192])
    canvas.save(out/'context.png')
    known=np.asarray(canvas)[:,:,3]==255
    assert known.any() and not known.all()
    master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
    assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
    with Image.open(master) as im:
        im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in global_box)).save(out/'layout-reference-only.png')
    refs=[out/'context.png',out/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
    prompt='''Use case: precise-object-edit / outpainting. Continue one exact native-detail crop of the original game 五行奇谈. Return one square opaque image with the same framing as image 1.
Image 1 is the EDIT TARGET: a 1254 by 1254 crop with authentic finished map pixels and transparent missing area. Preserve the visible stone outlines, curve tangents, bevel widths, carved petal contours, subtle colors, scale and lighting precisely. Paint only the transparent missing map region, continuing the same structures seamlessly. Do not reinterpret existing visible artwork. Opaque strips show the directly adjacent continuation of the same world surface. Existing outlines meeting a transparency edge must continue from the very same point and tangent.
Image 2 is ONLY broad canonical layout at exactly the same global coordinates, to guide what enters the missing area. Its blur and small accidental marks are not material detail. Never copy its enlarged pixels. It is subordinate to the exact edges of image 1. Draw newly rendered sharp stone relief, broad smooth clean stone planes, ivory stone and restrained warm gold edging, slate gray inset and clean gently rounded bevels. Do not invent extra seams or carvings. There is no new building, character, foliage or separate prop here.
Image 3 is the user's approved primary STYLE reference ONLY: bright clean rounded full Q-version Daoist fantasy handpainted rendering, finely controlled contour shading and quiet surface texture. Do not import its UI, lettering, icons, figures or frames.
The transparent boundary is not a physical edge. No vertical or horizontal line, bevel, panel, shadow, color rectangle or inset may appear there just because it was transparent. Preserve broad curved plaza ring structures and existing relief. Stone must have subtle broad low-contrast shading only: no cracks, broken pieces, mosaic noise, marble veins, speckles, grunge or cloudy polygon texture. No text, UI, watermark, border, transparent output, rescaling, zooming, rotation or camera shift. Highest visual finish available through the host.'''
    (out/'prompt.txt').write_text(prompt,encoding='utf-8')
    payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
    write(out/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'patch':args.patch,'tile':'r08_c10','globalCropLTRB':global_box,'tileLocalCropLTRB':[bx,by,bx+1254,by+1254],'knownPixels':int(known.sum()),'missingPixels':int((~known).sum()),'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json')})
    write(out/'preparation.json',{'handoff':info(TASK/'handoff.json'),'taskLocalSourceCheckpoint':info(args.source_checkpoint) if args.source_checkpoint else None,'references':[info(p) for p in refs],'nativeInputs':[info(args.fragment),info(args.bottom)],'master':info(master),'nativeScale':1,'guidePixelsAllowedInFinal':False})
    for p in refs[:2]:
        write(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'derivedFrom':[info(args.fragment),info(args.bottom)] if p.name=='context.png' else [info(master)],'operation':'Exact native ownership crop and transparent missing region' if p.name=='context.png' else 'Reference-only enlarged canonical crop; forbidden as final pixels','newModelCalls':0})
    write(TASK/'current-work.json',{'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_expansion_ready_to_generate','tile':'r08_c10','patch':args.patch,'request':str(out/'request.json'),'wholeCityComplete':False})
    print(json.dumps({'directory':str(out),'globalCropLTRB':global_box,'knownPixels':int(known.sum()),'missingPixels':int((~known).sum())}))
if __name__=='__main__': main()
