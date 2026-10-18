from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime,sys
version=sys.argv[1] if len(sys.argv)>1 else 'v1'
R=Path(__file__).resolve().parent;B=R.parent.parent;Q=R/('final-qa-'+version);Q.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,a):
    with p.open('xb') as f:Image.fromarray(a).save(f,format='PNG')
def fref(p):return {'path':str(p),'sha256':sha(p)}
base=B/'qa/r13-c06-water-repair-W19-v1/context-native.png';north=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png';final=R/'N03-assembly-v3/context-native.png' if version=='v1' else R/('final-candidate-'+version)/'context-native.png'
assert sha(base)=='2f414db91456bd6fc8839b262ec58c53472e665e0a8c4d081ea5bc97122c466c';assert sha(base.parent/'assembly.json')=='aed99126ceb376c563e80505c29a63491b0f4b1c9544b20e42c312095cb877d8'
a=np.asarray(Image.open(base).convert('RGB'));n=np.asarray(Image.open(north).convert('RGB'));c=np.asarray(Image.open(final).convert('RGB')) if version=='v1' else None;replay=a.copy();ids=np.zeros(a.shape[:2],np.uint8)
hm=np.asarray(Image.open(R/'hard-v1/north-source-mask.png'))>0;replay[:230][hm]=n[4096:4326][hm];ids[:230][hm]=1
trace=[{'step':'W19 complete native baseline',**fref(base.parent/'assembly.json')},{'step':'frozen north anchor provenance',**fref(north.parent.parent/'delivery-manifest-v1.json')},{'step':'native overlap hard source selection',**fref(R/'hard-v1/assembly.json')}]
sources=[{'sourceLayerId':0,'type':'W19-complete-native-context','globalContextBox':[20365,49037,24691,53363],**fref(base),'trace':fref(base.parent/'assembly.json')},{'sourceLayerId':1,'type':'frozen-r12-complete-native-context','globalContextBox':[20365,44941,24691,49267],**fref(north),'trace':fref(north.parent.parent/'delivery-manifest-v1.json')}]
for sid,name,ver in [(2,'N01','v1' if version=='v1' else 'v2'),(3,'N02','v1'),(4,'N03','v3')]:
    asm=R/f'{name}-assembly-{ver}/assembly.json';j=json.loads(asm.read_text());x=j['contextNativeBox'][0];g=np.asarray(Image.open(j['source']['path']).convert('RGB'));m=np.asarray(Image.open(j['mask']['path']))>0
    replay[:998,x:x+1254][m[256:]]=g[256:][m[256:]];ids[:998,x:x+1254][m[256:]]=sid
    sources.append({'sourceLayerId':sid,'type':'native1254-AI-repair',**j['source'],'mask':j['mask'],'trace':fref(asm)});trace.append({'step':f'{name} selected {ver}',**fref(asm)})
if version!='v1':
    final.parent.mkdir(exist_ok=False);save(final,replay);save(final.parent/'r13_c06.candidate-native-4096.png',replay[115:4211,115:4211]);c=np.asarray(Image.open(final).convert('RGB'))
assert np.array_equal(replay,c);save(Q/'final-source-layer-id.png',ids)
proof={'hierarchicalReplayMismatch':int(np.any(replay!=c,axis=2).sum()),'uncoveredPixels':0,'rows650AndBelowChangesFromW19':int(np.any(c[650:]!=a[650:],axis=2).sum()),'r12AnchorUnchanged':sha(north)=='f688156e4a82f4f0b0ef294b3f2ba76e5b36d42baaf009f902b0530ea986b3ef','allSelectedAIInputsNative1254':True,'noBlendOrResample':True}
crops=[]
for k,x in enumerate([115,1139,2163,3187],1):
    p=Q/f'actual-core-c{k}.png';qa=np.concatenate([n[3981:4211,x:x+1024],c[115:865,x:x+1024]],axis=0);save(p,qa)
    assert np.array_equal(np.asarray(Image.open(p))[:230],n[3981:4211,x:x+1024]);assert np.array_equal(np.asarray(Image.open(p))[230:],c[115:865,x:x+1024])
    crops.append({'kind':'actual-core-join','segment':k,**fref(p),'dimensions':[1024,980],'scale':1,'northContextBox':[x,3981,x+1024,4211],'southContextBox':[x,115,x+1024,865],'globalBox':[20365+x,48922,21389+x,49902],'seamImageY':230,'pixelIdentityMismatch':0})
for k,x in enumerate([1139,2163,3187,3302],1):
    box=[x-150,0,x+150,760];p=Q/f'selection-junction-{k}.png';save(p,c[box[1]:box[3],box[0]:box[2]])
    assert np.array_equal(np.asarray(Image.open(p)),c[box[1]:box[3],box[0]:box[2]])
    crops.append({'kind':'selection-junction',**fref(p),'contextBox':box,'dimensions':[300,760],'scale':1,'pixelIdentityMismatch':0})
rec={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r13_c06','status':'pending-final-native-visual-QA','formalAccepted':False,'baseW19':fref(base),'finalContext':fref(final),'final4096':fref(final.parent/'r13_c06.candidate-native-4096.png'),'northFrozenAnchor':fref(north),'sourceLayerMap':fref(Q/'final-source-layer-id.png'),'sources':sources,'orderedTrace':trace,'proof':proof,'crops':crops,'operation':'hierarchical native source replay from linked complete W19 and frozen r12 trace chains plus three native1254 AI edits; binary integer selection only','actualModel':'not returned','generationRoute':'builtin-image_gen','newNativeGenerations':3,'preservedRejectedCandidates':['hard-v1 (N01..03 new lower boundary failures)','N03-assembly-v1 (old triangle retained)','N03-assembly-v2 (right-boundary blue-water cut)']}
with (Q/'trace-and-qa-inputs-v1.json').open('x',encoding='utf-8') as f:json.dump(rec,f,ensure_ascii=False,indent=2)
if version!='v1':
    rec['rebaseNote']='Saved integer masks replayed in orderedTrace order onto complete W19 with N01 v2 chosen. N02 and N03 source/mask artifacts are reused unchanged; this new recipe records their reapplication, not a claim that the old intermediate baseline remained identical.'
    with (final.parent/'assembly.json').open('x',encoding='utf-8') as f:json.dump(rec,f,ensure_ascii=False,indent=2)
print(json.dumps({'qa':str(Q),'finalContext':rec['finalContext'],'final4096':rec['final4096'],'proof':proof,'traceSha256':sha(Q/'trace-and-qa-inputs-v1.json')}))
