from pathlib import Path
import sys, json
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
sys.path.insert(0, str(BASE))
import production as p
p.ROOT = ROOT
STYLE = Path('D:/work/image/designs/gameplay-ui/04-guild.png')

def update(stage='native_details'):
    names = sorted(fp.stem for fp in (ROOT/'native').glob('p??.png'))
    p.write(ROOT/'progress.json', {'updatedAt':p.stamp(),'tile':'r10_c13','nativeDetailPatches':len(names),'expectedPatches':16,'completePixelCandidateTiles':int((ROOT/'tiles/r10_c13-candidate.png').exists()),'formalAccepted':0,'wholeCityComplete':False,'clientAccepted':False,'stage':stage})
    p.write(ROOT/'current-work.json', {'updatedAt':p.stamp(),'tile':'r10_c13','stage':stage,'completedPatches':names,'missingPatches':[f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in names]})
    if names:
        board=Image.new('RGB',(4096,4096),(214,217,216));d=ImageDraw.Draw(board)
        for r in range(1,5):
            for c in range(1,5):
                name=f'p{r}{c}';fp=ROOT/'native'/(name+'.png')
                if fp.exists():
                    im=Image.open(fp).convert('RGB');assert im.size==(1254,1254);board.paste(im.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
                else:d.text(((c-1)*1024+30,(r-1)*1024+30),name+' PENDING',fill=(70,70,70))
        dest=ROOT/'current-preview.png';board.resize((1254,1254),Image.Resampling.LANCZOS).save(dest);p.derived(dest,[ROOT/'native'/(n+'.png') for n in names],{'method':'native core review montage, downscaled preview','missingPatchesArePlaceholders':len(names)<16,'notProductionArt':True})

def guides():
    src=ROOT/'references/structure-v1.png';im=Image.open(src).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS)
    state=p.read(ROOT/'evidence/boundary-state.json');anchor=Path(state['north']['anchor']);assert p.sha(anchor)==state['north']['anchorSha256'];im.paste(Image.open(anchor).convert('RGB'),(115,0))
    canvas=ROOT/'references/layout-canvas-only.png';im.save(canvas);p.derived(canvas,[src,anchor],{'method':'resample layout guide only; insert fixed exact north115px at [115,0]','neverFinalPixels':True})
    index=[]
    for r in range(1,5):
        for c in range(1,5):
            name=f'p{r}{c}';box=((c-1)*1024,(r-1)*1024,(c-1)*1024+1254,(r-1)*1024+1254);dest=ROOT/'guides'/(name+'.png');im.crop(box).save(dest);p.derived(dest,[canvas],{'method':'native-size geometry guide crop; not HD art','boxLTRB':box})
            index.append({'id':name,'file':str(dest),'globalCoreXYWH':[49152+(c-1)*1024,36864+(r-1)*1024,1024,1024]})
    p.write(ROOT/'guides/index.json',{'patches':index,'finalUseForbidden':True});update('guides_ready')

def prepare(name,scene):
    row=int(name[1]);col=int(name[2]);state=p.read(ROOT/'evidence/boundary-state.json')
    if row==1:assert state['north'].get('parentApproved')
    if col==1:assert str(row) in state['west']['rows'], 'West native context is not ready'
    refs=[(ROOT/'guides'/(name+'.png')).as_posix(),STYLE.as_posix()];notes=[]
    for dr,dc,direction,overlap in [(0,-1,'LEFT','target left230px matches neighbor right230px'),(0,1,'RIGHT','target right230px matches neighbor left230px'),(-1,0,'UPPER','target top230px matches neighbor bottom230px'),(1,0,'LOWER','target bottom230px matches neighbor top230px')]:
        nr,nc=row+dr,col+dc;fp=ROOT/'native'/f'p{nr}{nc}.png'
        if 1<=nr<=4 and 1<=nc<=4 and fp.exists():refs.append(fp.as_posix());notes.append(f'Image {len(refs)} is completed {direction} neighbor p{nr}{nc}: {overlap}.')
    if col==1:
        fp=Path(state['west']['rows'][str(row)]['native']);assert p.sha(fp)==state['west']['rows'][str(row)]['sha256'];refs.append(fp.as_posix());notes.append(f'Image {len(refs)} is completed WEST TILE native patch: target left230px matches its right230px. Preserve this overlapping structure exactly.')
    prompt='Use case: sketch-to-render. Native detailed art patch '+name+' for r10_c13 in the continuous isometric Taoist Q fantasy harbor map 五行奇谈. Image 1 is EXACT target crop and geometry guide, reference pixels only. Image 2 is approved PRIMARY PAINTING STYLE, never copy UI. '+' '.join(notes)+' REDRAW ONLY Image 1 at identical crop and scale with crisp native clean hand-painted detail. Scene: '+scene+' Preserve exact camera, boundaries, object counts, silhouettes, edge tangent endpoints, overlap order, material identity, light and cool shadows. Neighbor inputs only constrain overlapping geometry/material; do not substitute their whole composition. '+('Top115px is fixed original north-tile context; continue the same outlines and surface naturally into the target, removing its artificial horizontal splice at y115 without moving geometry. ' if row==1 else '')+'Bright clean rounded full Taoist Q fantasy painting: restrained texture, clear rounded bevels, delicate warm wood/ceramic and clean cream paving; no added objects, no extra tile subdivision or denser foliage. Keep all cropped objects cropped. No text, labels, UI, border, watermark, dense cracks, noise, photorealism, plastic glare, blur or sharpen halos. Square exact crop.'
    fp=ROOT/'prompts'/(name+'.prompt.txt');fp.write_text(prompt,encoding='utf8');call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};p.write(ROOT/'prompts'/(name+'.call.json'),call);return call

def ingest(source,name,role='native_detail'):
    assert not (ROOT/('references' if role=='layout_only' else 'native')/(name+'.png')).exists(),'Existing asset requires a distinct version'
    call=p.read(ROOT/'prompts'/(name+'.call.json'));dest=p.ingest(source,name,str(ROOT/'prompts'/(name+'.prompt.txt')),call['referenced_image_paths'],role);assert Image.open(dest).size==(1254,1254)
    rec=p.read(str(dest)+'.generation.json');rec['configSnapshot']=p.read(ROOT/'evidence/model-verification.json')['configSnapshot'];rec['evidence']['toolOutputHintFile']=str(ROOT/'evidence'/(name+'.tool-result.json'));rec['visualInspection']={'at':p.stamp(),'scope':'Tool output viewed at native dimensions against geometry guide and approved style; complete seam QA pending'};p.write(str(dest)+'.generation.json',rec);update();print(dest)

if __name__=='__main__':
    if sys.argv[1]=='guides':guides()
    elif sys.argv[1]=='prepare':print(json.dumps(prepare(sys.argv[2],sys.argv[3]),ensure_ascii=True))
    elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
