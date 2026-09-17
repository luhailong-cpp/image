"""Independent V13 export verification; never publishes or changes artwork."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'candidate/24_lu_dongbin'
DIRS=('N','NE','E','SE','S','SW','W','NW')
BASE=ROOT.parent/'qdao_chibi_roster_v12/candidate-stable-body/24_lu_dongbin'
FROZEN_MANIFEST='3dbc699023fd7fe6f45304fd91ecea2f088e107d4c727d375dc1b23c31e68c68'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pixels(p):
    with Image.open(p) as im:
        if im.format!='PNG' or im.mode!='RGBA': raise ValueError(f'Not an RGBA PNG: {p}')
        return np.array(im)
def require(test,message):
    if not test: raise ValueError(message)
def mod(path,name):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def same(im,p,label): require(np.array_equal(np.asarray(im),pixels(p)),f'{label} pixels changed')
def anchor(a,roi):
    y,x=np.where(a[:,:,3]>8); require(len(x)>0,'Empty alpha mask')
    return float(np.median(x[y<int(y.min())+roi])),int(y.min())

def verify(require_visual=False, ignore_previous_visual=False):
    require(sha(BASE/'manifest.json')==FROZEN_MANIFEST,'V12 manifest no longer matches approved SHA')
    bm=load(BASE/'manifest.json'); m=load(OUT/'manifest.json'); qc=load(OUT/'qc.json')
    require(m['version']==13 and m['character_id']=='24_lu_dongbin','Wrong V13 identity')
    require(m['walk']['frames_per_direction']==16 and m['walk']['frame_duration_ms']==30 and m['walk']['cycle_duration_ms']==480,'V13 timing must be 16x30ms=480ms')
    require(m['walk']['contact_frame']==0 and set(m['walk']['directions'])==set(DIRS),'Wrong directions or contact frame')
    require(m['idle']['dedicated_neutral_pose'] and m['alignment']['version']==3 and m['alignment']['common_scale']==1.0,'Wrong idle/alignment contract')
    require(m['alignment']['direction_references']==bm['alignment']['direction_references'],'Fixed V12 direction references altered')
    for d in DIRS:
        ref=bm['alignment']['direction_references'][d]; idle_input=OUT/ref['idle_input_path']
        require(idle_input.is_file() and sha(idle_input)==ref['idle_input_sha256'],f'Frozen alignment idle input missing/changed: {d}')
    require(qc['status'] in ('passed_numeric_qc_pending_visual_review','passed') and not qc['errors'],'Numeric QC incomplete or failed')
    expected={'portrait.png',*[f'idle/{d}.png' for d in DIRS],*[f'walk/{d}/{i:02d}.png' for d in DIRS for i in range(1,17)],*[f'walk/{d}/strip.png' for d in DIRS]}
    require(len(expected)==145,'Internal expected export count wrong')
    files={f['path']:f for f in m['files']}; require(len(files)==len(m['files']) and set(files)==expected,'Expected exact 145 PNG delivery manifest')
    actual={p.relative_to(OUT).as_posix() for part in ('walk','idle') for p in (OUT/part).rglob('*.png')}|{'portrait.png'}
    require(actual==expected,'Missing or extra delivery PNG files')
    artifacts=[]
    for p in sorted(expected):
        require((OUT/p).is_file(),f'Missing output: {p}')
        require(sha(OUT/p)==files[p]['sha256'],f'Manifest SHA mismatch: {p}')
        a=pixels(OUT/p); size=(1024,1024) if p=='portrait.png' else (512,8192) if p.endswith('strip.png') else (512,512)
        require(a.shape[:2]==size,f'Wrong dimensions: {p} {a.shape}')
        require(a[:,:,3].min()==0 and a[:,:,3].max()==255,f'Missing transparency or opaque body: {p}')
        artifacts.append({'path':p,'sha256':sha(OUT/p)})
    frozen=load(OUT/'source/v12-frozen/preservation.json'); require(len(frozen['records'])==73,'Expected 73 unchanged baseline PNGs')
    for record in frozen['records']:
        src=Path(record['source']); require(src.is_file() and sha(src)==record['sha256'],'V12 source SHA changed')
        require(sha(OUT/record['output'])==record['sha256'],f'Frozen output changed: {record["output"]}')
    for d in DIRS:
        require(sha(OUT/f'idle/{d}.png')==sha(BASE/f'idle/{d}.png'),f'Idle changed: {d}')
        for i in range(1,9): require(sha(OUT/f'walk/{d}/{2*i-1:02d}.png')==sha(BASE/f'walk/{d}/{i:02d}.png'),f'Old frame changed: {d}/{i}')
    require(sha(OUT/'portrait.png')==sha(BASE/'portrait.png'),'Portrait changed')
    source_path=OUT/'processing/even-frame-sources.json'; require(sha(source_path)==m['alignment']['transforms_sha256'],'Source record SHA mismatch')
    sources=load(source_path); require(set(sources)=={f'{d}/{i:02d}' for d in DIRS for i in range(2,17,2)},'Expected 64 actual generated transition records')
    source_cells={(r['source']['sha256'],tuple(r['source']['cell_xyxy'])) for r in sources.values()}
    require(len(source_cells)==64,'A generated source cell was reused for multiple requested transitions')
    key_path=ROOT/'tools/vendor/generate2dsprite.py'; edge_path=ROOT/'tools/vendor/edge_despill.py'
    keyer=mod(key_path,'verify_chroma'); edge=mod(edge_path,'verify_edge')
    generation_evidence=[]
    for key,rec in sources.items():
        d,i=key.split('/'); i=int(i)
        require(rec['direction']==d and rec['frame']==i and rec['between_v12_frames']==[i//2,i//2%8+1],f'Wrong phase source: {key}')
        require(rec['generation']['tool']=='built-in image_gen' and rec['generation'].get('model_evidence'),'Missing real generation evidence')
        require(rec.get('selection_reason'),'Missing specific selection judgment')
        s=rec['source']; raw_path=OUT/s['path']; require(sha(raw_path)==s['sha256'],f'Original generation SHA changed: {key}')
        prompt=OUT/rec['prompt']['path']; require(sha(prompt)==rec['prompt']['sha256'] and prompt.read_text(encoding='utf-8-sig').strip(),f'Prompt missing/changed: {key}')
        with Image.open(raw_path) as original: raw=original.convert('RGBA')
        require(list(raw.size)==s['native_size'],'Raw source dimensions changed')
        grid=s['grid']; rows=grid['rows']; cols=grid['cols']; r=grid['row']; c=grid['col']
        expected_box=[round(c*raw.width/cols),round(r*raw.height/rows),round((c+1)*raw.width/cols),round((r+1)*raw.height/rows)]
        require(s['cell_xyxy']==expected_box,'Crop was not the complete original grid cell')
        cell=raw.crop(tuple(expected_box)); stages=rec['stages']
        for stage,data in stages.items(): require(sha(OUT/data['path'])==data['sha256'],f'Changed {stage} evidence: {key}')
        same(cell,OUT/stages['cell']['path'],'Source cell')
        ck=rec['chroma_key']; require(ck['implementation_sha256']==sha(key_path) and ck['threshold']==100 and ck['edge_threshold']==150,'Unknown chroma implementation/parameters')
        keyed=keyer.remove_bg_magenta(cell.copy(),100,150); same(keyed,OUT/stages['keyed']['path'],'Chroma cleanup')
        source_alpha=np.asarray(keyed)[:,:,3]
        require(not any(np.any(e) for e in (source_alpha[0],source_alpha[-1],source_alpha[:,0],source_alpha[:,-1])),f'Original source cell was clipped/touched border: {key}')
        require(rec['source_cell_qc']['edge_touch_alpha_gt_0'] is False,'Source border QC missing')
        sw,sh=keyed.size; half=max(1,int(round(sw*.25))); mid=sw//2
        source_scale=float(np.sqrt(np.count_nonzero(source_alpha[:,max(0,mid-half):min(sw,mid+half)])/(sw*sh)))
        require(abs(rec['source_cell_qc']['body_scale']-source_scale)<1e-12,'Source body-scale evidence differs from raw pixels')
        norm=rec['whole_cell_normalization']; factor=512/max(raw.width/cols,raw.height/rows)
        require(norm['scale']==factor and norm['bbox_fit'] is False and norm['common_scale']==1.0,'Noncanonical or per-subject scaling')
        size=[round(cell.width*factor),round(cell.height*factor)]
        require(norm['source_cell_size']==list(cell.size) and norm['normalized_size']==size and norm['resample']=='LANCZOS','Wrong complete-cell normalization')
        normalized=keyed.resize(size,Image.Resampling.LANCZOS) if keyed.size!=tuple(size) else keyed.copy()
        same(normalized,OUT/stages['normalized']['path'],'Normalized full cell')
        e=rec['edge_despill']; require(e['implementation_sha256']==sha(edge_path) and e['radius_px'] in (2,4) and e['reference_radius_px']==3*e['radius_px'],'Unknown edge cleanup')
        cleaned,stats=edge.despill(normalized,radius=e['radius_px'],reference_radius=e['reference_radius_px']); same(cleaned,OUT/stages['cleaned']['path'],'Edge cleanup')
        require(np.array_equal(np.asarray(normalized)[:,:,3],np.asarray(cleaned)[:,:,3]),'Edge cleanup changed alpha')
        require(np.array_equal(np.asarray(normalized)[:,:,1],np.asarray(cleaned)[:,:,1]),'Edge cleanup changed green')
        require(stats['protected_red_changes']==0 and stats['outside_band_changes']==0,'Edge cleanup altered protected pixels')
        ref=bm['alignment']['direction_references'][d]; require(rec['reference']==ref and rec['alignment_version']==3,'Changed V3 reference')
        a=np.asarray(cleaned); ax,ay=anchor(a,ref['roi_height_px']); delta=[round(ref['target_head_px'][0]-ax),ref['target_head_px'][1]-ay]
        require(rec['translation_px']==delta and all(isinstance(v,int) for v in delta),'Wrong integer translation')
        yy,xx=np.where(a[:,:,3]>0); moved=[int(xx.min())+delta[0],int(yy.min())+delta[1],int(xx.max())+delta[0],int(yy.max())+delta[1]]
        require(min(moved[:2])>=1 and max(moved[2:])<=510,'Translation clipped alpha or touched output boundary')
        rebuilt=Image.new('RGBA',(512,512)); rebuilt.paste(cleaned,tuple(delta))
        same(rebuilt,OUT/rec['output'],'Reconstructed final frame'); same(rebuilt,OUT/stages['final']['path'],'Final evidence')
        require(sha(OUT/rec['output'])==rec['output_sha256'],'Final source mapping SHA changed')
        generation_evidence.append({'frame':key,'source_sha256':s['sha256'],'source_cell_xyxy':s['cell_xyxy'],'output_sha256':rec['output_sha256']})
    directions={}; means=[]
    for d in DIRS:
        frames=[pixels(OUT/f'walk/{d}/{i:02d}.png') for i in range(1,17)]; strip=pixels(OUT/f'walk/{d}/strip.png'); idle=pixels(OUT/f'idle/{d}.png')
        hashes=[hashlib.sha256(a.tobytes()).hexdigest() for a in frames]
        require(len(set(hashes))==16,f'Duplicate pose pixels: {d}')
        require(hashlib.sha256(idle.tobytes()).hexdigest() not in hashes,f'Idle copied walk: {d}')
        for n,a in enumerate(frames): require(np.array_equal(a,strip[:,n*512:(n+1)*512]),f'Strip order or pixel mismatch: {d}/{n+1}')
        ref=bm['alignment']['direction_references'][d]; heights=[]; anchors=[]
        for a in [idle,*frames]:
            alpha=a[:,:,3]; require(not any(np.any(v) for v in [alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]),f'Alpha touches boundary: {d}')
            x,y=anchor(a,ref['roi_height_px']); require(abs(x-256)<=.5 and y==ref['target_head_px'][1],f'Head alignment failed: {d}: {x,y}')
            yy,xx=np.where(alpha>8); heights.append(int(yy.max()-yy.min()+1)); anchors.append([x,y])
        mean=float(np.mean(heights[1:])); scale_samples=[]
        for a in frames:
            # Independently implement the V12 central-half area scale proxy.
            height,width=a.shape[:2]; half=max(1,int(round(width*.25))); center=width//2
            area=np.count_nonzero(a[:,max(0,center-half):min(width,center+half),3])
            scale_samples.append(float(np.sqrt(area/(height*width))))
        cv=float(np.std(scale_samples)/np.mean(scale_samples)); drift=abs(heights[0]/mean-1)
        require(cv<=.08 and drift<=.08,f'Body scale gate failed: {d}')
        means.append(mean); directions[d]={'unique_frames':16,'strip_cells_equal':16,'body_scale_cv':cv,'body_scale_samples':scale_samples,'body_scale_definition':'sqrt(nonzero_alpha_in_central_50_percent_width / full_cell_area), measured on uniformly aligned output cells','body_height_cv_record_only':float(np.std(heights[1:])/mean),'idle_walk_height_drift':drift,'head_anchors':anchors}
    require(max(means)/min(means)<=1.10,'Cross-direction average-height gate failed')
    visual='pending'; visual_sha=None
    if not ignore_previous_visual and (OUT/'review/visual-review.json').exists():
        v=load(OUT/'review/visual-review.json'); visual=v.get('status','pending')
        if visual=='passed':
            require(v.get('reviewed_manifest_sha256')==sha(OUT/'manifest.json') and v.get('reviewed_qc_sha256')==sha(OUT/'qc.json'),'Visual review belongs to an earlier candidate revision')
            visual_sha=sha(OUT/'review/visual-review.json')
            require(set(v.get('reviewed_directions',[]))==set(DIRS) and v.get('normal_size_review') and v.get('enlarged_review') and v.get('seam_15_16_01_review') and v.get('anatomical_contacts_01_09_review'),'Visual review scope incomplete')
    if require_visual: require(visual=='passed','All eight directions still require visual inspection')
    return {'version':13,'character_id':'24_lu_dongbin','status':'passed' if visual=='passed' else 'passed_exports_pending_visual','verified_at_utc':datetime.now(timezone.utc).isoformat(),
      'manifest_sha256':sha(OUT/'manifest.json'),'qc_sha256':sha(OUT/'qc.json'),'visual_review_sha256':visual_sha,'baseline_manifest_sha256':FROZEN_MANIFEST,'preserved_old_walk':64,'preserved_idle':8,'preserved_portrait':1,'generated_new_walk':64,'delivery_pngs':145,'alignment_version':3,'cycle_duration_ms':480,'cross_direction_mean_height_ratio':max(means)/min(means),'directions':directions,'generated_provenance':generation_evidence,'artifacts':artifacts}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--require-visual',action='store_true'); a=p.parse_args()
    try: result=verify(a.require_visual); code=0
    except Exception as e: result={'version':13,'status':'failed','verified_at_utc':datetime.now(timezone.utc).isoformat(),'error':str(e)}; code=1
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'validation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('directions','generated_provenance','artifacts')},ensure_ascii=False)); return code
if __name__=='__main__': sys.exit(main())
