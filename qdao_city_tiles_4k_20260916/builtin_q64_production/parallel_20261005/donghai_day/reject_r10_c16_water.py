from pathlib import Path
import shutil,sys
import production_r10_c16 as p
T=p.common.p.T
D=T/'rejected'/'r01_c04-v1'
D.mkdir(parents=True,exist_ok=True)
for fn in ['r01_c04.txt','r01_c04.references.json']:
 shutil.copyfile(T/'prompts'/fn,D/fn)
src=Path(sys.argv[1]);out=D/'rejected-native.png';assert not out.exists();shutil.copyfile(src,out)
from PIL import Image
im=Image.open(out);im.load()
refs=p.common.p.loadj(D/'r01_c04.references.json')
p.common.p.savej(D/'rejection.json',{'file':str(out),'sha256':p.common.p.sha(out),'generatedAt':p.common.p.now(),'width':im.width,'height':im.height,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':p.common.p.loadj(p.common.p.PROJECT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[x['file'] for x in refs]},'actualModel':None,'actualQuality':None,'prompt':str(D/'r01_c04.txt'),'promptSha256':p.common.p.sha(D/'r01_c04.txt'),'references':refs,'sourcePath':str(src),'status':'rejected','actualVisualReview':True,'reason':'Added an entire pier, shore, bucket and net to a crop containing only quiet cyan water and a tiny existing corner. Do not use in final pixels.','resizedAfterGeneration':False,'finalArtUpscaled':False})
