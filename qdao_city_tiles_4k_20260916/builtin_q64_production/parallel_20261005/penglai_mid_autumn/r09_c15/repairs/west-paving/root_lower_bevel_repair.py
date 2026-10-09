from pathlib import Path
import sys,shutil
F=Path(__file__).resolve().parent;ROOT=F.parents[2];sys.path.insert(0,str(ROOT))
from production import read,write,sha,now,deriv,REPO
from PIL import Image
P='root-lower-bevel-v12'
def prepare():
    base=F.parents[1]/'output/r09_c15-candidate.png';west=ROOT/'r09_c14/output/r09_c14-candidate.png';proposal=F/'proposed-joint-v9.png'
    assert sha(base)=='957194bcbf888cac88f8b0a3d79d055f8ce69a76846590f174eee7e6f8b9e456'
    assert sha(west)=='3e8b712967d34934645eb60a94ab57981e944ddcb7557c4dd765546d87be30b2'
    cur=Image.open(base).convert('RGB');cur.paste(Image.open(proposal).crop((320,80,920,990)),(0,2840))
    im=Image.new('RGB',(1254,1254));im.paste(Image.open(west).convert('RGB').crop((3469,2842,4096,4096)),(0,0));im.paste(cur.crop((0,2842,627,4096)),(627,0))
    target=F/(P+'-target.png');assert not target.exists();im.save(target)
    deriv(target,[base,west,proposal],dict(kind='exact native recentered lower W bevel repair target',canvasGlobalXYWH=[57344-627,32768+2842,1254,1254],trueWestCropLTRB=[3469,2842,4096,4096],currentCropLTRB=[0,2842,627,4096],candidateProposalPaste=dict(sourceCropLTRB=[320,80,920,990],pasteXY=[0,2840]),scale=1,productionPixels=False))
    prompt='''Use case: precise-object-edit. Edit Image1 at its exact native1254 square framing. It is a continuous close-up of blue-violet stone paving and warm wooden rails in a Daoist chibi night map. Image2 is approved art STYLE only; do not copy its UI, writing or objects.
Fix ONLY one tiny seam of the existing diagonal stone-floor grout and its pale bevel, near x627, y800..910. At x627 the dark groove and its bright edge have a small endpoint step and a short straight vertical paint cut. LEFT of x627 is fixed, correct neighboring artwork: preserve it. Repaint the tiny continuation immediately RIGHT of x627, joining the same existing dark groove and pale bevel at exactly the same heights, slopes, widths and colors as the left-side endpoints. Flow naturally back into the already correct right-side groove within roughly160 pixels; no new groove, extra parallel highlight, duplicated bevel, kink, notch, rectangular paint block, ridge or blur. Keep the surrounding stone brushwork continuous across x627.
Preserve all other grout lines and every post, railing, wood-grain feature, light/shadow boundary and object position. Only x627..795,y755..908 requires repair. Do not move, enlarge or redesign the paving, change warm/cool lighting globally, add details, or complete any cropped object. Retain the exact1254 camera and crop, clean painted stone texture, readable rounded forms. No text, labels, borders, grain or sharpening halos. Return an opaque image. This is an extremely small endpoint alignment repair; everything else is unchanged.'''
    pp=F/(P+'.prompt.txt');pp.write_text(prompt,encoding='utf-8');style=REPO/'designs/gameplay-ui/04-guild.png'
    call=dict(prompt=prompt,referenced_image_paths=[str(target),str(style)],transparent_background=False);write(F/(P+'.call.json'),call)
    write(F/(P+'.request.json'),dict(preparedAt=now(),configSnapshot=read(REPO/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,**call),prompt=str(pp),promptSha256=sha(pp),references=[dict(file=str(p),sha256=sha(p),role=role) for p,role in [(target,'exact native joint target'),(style,'approved style')]],mapping=dict(canvasGlobalXYWH=[56717,35610,1254,1254],candidateXYAtCanvasOrigin=[-627,2842],candidateBoxLTRB=[0,3597,168,3750]),sourcePixelScale=1))
def save(source):
    src=Path(source);dst=F/(P+'.png');assert not dst.exists() and Image.open(src).size==(1254,1254);req=read(F/(P+'.request.json'))
    for x in req['references']:assert sha(x['file'])==x['sha256']
    shutil.copy2(src,dst);write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin with no model or quality selector and no actual returned version evidence.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],mapping=req['mapping'],sourceUpscaled=False,resizedAfterGeneration=False,accepted=False))
    print(str(dst));print(sha(dst))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='save':save(sys.argv[2])
