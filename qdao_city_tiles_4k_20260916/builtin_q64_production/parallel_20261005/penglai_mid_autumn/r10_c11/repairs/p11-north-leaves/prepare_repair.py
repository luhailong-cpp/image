from pathlib import Path
import sys, shutil
from PIL import Image
F=Path(__file__).resolve().parent; ROOT=F.parents[2];sys.path.insert(0,str(ROOT))
from production import read,write,sha,now,deriv,REPO
def prepare():
 F.mkdir(parents=True,exist_ok=True);plan=read(F.parents[1]/'plan.json'); n=Path(plan['northCandidate']); p11=F.parents[1]/'native/p11.png';p12=F.parents[1]/'native/p12.png'
 assert sha(n)==plan['northCandidateSha256']
 im=Image.new('RGB',(1254,1254));im.paste(Image.open(n).convert('RGB').crop((0,3469,1254,4096)),(0,0));im.paste(Image.open(p11).convert('RGB').crop((115,115,1254,742)),(0,627));im.paste(Image.open(p12).convert('RGB').crop((230,115,345,742)),(1139,627))
 target=F/'north-leaves-v1-target.png';assert not target.exists();im.save(target)
 deriv(target,[n,p11,p12],dict(kind='native true N and current leaf repair context',canvasGlobalXYWH=[40960,36237,1254,1254],scale=1,productionPixels=False,operations=[dict(source=str(n),cropLTRB=[0,3469,1254,4096],pasteXY=[0,0]),dict(source=str(p11),cropLTRB=[115,115,1254,742],pasteXY=[0,627]),dict(source=str(p12),cropLTRB=[230,115,345,742],pasteXY=[1139,627])]))
 prompt='''Use case: precise-object-edit. Repair Image1 at its exact native1254x1254 crop. Image2 is approved Daoist chibi art STYLE only, not UI content. This is a close-up of golden tree foliage in a larger isometric night map. The perfectly straight horizontal image join at y627 is a TEMPORARY COLLAGE DEFECT, not a real lighting edge. The region ABOVE y627 is correct authoritative artwork and must remain unchanged. Genuinely repaint the short missing or mismatching continuations of the EXISTING rounded golden leaves immediately BELOW y627, especially x0..850. Continue each upper leaf silhouette, ochre shadow and golden highlight at precisely the same position and width. The two sides should look painted together, with complete coherent leaf shapes crossing the line. Eliminate the horizontal rectangular tone band, truncated leaf shapes and doubled highlight edges by drawing the correct connected leaf forms, not by blurring the line. Preserve the existing leaf cluster arrangement, black-purple branches, warm platform opening at far left, all object positions, camera, scale and crop. Gradually return to the existing lower foliage by y947, and to the existing right foliage by x850. Keep all pixels above627, below947 and to the right of850 unchanged. Keep rounded, bright clean painterly forms, consistent warm amber lighting with blue night gaps. No new branches, flowers, decoration, text, outlines, noise, diffuse haze or sharpening halo. Return one fully opaque image.'''
 pp=F/'north-leaves-v1.prompt.txt';pp.write_text(prompt,encoding='utf-8');style=REPO/'designs/gameplay-ui/04-guild.png';call=dict(prompt=prompt,referenced_image_paths=[str(target),str(style)],transparent_background=False)
 write(F/'north-leaves-v1.call.json',call);write(F/'north-leaves-v1.request.json',dict(preparedAt=now(),configSnapshot=read(REPO/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,**call),prompt=str(pp),promptSha256=sha(pp),references=[dict(file=str(p),sha256=sha(p)) for p in [target,style]],sources=[dict(file=str(p),sha256=sha(p)) for p in [n,p11,p12]],candidateBoxLTRB=[0,0,850,320],p11BoxLTRB=[115,115,965,435],canvasGlobalXYWH=[40960,36237,1254,1254],sourcePixelScale=1))
 print(str(F/'north-leaves-v1.call.json'))
def save(source):
 src=Path(source);dst=F/'north-leaves-v1.png';req=read(F/'north-leaves-v1.request.json');assert not dst.exists() and Image.open(src).size==(1254,1254)
 for a in req['references']+req['sources']:assert sha(a['file'])==a['sha256']
 shutil.copy2(src,dst);write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',actualModel=None,actualQuality=None,unverifiedReason='Host-managed; selectors and actual version/quality metadata unavailable.',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),sourceUpscaled=False,resizedAfterGeneration=False,accepted=False,mapping=dict(canvasGlobalXYWH=req['canvasGlobalXYWH'],p11BoxLTRB=req['p11BoxLTRB'])))
 print(str(dst));print(sha(dst))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 else:save(sys.argv[2])
