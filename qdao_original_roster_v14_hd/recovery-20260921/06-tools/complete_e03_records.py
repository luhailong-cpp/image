"""Add missing generation records for the actual E03 v2/v3 calls without rewriting requests or receipts."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    if p.exists():
        assert read(p)==v,str(p)+' already exists with different evidence'
        return
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('e03_provenance',ROOT/'tools/inspect_image_provenance.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for batch in ('E03-edge-v2','E03-edge-v3'):
    folder=HERE.parent/'06-generation'/batch
    keep={n:sha(folder/n) for n in ('raw.png','request.json','prompt.txt','generation-receipt.json')}
    receipt=read(folder/'generation-receipt.json');request=read(folder/'request.json');actual=request['request'];config=read(folder/'config-snapshot.json')
    provenance=m.inspect_image(folder/'raw.png')
    write(folder/'provenance.json',provenance)
    refs=[{'path':p,'sha256':sha(Path(p)),'role':'edit target' if i==0 else 'approved painted style reference'} for i,p in enumerate(actual['referenced_image_paths'])]
    record={'file':'raw.png','sha256':sha(folder/'raw.png'),'generatedAt':receipt['completedAt'],
            'startedAt':request['startedAt'],'width':provenance['native_size'][0],'height':provenance['native_size'][1],'format':'PNG',
            'tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':request.get('submittedParameters',receipt.get('submittedParameters',{'model':None,'quality':None})),
            'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际型号或质量；PNG的gpt-image系列元数据不等于2.5或max锁定。',
            'prompt':'prompt.txt','prompt_sha256':sha(folder/'prompt.txt'),'references':refs,
            'editTarget':refs[0],'evidence':[{'path':n,'sha256':sha(folder/n)} for n in ('request.json','generation-receipt.json','provenance.json')],
            'visual_selection':'rejected' if batch.endswith('v2') else 'selected_for_E03',
            'selection_reason':'Character enlarged and planted shoe visibly clipped at bottom; edge alpha reaches250.' if batch.endswith('v2') else 'Original framing largely preserved; root viewed deep/light composites and accepted edge repair; loop review still pending.'}
    write(folder/'raw.png.generation.json',record)
    assert keep=={n:sha(folder/n) for n in keep}
    print(batch,record['visual_selection'],record['sha256'])
