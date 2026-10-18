import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
BASE=Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def artifact(p): return {'file':str(p),'sha256':sha(p)}
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,obj):
    with p.open('x',encoding='utf-8') as stream:
        json.dump(obj,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(json.dumps(artifact(p),ensure_ascii=False))
version=BASE/'versions/right-r03c14-roof-corner-native-v001'
integration=read(version/'integration.json')
manifest_path=BASE/'versions/root-r03c14-full-assembly-v002/r03_c14/assembly/assembly.json'
manifest=read(manifest_path)
candidate=Image.open(integration['candidate']['file']).convert('RGB')
baseline=Image.open(integration['previousCandidate']['file']).convert('RGB')
affected={'vertical-p22-p23','vertical-p32-p33','horizontal-p22-p32','horizontal-p23-p33'}
unchanged=[]
for seam in manifest['internalSeamSegments']:
    key=Path(seam['file']).stem
    if key not in affected:
        assert candidate.crop(seam['crop']).tobytes()==baseline.crop(seam['crop']).tobytes()
        unchanged.append({'name':key,'evidence':seam,'candidateCropPixelIdentityVerified':True})
assert len(unchanged)==20
qa_path=BASE/'qa/right-r03c14-roof-corner-after-v001.json'
qa={
 'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'tower_right','tile':'r03_c14',
 'candidate':integration['candidate'],'nativeRepair':integration['nativeRepair'],'integration':artifact(version/'integration.json'),
 'actualModel':None,'actualModelEvidence':'未返回','entryPoint':'existing included built-in image_gen',
 'localRoiAttempt':1,'localRoiAttemptLimit':2,'oldP23WholeCoreAttemptCount':2,
 'differentRepairScope':'This attempt repairs only one 190x410 roof/eave junction spanning four patch corners; it does not replace p23 whole core.',
 'editTileXYXY':integration['editTileXYXY'],'alphaPerimeterPixels':16,
 'nativeEventBytesMatch':True,'unchangedOutsideEditVerified':True,'noResize':True,'noWarp':True,'noImageBlur':True,
 'geometricResult':'local-pass',
 'observedImprovement':'此前直切的上段蓝瓦端面补成完整椭圆，下段瓦端正常弧形收头，斜红檐跨缝连通。未把旧断口迁移到ROI四边。',
 'perimeterReview':[
   {'side':'north','status':'local-pass','observation':'蓝瓦曲面、白色高光和端部金圈在ROI上缘连续。'},
   {'side':'south','status':'local-pass','observation':'红梁下缘、红柱顶和支撑括件连接保持，未新增层级错位。'},
   {'side':'west','status':'local-pass','observation':'左端瓦列曲线和红檐亮线平顺接入，未见ROI竖切边。'},
   {'side':'east','status':'local-pass','observation':'金圈瓦端、红梁与原木面接续；更右侧既有明暗分区未移动。'}
 ],
 'perimeterEvidence':integration['perimeterEvidence'],
 'contextEvidence':integration['contextEvidence'],
 'affectedSeamEvidence':read(BASE/'qa/right-r03c14-roof-corner-evidence-v001.json')['affectedSeamCrops'],
 'changedSeamReview':[
   {'name':'vertical-p22-p23','status':'local-pass','scope':'Full vertical crop re-viewed at original pixels.'},
   {'name':'vertical-p32-p33','status':'local-pass','scope':'Full vertical crop re-viewed at original pixels.'},
   {'name':'horizontal-p22-p32','status':'local-pass','scope':'Only changed area and transition checked; unchanged remainder retains root/QA status.'},
   {'name':'horizontal-p23-p33','status':'local-pass','scope':'Only changed area and transition checked; unchanged remainder retains root/QA status.'}
 ],
 'unchangedSeamCropsVerified':unchanged,
 'verticalLocalPassCount':12,'verticalNeedsRepairCount':0,
 'priorVerticalReports':[artifact(BASE/f'qa/right-r03c14-vertical-group{i}-v001.json') for i in (1,2,3)],
 'supersedesCorrection':artifact(BASE/'qa/right-r03c14-vertical-correction-v002.json'),
 'horizontalFullReview':'Root/tower_qa owns the 12-horizontal-seam review; this record only rechecks touched parts.',
 'externalSeamAcceptance':'Not assessed by this local repair. Candidate outer 115px frame is unchanged from full-assembly-v002.',
 'formalAcceptedCount':0,'fullTileVisualAcceptance':False,
 'nextAction':'Submit to root/independent QA; no second local generation needed absent a new concrete defect.'
}
write(qa_path,qa)
selection={
 'schemaVersion':1,'selectionVersion':'right-r03c14-candidate-overlay-v001','kind':'complete4096_candidate_with_native_AI_repair_overlay','tile':'r03_c14',
 'baseNativeSelection':manifest['selection'],'nativeCoreCount':16,'additionalCoreCount':0,
 'candidate':integration['candidate'],'repairIntegrations':[artifact(version/'integration.json')],
 'visualQa':artifact(qa_path),'verticalLocalPassCount':12,'formalAcceptedCount':0,'fullVisualAcceptance':False,
 'status':'local_roof_junction_repaired_pending_independent_and_external_qa',
 'reassemblyWarning':'Reassembling the16base sources alone omits the selected native repair ROI; use this candidate and integration chain.',
 'originalCandidate':integration['previousCandidate']
}
write(BASE/'selections/right-r03c14-candidate-overlay-v001.json',selection)
