from pathlib import Path
import sys,json
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;B=T.parent;sys.path.insert(0,str(B));import production as p
p.ROOT=T
for d in ['native','references','prompts','guides','evidence','tiles','qa','repairs']:(T/d).mkdir(parents=True,exist_ok=True)
h=p.read(B/'handoff.json');layout=Path(h['layout']['file']);assert p.sha(layout)==h['layout']['sha256'];assert p.sha(h['plan']['file'])==h['plan']['sha256']
tile=next(x for x in p.read(h['plan']['file'])['tiles'] if x['id']=='r11_c10');assert tile['finalPixelRect']==[36864,40960,4096,4096]
north=B/'r10_c10/repairs/shared-output-v3/r10_c10-candidate.png';assert p.sha(north)=='45af814cd610d0243598105bd1a55839cd45c86597bc04509293b1a035488417'
box=[v*1254/65536 for v in [36749,40845,41075,45171]];im=Image.open(layout).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC);f=T/'references/layout-only.png';im.save(f);p.derived(f,[layout],{'method':'layoutonly geometry crop and resample, never final pixels','sourceBox':box,'globalBox':[36749,40845,41075,45171],'neverFinalArt':True})
src=Image.open(north).convert('RGB');f=T/'references/north-115-native.png';src.crop((0,3981,4096,4096)).save(f);p.derived(f,[north],{'method':'exact native115 bottomstrip'})
src.resize((1254,1254),Image.Resampling.LANCZOS).save(T/'references/north-preview.png');p.derived(T/'references/north-preview.png',[north],{'method':'reviewonlydownscale'})
im.paste(Image.open(f).resize((1188,33),Image.Resampling.LANCZOS),(33,0));dest=T/'references/layout-anchors-only.png';im.save(dest);p.derived(dest,[T/'references/layout-only.png',f],{'method':'layoutonly exact geometry with downscalednorthanchor','neverFinalArt':True})
p.write(T/'evidence/boundary-state.json',{'north':{'source':str(north),'sha256':p.sha(north),'anchor':str(f),'anchorSha256':p.sha(f),'stable':True},'note':'Root authorized nexttile r11_c10. North c10sharedv3 frozen. No east west south candidates exist.'})
p.write(T/'plan.json',{'tile':tile,'core':1024,'halo':115,'nativePatch':[1254,1254],'grid':[4,4],'formalAccepted':False})
p.write(T/'evidence/model-verification.json',{'configSnapshot':p.read(p.REPO/'config/image-generation.json'),'batch':'continuation of builtin_q64 parallel20261005 same batch','actualSelectorsExposed':False,'actualModel':None,'actualQuality':None})
print(tile);print(north)

