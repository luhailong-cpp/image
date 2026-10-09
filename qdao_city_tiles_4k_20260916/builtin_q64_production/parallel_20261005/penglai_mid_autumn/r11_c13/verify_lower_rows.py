import sys
sys.dont_write_bytecode=True
from prepare_structure import *
expected_plan='5e1121efeb9a33338ccbf125ac3ffbddb2c3b08daa32f319102afc8978bda591'
assert sha(F/'plan.json')==expected_plan
records=[]
for row in [3,4]:
    for c in range(1,5):
        ident=f'p{row}{c}';p=F/'native'/f'{ident}.png';req=read(F/'native'/f'{ident}.request.json');call=read(F/'native'/f'{ident}.call.json');gen=read(str(p)+'.generation.json');view=read(F/'native'/f'{ident}.visual-review.json')
        assert Image.open(p).size==(1254,1254) and sha(p)==gen['sha256']==view['sha256']
        assert view['actuallyViewed'] is True and view['formalAccepted'] is False
        assert sha(req['prompt'])==req['promptSha256']==gen['promptSha256']
        assert Path(req['prompt']).read_text(encoding='utf8')==call['prompt']
        assert req['submittedParameters']==dict(model=None,quality=None,**call)==gen['submittedParameters']
        assert gen['actualModel'] is None and gen['actualQuality'] is None
        assert req['globalPatchXYWH']==[X-115+(c-1)*1024,Y-115+(row-1)*1024,1254,1254]==gen['globalPatchXYWH']
        for source in req['references']+req['contextRegions']:
            assert sha(source['file'])==source['sha256']
        assert sha(gen['evidence']['sourceOutputPath'])==gen['evidence']['sourceOutputSha256']==sha(p)
        records.append(dict(id=ident,file=str(p),sha256=sha(p),generationRecord=ref(str(p)+'.generation.json'),request=ref(F/'native'/f'{ident}.request.json'),call=ref(F/'native'/f'{ident}.call.json'),visualReview=ref(F/'native'/f'{ident}.visual-review.json'),actualModel=None,actualQuality=None,contextSourcesVerified=True,promptAndReferencesVerified=True,hostSourceByteIdentical=True))
all_native=[]
for row in range(1,5):
    for c in range(1,5):
        p=F/'native'/f'p{row}{c}.png';gen=read(str(p)+'.generation.json')
        assert Image.open(p).size==(1254,1254) and sha(p)==gen['sha256']
        all_native.append(ref(p))
write(Q/'native-lower-rows-agent-review.json',dict(at=now(),reviewer='/root/r09c14_row4_resume',rootReview=False,scope='r11_c13 p31..p34 and p41..p44 generated native outputs and actual per-image viewing; no assembled seam pass',records=records,allNativeFiles=all_native,plan=ref(F/'plan.json'),planUnchanged=True,north=ref(N),allEightComplete=True,allSixteenNativeFilesComplete=True,pendingCalls=False,assemblyStartedByThisAgent=False,formalAccepted=False,nativeSeamAccepted=False))
print(json.dumps(dict(report=ref(Q/'native-lower-rows-agent-review.json'),patches=[dict(id=r['id'],sha256=r['sha256']) for r in records],allSixteenNativeFilesComplete=True,planUnchanged=True),indent=2))
