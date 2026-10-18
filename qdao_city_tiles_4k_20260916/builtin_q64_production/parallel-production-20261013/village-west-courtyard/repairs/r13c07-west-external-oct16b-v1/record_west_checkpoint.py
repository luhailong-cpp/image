from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
R=Path(__file__).resolve().parent;B=R.parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):
    if Path(p).exists():return
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
q=B/'qa/r13-c07-west-final-inspection-oct16b-v2';m=read(q/'manifest.json');obs=[]
reused=['band-01','band-02','band-05','band-06','south-west-corner']
for c in m['crops']:
    assert sha(c['path'])==c['sha256'];same=None
    if c['id'] in reused:
        previous=B/'qa/r13-c07-west-final-inspection-oct16b-v1'/Path(c['path']).name
        same=np.array_equal(np.asarray(Image.open(previous)),np.asarray(Image.open(c['path'])));assert same
    obs.append(dict(c,reviewed=True,accepted=c['id']!='band-01',viewMethod='view_image original native pixels' if same is None else 'reuse exact pixel equality from actually viewed v1 crop',reusedVisualEvidencePixelsEqual=same,note='Residual small triangular color boundary near own context [150,450,240,560]; pending root N01 correction.' if c['id']=='band-01' else 'Continuous native water/foam contours across contact and patch sides; no rectangular gap.'))
pending=[{'id':'west-r01-triangular-color-transition','contextBox':[150,450,240,560],'evidence':pin(q/'west-r01-contact-detail.png'),'status':'pending','owner':'root upcoming north N01','aiAttemptsHere':1},{'id':'vertical-r01-c03','contextBox':[3185,470,3250,535],'status':'pending','owner':'root north N03/N04','aiAttemptsHere':2}]
qa={'tile':'r13_c07','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inspection':pin(q/'manifest.json'),'candidate':m['candidate'],'context':m['context'],'westAnchor':m['westAnchor'],'southAnchor':m['southAnchor'],'observations':obs,'reviewedNativeCrops':11,'acceptedNativeCrops':10,'westEdgeAccepted':False,'southWestCornerAccepted':True,'southEdgePreserved':True,'wholeTileInternalAccepted':False,'internalAcceptedCount':32,'internalTotal':33,'formalAccepted':False,'pending':pending,'reusedInternalCrops':m['reusedInternalCrops'],'acceptanceIsVisualNotReplay':True}
js(q/'visual-qa-v1.json',qa)
initial=B/'qa/r13-c07-west-actualcorejoin-oct16b-v1';im=read(initial/'manifest.json')
js(initial/'visual-qa-v1.json',{'inspection':pin(initial/'manifest.json'),'observations':[dict(c,reviewed=True,accepted=False,note='Vertical ripple/foam phase and tone discontinuity at actual core boundary x345.') for c in im['crops']],'westEdgeAccepted':False,'formalAccepted':False})
failed=B/'qa/r13-c07-west-final-inspection-oct16b-v1'
js(failed/'visual-qa-v1.json',{'candidate':pin(R/'west-r04-v01-assembly-v1/r13_c07.candidate.png'),'reviewedNativeCrops':[pin(failed/f'band-{i:02d}.png') for i in range(1,8)]+[pin(failed/'south-west-corner.png')],'westEdgeAccepted':False,'formalAccepted':False,'issues':[{'id':'west-r01-triangle','contextBox':[150,450,240,560]},{'id':'west-r03-r04-overlap-coverage-gap','contextBox':[115,3072,230,3200],'correctedInV2':True}],'supersededBy':pin(q/'visual-qa-v1.json')})
asm=read(m['assembly']['path']);context=np.asarray(Image.open(m['context']['path']).convert('RGB'));candidate=np.asarray(Image.open(m['candidate']['path']).convert('RGB'));assert context.shape==(4326,4326,3) and candidate.shape==(4096,4096,3) and np.array_equal(context[115:4211,115:4211],candidate)
ownpre=read(B/'records/r13c07-south-checkpoint-oct16b-v1.json');baseline=np.asarray(Image.open(ownpre['context']['path']).convert('RGB'));assert np.array_equal(context[:,742:],baseline[:,742:])
sources=[pin(B/'repairs/r13c07-internal-seams-oct16/rock-east-r03-v01.png.generation.json')]
sources += [pin(B/f'repairs/r13c07-south-external-oct16b-v1/south-c{i:02d}-v01.generation.json') for i in range(1,5)]
sources += [pin(R/f'west-r{i:02d}-v01.generation.json') for i in range(1,5)]
record={'schemaVersion':1,'tile':'r13_c07','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'native-candidate-south-passed-west-local-pending-north-root-in-progress','formalAccepted':False,'dimensions':[4096,4096],'globalCoreBox':[24576,49152,28672,53248],'globalContextBox':[24461,49037,28787,53363],'integerCoreCrop':[115,115,4211,4211],'assembly':m['assembly'],'candidate':m['candidate'],'context':m['context'],'selected16CoreManifest':pin(B/'records/selection-r13c07-v1.json'),'newGenerationRecordsThisWorker':sources,'westQA':pin(q/'visual-qa-v1.json'),'southQA':ownpre['southQA'],'internalBaselineQA':ownpre['internalQA'],'proof':{'actual4096':True,'candidateEqualsIntegerCoreCrop':True,'westChangesOutsideContextX742':0,'lastAssemblyReplay':asm['proof'],'allNewGenerationDimensions':[1254,1254],'nativePixelsResampled':False,'blending':False,'proceduralPaint':False},'route':'builtin','actualModel':None,'internal':{'accepted':32,'total':33,'wholeAccepted':False},'external':{'south':'passed; corner rechecked after west','west':'6 of 7 bands passed; W01 triangle pending','north':'root independent N02-N04 patches in progress, N01 after west freeze','east':'current owner processed candidate found but no frozen external pin'},'pending':pending+[{'id':'east-actual-core-join','status':'pending-neighbor-freeze'},{'id':'north-actual-core-join','status':'root-in-progress'}]}
js(B/'records/r13c07-native-delivery-oct16b-v1.json',record)
print(json.dumps({'delivery':pin(B/'records/r13c07-native-delivery-oct16b-v1.json'),'westQA':pin(q/'visual-qa-v1.json'),'assembly':m['assembly'],'candidate':m['candidate'],'context':m['context']}))
