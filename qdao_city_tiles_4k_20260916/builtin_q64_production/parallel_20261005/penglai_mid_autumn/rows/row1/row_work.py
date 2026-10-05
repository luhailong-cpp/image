from pathlib import Path
import sys, shutil, json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from production import read, write, sha, now, deriv, REPO
from PIL import Image
ROW=Path(__file__).resolve().parent

def prepare(col):
    ident=f'p1{col}'
    src=ROOT/'guides'/f'{ident}.png'; target=ROW/f'{ident}-target.png'
    im=Image.open(src).convert('RGB'); sources=[src]
    if col>1:
        left=ROW/f'p1{col-1}.png'; lim=Image.open(left).convert('RGB'); assert lim.size==(1254,1254)
        im.paste(lim.crop((1024,0,1254,1254)),(0,0)); sources.append(left)
    im.save(target); deriv(target,sources,dict(kind='layout_guide_with_native_left_overlap',leftOverlap=230 if col>1 else 115,notProductionPixels=True))
    refs=[target,REPO/'designs/gameplay-ui/04-guild.png']
    prompt=f'''Use case: precise-object-edit.
Asset type: native game map detail patch {ident}, Mid-Autumn appearance of the original 五行奇谈 game, town tile r09_c13.
Image 1 is the EDIT TARGET and exact geometry/lighting guide. Redraw its soft layout-only regions as newly generated crisp native painted detail in the SAME square framing and camera, with precisely the same structure coordinates. It is one tiny cropped patch of a larger continuous map, not a complete scene. Do not zoom out, change composition, add objects, or move edges. Output a single native square at the input framing; retain its1254x1254 dimensions if supported.
The left {230 if col>1 else 115}px is native adjacent context. Match it exactly, carrying brick seams, step edges, wood grain direction, object silhouettes and light through the boundary without a band. Keep all large forms, slab sizes, bevel widths, contour positions and shadow footprints fixed. Restore clean edge definition and subtle organized brushwork within each form rather than adding texture noise.
Image 2 is the user-approved MAIN ART STYLE reference: clean, bright, rounded and full-bodied Daoist chibi hand painting, gentle ivory/jade/warm-gold material, controlled highlights, clear dimensional shapes. Do not borrow UI, characters, writing or frame.
Preserve the first image's Mid-Autumn blue-violet evening stones and gentle warm amber light, warm wood, jade foliage, and existing decorations where visible. Do not create new lamps, furniture, plants, railings, paths or stairs. If a subject is cropped by an edge, keep it cropped at exactly the same place. Preserve road clearance and original doorway/step/rail geometry. No blur, dense grain, cracks, sharpening halos, plastic gloss, bloom, border, text or watermark. Highest visual finish consistent with the approved painting style.'''
    pp=ROW/f'{ident}.prompt.txt'; pp.write_text(prompt,encoding='utf-8')
    req=dict(id=ident,startedAt=now(),tool='image_gen.imagegen',route='builtin',configSnapshot=read(REPO/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,referenced_image_paths=[str(x) for x in refs],transparent_background=False),prompt=str(pp),promptSha256=sha(pp),references=[dict(file=str(x),sha256=sha(x),role=r) for x,r in zip(refs,['edit target: exact geometry and actual native adjacent overlap','main approved style'])],globalBoxLTRB=[49037+(col-1)*1024,32653,50291+(col-1)*1024,33907])
    write(ROW/f'{ident}.request.json',req)
    print(json.dumps(dict(prompt=prompt,referenced_image_paths=[str(x) for x in refs],transparent_background=False),ensure_ascii=True))

def save(col,source):
    ident=f'p1{col}'; req=read(ROW/f'{ident}.request.json'); src=Path(source); dst=ROW/f'{ident}.png'; shutil.copy2(src,dst); im=Image.open(dst); im.load()
    assert im.size==(1254,1254),im.size
    rec=dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=im.width,height=im.height,format=im.format,tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed, no model/quality selectors or returned model/quality metadata.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],globalBoxLTRB=req['globalBoxLTRB'],sourceUpscaled=False,status='native_detail_pending_full_seam_QA',formalAccepted=False)
    write(str(dst)+'.generation.json',rec); print(str(dst))

if __name__=='__main__':
    if sys.argv[1]=='prepare': prepare(int(sys.argv[2]))
    elif sys.argv[1]=='save': save(int(sys.argv[2]),sys.argv[3])
