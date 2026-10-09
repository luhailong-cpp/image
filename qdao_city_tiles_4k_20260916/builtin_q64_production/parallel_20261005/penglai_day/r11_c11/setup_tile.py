from pathlib import Path
import sys,json
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;B=T.parent;sys.path.insert(0,str(B));import production as p
p.ROOT=T
for d in ['native','references','prompts','guides','evidence','tiles','qa','repairs']:(T/d).mkdir(parents=True,exist_ok=True)
h=p.read(B/'handoff.json');layout=Path(h['layout']['file']);assert p.sha(layout)==h['layout']['sha256'];assert p.sha(h['plan']['file'])==h['plan']['sha256']
tile=next(x for x in p.read(h['plan']['file'])['tiles'] if x['id']=='r11_c11');assert tile['finalPixelRect']==[40960,40960,4096,4096]
neighbors={'north':(B/'tiles/current/region-v6/r10_c11-candidate.png','802da6cc33ef10cd951698b7d750c516ae674df2799d0eb9f1d05e99cb8d04d8'),'west':(B/'r11_c10/repairs/shared-output-v1/r11_c10-candidate.png','258fa74f938f10b1920d953be1765c5ecca47a31d3fae6437908d92be362240e'),'northwest':(B/'r11_c10/repairs/shared-output-v1/r10_c10-candidate.png','9d8ba5e58f78ffc43bb15dbfe640c268e6ae158000aae77dc43bf7bf8bbd851d')}
box=[v*1254/65536 for v in [40845,40845,45171,45171]];im=Image.open(layout).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC);f=T/'references/layout-only.png';im.save(f);p.derived(f,[layout],{'method':'layout-only geometry crop and resample, never final pixels','sourceBox':box,'globalBox':[40845,40845,45171,45171],'neverFinalArt':True})
state={};sources=[f]
for name,(source,digest) in neighbors.items():
 assert p.sha(source)==digest,source
 src=Image.open(source).convert('RGB');crop={'north':(0,3981,4096,4096),'west':(3981,0,4096,4096),'northwest':(3981,3981,4096,4096)}[name]
 f=T/'references'/f'{name}-115-native.png';src.crop(crop).save(f);p.derived(f,[source],{'method':'exact native115 anchor','boxLTRB':crop})
 preview=T/'references'/f'{name}-preview.png';src.resize((1254,1254),Image.Resampling.LANCZOS).save(preview);p.derived(preview,[source],{'method':'review-only downscale'})
 pos={'north':(33,0),'west':(0,33),'northwest':(0,0)}[name];size={'north':(1188,33),'west':(33,1188),'northwest':(33,33)}[name]
 im.paste(Image.open(f).resize(size,Image.Resampling.LANCZOS),pos);sources.append(f)
 state[name]={'source':str(source),'sha256':digest,'anchor':str(f),'anchorSha256':p.sha(f),'stable':True}
dest=T/'references/layout-anchors-only.png';im.save(dest);p.derived(dest,sources,{'method':'layout-only native-geometry anchors downscaled for structure drafting','neverFinalArt':True})
state['note']='North west northwest frozen by root. East/south currently nonexistent. Output exact proposals only; never modify neighbors.'
p.write(T/'evidence/boundary-state.json',state)
p.write(T/'plan.json',{'tile':tile,'core':1024,'halo':115,'nativePatch':[1254,1254],'grid':[4,4],'formalAccepted':False})
p.write(T/'evidence/model-verification.json',{'configSnapshot':p.read(p.REPO/'config/image-generation.json'),'batch':'continuation of builtin_q64 parallel20261005 same batch','actualSelectorsExposed':False,'actualModel':None,'actualQuality':None})
print(tile)

