from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import compose_shared as c
q=c.q;h=c.h;R=T/'repairs';I=R/'shared-output-v2';O=R/'shared-output-v3';O.mkdir(exist_ok=True)
names=['r09_c10','r09_c11','r10_c10','r10_c11'];state=h.p.read(R/'shared-boundary-state.json')
a={k:q.arr(I/(k+'-candidate.png')) for k in names}
x,y=0,1421;src=R/'internal-ai/native/post.png';old=a['r10_c10'][y:y+1254,x:x+1254];out,e=c.record(R/'internal-ai/output-v3','post',old,q.arr(src),src,[x,y],[(480,540),(690,750),(50,90),(200,270)]);a['r10_c10'][y:y+1254,x:x+1254]=out
deltas=[]
for k,v in a.items():
 f=O/(k+'-candidate.png');c.save(v,f,[I/(k+'-candidate.png')]+([e['replacement']] if k=='r10_c10' else []),{'method':'exactnative maskedpostrepair' if k=='r10_c10' else 'unchanged shared-output-v2 pixels','formalAccepted':False})
 base=Path(state[k]['file']) if k!='r10_c10' else T/'tiles/r10_c10-candidate.png'
 aa=np.asarray(Image.open(base).convert('RGB'));bb=np.asarray(Image.open(f).convert('RGB'));m=np.any(aa!=bb,axis=2);mp=O/(k+'-change-mask.png');Image.fromarray(m.astype('uint8')*255).save(mp)
 replay=aa.copy();replay[m]=bb[m];assert np.array_equal(replay,bb)
 yy,xx=np.nonzero(m);bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
 tilex=36864+(4096 if k.endswith('11') else 0);tiley=32768 if k.startswith('r09') else 36864
 deltas.append({'tile':k,'globalRectXYWH':[tilex,tiley,4096,4096],'baseline':str(base),'baselineSha256':h.p.sha(base),'candidate':str(f),'candidateSha256':h.p.sha(f),'changeMask':str(mp),'changeMaskSha256':h.p.sha(mp),'changedPixels':int(m.sum()),'bboxLTRB':bbox,'replayExact':True,'rule':'apply candidate pixels where mask255 only; preserve all other current neighbor pixels'})
srcs=sorted((T/'native').glob('p??.png'))+sorted((R).glob('*/native/*.png'));validation=[]
for src in srcs:
 recpath=Path(str(src)+'.generation.json');rec=h.p.read(recpath)
 assert h.p.sha(src)==rec['sha256']
 assert Image.open(src).size==(1254,1254)
 assert h.p.sha(rec['toolResultPath'])==rec['sha256']
 assert Path(rec['evidence']['toolOutputHintFile']).exists()
 for ref in rec['references']:assert h.p.sha(ref['file'])==ref['sha256'],ref
 assert any(Path(ref['file']).name=='04-guild.png' for ref in rec['references'])
 validation.append({'file':str(src),'sha256':rec['sha256'],'record':str(recpath),'actualModel':rec['actualModel'],'actualQuality':rec['actualQuality'],'referencesAndToolSourceHashVerified':True})
im=Image.fromarray(a['r10_c10'].astype('uint8'));im.crop((0,1421,1254,2675)).save(O/'post-review.png');q.qa(im,'shared-v3',O/'r10_c10-candidate.png');im.resize((1254,1254),Image.Resampling.LANCZOS).save(O/'preview.png')
manifest={'schema':1,'tile':'r10_c10','createdAt':h.p.stamp(),'finalCandidate':str(O/'r10_c10-candidate.png'),'sha256':h.p.sha(O/'r10_c10-candidate.png'),'deltas':deltas,'nativeRecordsVerified':validation,'nativeDetailCount':16,'nativeRepairCount':len(srcs)-16,'layoutGuideNeverFinalPixels':True,'allSourcesNative1254':True,'postFinalPatch':e,'provenance':{'sharedV1':str(R/'shared-output-v1/record.json'),'sharedV2':str(R/'shared-output-v2/record.json'),'nativeOwnership':str(R/'internal-quilt/record-v2.json')},'qa':{'sixInternalLines':str(T/'qa/shared-v3-*.png'),'nineJunctions':str(T/'qa/shared-v3-junctions.png'),'nineFull1254InternalContexts':str(T/'qa/internal-v2-full-*.png'),'eightFull1254SharedContexts':str(R/'shared-output-v2/*-s*-review.png'),'fourCornerAndFourReturnContexts':str(R/'shared-output-v2/*return-review.png'),'postFinalContext':str(O/'post-review.png'),'status':'Visual review complete for shared-v2 internal6lines9junction and8shared1254 contexts, corner4return andshadow; finalpost localQA pending at manifest creation.'},'formalAccepted':False,'clientAccepted':False,'wholeCityComplete':False,'cleanup':'Root owns final cleanup after regional merge and reference completeness; no source images deleted here.'}
h.p.write(R/'handoff-shared-v3.json',manifest);h.p.write(O/'record.json',{'parent':str(I/'record.json'),'patch':e});print([(e['tile'],e['candidateSha256'],e['bboxLTRB'],e['changedPixels']) for e in deltas]);print('verified',len(validation))

