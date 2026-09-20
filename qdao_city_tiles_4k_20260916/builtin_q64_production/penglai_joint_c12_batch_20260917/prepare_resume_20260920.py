"""Versioned mechanical continuation; never edits historical plan or originals."""
import json, hashlib
from pathlib import Path
from PIL import Image
B=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
R=B/'penglai_mid_autumn/r09_c12'
src=(R/'assemble_builtin.py').read_text(encoding='utf-8')
dst=R/'assemble_builtin_v2_20260920.py'
assert not dst.exists()
src=src.replace('OUTPUT = ROOT / "output"','OUTPUT = ROOT / "output_v2_20260920"').replace('QA = ROOT / "qa"','QA = ROOT / "qa_v2_20260920"')
src=src.replace('"file": "output/extended-context.png"','"file": relative(OUTPUT / "extended-context.png")')
src=src.replace('!= "ready_unified_style_reference"','not in ("ready_unified_style_reference", "ready_unified_local_structure")')
src=src.replace('    rows, entries = load_sources()','    if OUTPUT.exists() or QA.exists():\n        raise FileExistsError("Versioned output exists; preserve it and choose another version")\n    rows, entries = load_sources()')
src=src.replace('"userSelectedModel": "GPT Image 2.0 (host builtin)",','"requestedProduct": "ChatGPT Images 2.5",\n        "configuredModelTarget": "gpt-image-2.5-sunburst",\n        "configuredQualityTarget": "max",\n        "actualBackendModel": None, "actualQualityPreset": None,\n        "historicalSourceModelsPreserved": True,')
src=src.replace('    return rows, entries','''    plan = read_json(ROOT / "plan.json")
    prep=plan['guidePreparation']; layout=Path(prep['sourceFile'])
    if sha256(layout) != prep['sourceSha256']: raise ValueError('Layout source hash changed')
    guides={}
    for item in plan['patches']:
        gp=Path(item['guide'])
        if sha256(gp)!=item['guideSha256']: raise ValueError('Plan guide SHA mismatch')
        guides[item['id']]=np.array(Image.open(gp).convert('RGB'))
    overlap_count=0
    for row in range(1,5):
        for col in range(1,5):
            g=guides[f'r{row:02d}_c{col:02d}']
            if col<4:
                assert np.array_equal(g[:,-230:],guides[f'r{row:02d}_c{col+1:02d}'][:,:230])
                overlap_count+=1
            if row<4:
                assert np.array_equal(g[-230:],guides[f'r{row+1:02d}_c{col:02d}'][:230])
                overlap_count+=1
    assert overlap_count==24
    for entry in entries:
        record=read_json(ROOT/entry['recordFile'])
        submitted=record.get('submittedImages',[])
        if not submitted: raise ValueError('Missing submitted reference record')
        for ref in submitted:
            if sha256(Path(ref['path']))!=ref['sha256']: raise ValueError('Submitted reference SHA changed')
        toolrefs=record.get('toolCall',{}).get('referenced_image_paths')
        if toolrefs is not None:
            if [Path(p).resolve() for p in toolrefs] != [Path(ref['path']).resolve() for ref in submitted]:
                raise ValueError('Tool reference order differs')
        entry['submittedImages']=submitted
        entry['guideOverlap24Passed']=True
    return rows, entries''')
dst.write_text(src,encoding='utf-8')

# Exact ROI return-edge crops, with 100 pixels on either side, no resizing.
J=B/'penglai_day/r09_c10_c11_c12_joint'
Q=J/'qa_return_edges_20260920'; Q.mkdir(exist_ok=False)
im=Image.open(J/'output_v2_20260918/triple-12288x4096.png')
asm=json.loads((J/'output_v2_20260918/assembly.json').read_text())
meta=[]
for repair in asm['repairs']:
    x,y,r,b=repair['pasteROIInTriple']
    boxes={'left':(x-100,y,x+100,b),'right':(r-100,y,r+100,b),'top':(x-100,y-100,r+100,y+100),'bottom':(x-100,max(0,b-100),r+100,min(4096,b+100))}
    for edge,box in boxes.items():
        p=Q/(repair['id']+'.'+edge+'.png'); im.crop(box).save(p)
        meta.append({'path':str(p),'cropLTRB':box,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'resized':False})
(Q/'crop-manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(json.dumps({'assembler':str(dst),'dayReturnQA':str(Q)}))
