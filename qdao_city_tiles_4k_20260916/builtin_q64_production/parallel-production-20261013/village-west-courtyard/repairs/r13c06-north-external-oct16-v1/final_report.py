from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
R=Path(__file__).resolve().parent;B=R.parent.parent;Q=R/'final-qa-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(p,j):
    with p.open('x',encoding='utf-8') as f:json.dump(j,f,ensure_ascii=False,indent=2)
t=json.loads((Q/'trace-and-qa-inputs-v1.json').read_text());cp=Path(t['finalContext']['path']);npth=Path(t['northFrozenAnchor']['path']);bp=Path(t['baseW19']['path'])
for v in [t['finalContext'],t['northFrozenAnchor'],t['baseW19'],t['final4096']]:assert sha(v['path'])==v['sha256']
c=np.asarray(Image.open(cp));n=np.asarray(Image.open(npth));a=np.asarray(Image.open(bp))
checks=[]
for x in t['crops']:
    assert sha(x['path'])==x['sha256'];got=np.asarray(Image.open(x['path']))
    if x['kind']=='actual-core-join':
        nb=x['northContextBox'];sb=x['southContextBox'];want=np.concatenate([n[nb[1]:nb[3],nb[0]:nb[2]],c[sb[1]:sb[3],sb[0]:sb[2]]],axis=0)
    else:
        b=x['contextBox'];want=c[b[1]:b[3],b[0]:b[2]]
    assert np.array_equal(got,want)
    status='passed-local-scope'
    if x.get('segment') in [3,4]:status='improved-with-residual-fine-step'
    reuse=None
    if x.get('segment')==3:
        old=R/'final-qa-v1/actual-core-c3.png';assert sha(old)==x['sha256'];reuse={'path':str(old),'sha256':sha(old),'reason':'Actually viewed original-scale crop with identical hash; unchanged input review reused'}
    checks.append({**x,'actuallyViewed':True,'viewDetail':'original','visualStatus':status,'reviewReuse':reuse})
res=json.loads((Q/'residual-inputs-v1.json').read_text())
for x in res:
    assert sha(x['path'])==x['sha256'];x.update(status='unresolved-local-fine-color-step',actuallyViewed=True,viewDetail='original',description='Fine nearly-horizontal color/texture step persists across a blue pool at the real core join. Much smaller than the original full-width seam, but not counted as passed.')
ys,xs=np.where(np.any(c!=a,axis=2));bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
review={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'/root/resume_r12c06_oct16','tile':'r13_c06','status':'north-external-improved-N01-N02-pass-N03-N04-residual','formalAccepted':False,'source':t['finalContext'],'northFrozenAnchor':t['northFrozenAnchor'],'sourceTrace':ref(cp.parent/'assembly.json'),'reviewedActualCoreSeamGlobalY':49152,'reviewedGlobalStrip':[20480,48922,24576,49902],'localConclusions':[{'id':'N01','status':'passed-local-north-join-and-selection-boundaries','note':'Large cut and moved jagged boundary resolved; N01 mask v2 chosen.'},{'id':'N02','status':'passed-local-north-join-and-selection-boundaries','note':'Large scalloped color step resolved; source N02 v1 retained.'},{'id':'N03','status':'improved-not-passed','note':'Large triangle and right boundary cut resolved, fine blue-pool step remains.'},{'id':'N04','status':'improved-not-passed','note':'Original full-segment straight line removed by hard selection, fine blue-pool step remains.'}],'checks':checks,'residualFindings':res,'rejectedFollowup':{'generatedSource':ref(R/'N04bridge.generated-v1.png'),'candidates':[ref(R/'N04bridge-assembly-v1/assembly.json'),ref(R/'N04bridge-assembly-v2/assembly.json')],'observation':'Focused native AI bridge plus 15px and 1px upper-boundary selections did not remove the remaining tiny steps; 1px selection introduced a straighter color band. Preserve best earlier v2 and pause these two small residual sites per repeated-no-improvement rule.','selected':False},'preservedIntermediateFailures':['hard-v1: visible lower moved seams N01..03','N03 v1: retained old blue triangle','N03 v2: new right-edge blue-pool cut','N01 v1: small moved edge retained'],'proof':{**t['proof'],'finalSourceHashesUnchanged':True,'qaCropPixelIdentityMismatches':0,'changedContextBBoxFromW19':bbox},'unaffectedScope':'All pixels at context y>=650 are exactly W19. Prior passed checks there may be reused when bound to the corresponding unchanged pixels.','pending':['Two fine north-seam residuals documented above','West/east/south external seams not reviewed or cleared here','Whole tile and global map formal acceptance'],'route':'builtin-image_gen','actualModel':'not returned','newNative1254Generations':4,'selectedNewNative1254Sources':3,'upstreamArtworkMutated':False,'gitOperations':False}
write(Q/'review-v1.json',review)
manifest={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r13_c06','status':'best-current-native4096-north-repaired-with-two-residuals','formalAccepted':False,'bestNative4096':t['final4096'],'bestContext':t['finalContext'],'fullHierarchicalTrace':ref(cp.parent/'assembly.json'),'qa':ref(Q/'review-v1.json'),'sourceLayerMap':t['sourceLayerMap'],'baselineW19':t['baseW19'],'baselineW19Assembly':ref(bp.parent/'assembly.json'),'frozenNorthAnchor':t['northFrozenAnchor'],'frozenNorthFullTrace':ref(npth.parent.parent/'delivery-manifest-v1.json'),'orderedSelectionTrace':t['orderedTrace'],'proof':review['proof'],'selectedNativeRepairs':[ref(R/(x+'.generated-v1.png')) for x in ['N01','N02','N03']],'generationRequests':[ref(R/(x+'.request.json')) for x in ['N01','N02','N03','N04bridge']],'generationReceipts':[ref(R/(x+'.receipt-v1.json')) for x in ['N01','N02','N03','N04bridge']],'pendingResiduals':[{'id':x['id'],'southContextBox':x['issueSouthContextBox'],'globalBox':x['issueGlobalBox']} for x in res],'outsideEdges':'west/east/south pending; north partially passed only','actualModel':'not returned','route':'builtin-image_gen','selectionOperation':'binary integer native pixel source selection, no resampling, blending, blur or painting','preserveAllSourcesAndFailures':True}
write(R/'delivery-manifest-v1.json',manifest)
print(json.dumps({'manifest':ref(R/'delivery-manifest-v1.json'),'review':ref(Q/'review-v1.json'),'best4096':t['final4096'],'bestContext':t['finalContext'],'trace':ref(cp.parent/'assembly.json'),'pending':manifest['pendingResiduals'],'proof':manifest['proof']}))
