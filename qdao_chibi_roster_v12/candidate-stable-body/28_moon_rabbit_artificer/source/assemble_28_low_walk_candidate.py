#!/usr/bin/env python3
"""Rebuild canonical 28 and replace exactly the 22 reviewed low-walk cells."""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent.parent
SOURCE=ROOT/'source'
REVIEW=BASE/'review/28_low_walk_fixes'
DIRECTIONS=('N','NE','E','SE','S','SW','W','NW')
PAIRS={'s_e':('S','E'),'n_w':('N','W'),'ne_sw':('NE','SW'),'nw_se':('NW','SE')}
CELL=443

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pixel(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def box(i):return(i%4*CELL,i//4*CELL,(i%4+1)*CELL,(i//4+1)*CELL)
def main():
    assert ROOT.resolve().is_relative_to((BASE/'candidate-stable-body').resolve())
    picks=read(REVIEW/'selected-all-22.json')
    assert len(picks)==22 and len({(x['direction'],x['canonical_phase']) for x in picks})==22
    for x in picks:
        for key,digest in [('cell_path','cell_sha256'),('native_source_path','native_source_sha256'),('prompt_path','prompt_sha256'),('generation_record_path','generation_record_sha256')]:assert sha(x[key])==x[digest],x[key]
        assert Image.open(x['cell_path']).size==(443,443)
    # Existing canonical assembler preserves all original assets and earlier NW arm fixes.
    subprocess.run([sys.executable,'-X','utf8','-B',str(SOURCE/'assemble_28_candidate.py')],check=True,stdout=subprocess.PIPE,text=True,encoding='utf-8')
    config=read(ROOT/'direction-sources.json')
    prior={d:Image.open(SOURCE/f'walk-{d}-final.png').convert('RGBA') for d in DIRECTIONS}
    prior_a={d:read(SOURCE/f'walk-{d}-final.assembly.json') for d in DIRECTIONS}
    protected={name:sha(SOURCE/name) for name in ['idle.png','portrait-daoist.png']}
    prov=SOURCE/'provenance/low-walk';prov.mkdir(parents=True,exist_ok=True)
    for d in DIRECTIONS:write(prov/f'{d}-before-low.assembly.json',prior_a[d])
    shutil.copy2(REVIEW/'selected-all-22.json',prov/'selected-all-22.json')
    shutil.copy2(REVIEW/'repair-plan.json',prov/'repair-plan.json')
    chosen={(x['direction'],x['canonical_phase']):x for x in picks}
    rows=[];directions={};unchanged=0;inventory={}
    for d in DIRECTIONS:
        out=prior[d].copy();records=[]
        for i in range(8):
            phase=i+1;rec=dict(prior_a[d]['sources'][i]);pick=chosen.get((d,phase))
            if pick:
                pdir=prov/d;pdir.mkdir(exist_ok=True)
                cell_dest=pdir/f'{phase:02d}-cell.png';shutil.copy2(pick['cell_path'],cell_dest)
                # Keep the actual original native image, prompt and generation record as source evidence.
                for key in ['native_source_path','prompt_path','generation_record_path']:
                    src=Path(pick[key]);dest=pdir/src.name
                    if not dest.exists():shutil.copy2(src,dest)
                    assert sha(src)==sha(dest)
                    inventory[str(src)]=sha(src);inventory[str(dest)]=sha(dest)
                cell=Image.open(cell_dest).convert('RGBA')
                assert pixel(cell)==pick['cell_rgba_sha256']
                out.paste(cell,box(i)[:2])
                config[d][i]={'source':str(cell_dest),'rows':1,'cols':1,'index':0,'original_phase':pick['original_phase'],'canonical_phase':phase,'edit_scope':'low-walk moving leg only; existing opposing arms retained','upstream_native_provenance':pick}
                rec.update(config[d][i]);rec.update({'source_path':str(cell_dest),'source_sha256':sha(cell_dest),'source_native_size':[443,443],'source_crop':[0,0,443,443],'uniform_whole_cell_scale':1.0,'normalized_cell_size':[443,443],'output_cell_box':list(box(i)),'output_cell_rgba_sha256':pixel(cell),'low_walk_generation':pick,'previous_selected_source_record':prior_a[d]['sources'][i]})
            else:
                assert out.crop(box(i)).tobytes()==prior[d].crop(box(i)).tobytes();unchanged+=1
                rec['low_walk_preserved_pixel_exact']=True
            rec.update({'direction':d,'phase':phase,'per_subject_fit':False,'mirrored':False,'synthetic_pose_or_interpolation':False})
            inventory[rec['source_path']]=sha(rec['source_path']);records.append(rec);rows.append(rec)
        path=SOURCE/f'walk-{d}-final.png'
        if any(k[0]==d for k in chosen):out.save(path)
        assert Image.open(path).convert('RGBA').tobytes()==out.tobytes()
        a={'version':12,'operation':'canonical original cells with exactly 22 builtin-imagegen low-walk local edits; all other 42 walk cells unchanged','output_path':str(path),'output_sha256':sha(path),'output_size':[1772,886],'output_grid':[4,2],'direction':d,'sources':records,'phase_rotation':prior_a[d]['phase_rotation'],'original_phases_in_new_order':prior_a[d]['original_phases_in_new_order'],'new_poses_generated_by_script':False,'mirroring':False,'interpolation_or_duplicate_pose':False,'per_subject_fit':False,'upstream_canonical_assembly':str(prov/f'{d}-before-low.assembly.json')}
        write(path.with_suffix('.assembly.json'),a);directions[d]=(out,path,a)
    assert unchanged==42
    paired={}
    for kind,ds in PAIRS.items():
        canvas=Image.new('RGBA',(1772,1772),(255,0,255,255));frames=[]
        for k,d in enumerate(ds):
            im,path,a=directions[d]
            for i in range(8):
                cell=im.crop(box(i));dst=box(k*8+i);canvas.paste(cell,dst[:2]);frames.append({'direction':d,'phase':i+1,'source_path':str(path),'source_sha256':sha(path),'source_crop_box':list(box(i)),'output_cell_box':list(dst),'source_crop_rgba_sha256':pixel(cell),'whole_cell_scale':1.0})
        path=SOURCE/f'{kind}.png';canvas.save(path)
        write(path.with_suffix('.assembly.json'),{'version':12,'operation':'exact whole-cell pairing of two independent canonical directions','output_path':str(path),'output_sha256':sha(path),'output_size':[1772,1772],'output_grid':[4,4],'direction_order':list(ds),'sources':[{'path':str(directions[d][1]),'sha256':sha(directions[d][1]),'upstream_assembly_path':str(directions[d][1].with_suffix('.assembly.json'))} for d in ds],'frames':frames,'new_poses_generated_by_script':False,'per_frame_body_fit':False,'mirrored_frames':False,'interpolation':False})
        paired[kind]={'path':str(path),'sha256':sha(path),'grid':[4,4],'direction_order':list(ds)}
    for name,digest in protected.items():assert sha(SOURCE/name)==digest
    paired['idle']={'path':str(SOURCE/'idle.png'),'sha256':sha(SOURCE/'idle.png'),'grid':[4,2],'direction_order':list(DIRECTIONS)}
    phase_plan=read(SOURCE/'phase-plan.json');phase_plan['low_walk_revision']={'changed_canonical_phases':{d:[x['canonical_phase'] for x in picks if x['direction']==d] for d in DIRECTIONS},'existing_cyclic_offsets_unchanged':True,'preserved_walk_cells':42,'preserved_idle_frames':8,'preserved_portrait':True,'source_map':str(prov/'selected-all-22.json')}
    write(SOURCE/'phase-plan.json',phase_plan)
    write(ROOT/'direction-sources.json',config);write(SOURCE/'cell-source-map.json',rows)
    write(SOURCE/'source-inventory-sha256.json',[{'path':p,'sha256':h} for p,h in sorted(inventory.items())])
    write(SOURCE/'candidate-sources.json',{'character_id':ROOT.name,'sources':paired,'portrait_raw':{'path':str(SOURCE/'portrait-daoist.png'),'sha256':sha(SOURCE/'portrait-daoist.png')},'checks':{'preserved_other_walk_cells':42,'new_low_walk_local_edits':22,'unique_authored_walk_frames':64,'independent_idle_frames':8,'idle_and_portrait_sources_byte_identical':True,'original_files_unmodified':True},'phase_policy':'Existing canonical RIGHT-first full cycles and offsets unchanged','phase_plan':str(SOURCE/'phase-plan.json')})
    write(ROOT/'candidate-plan.json',{'character_id':ROOT.name,'display_name_zh':'月兔机关师','stage':'low-walk candidate pending root visual review; do not seal or publish','changes':phase_plan['low_walk_revision'],'scale_policy':'one common scale1.02941176470588 for72; v3 stable-body translation; no individual body fit','edge_despill_radius':4,'original_directories_read_only':True})
    write(REVIEW/'assembly-validation.json',{'status':'passed','changed_cells':22,'unchanged_walk_cells_pixel_exact':unchanged,'idle_source_byte_identical':True,'portrait_source_byte_identical':True,'canonical_offsets_unchanged':True,'upstream_native_reconstruction_verified':22,'source_map':str(SOURCE/'cell-source-map.json')})
    print('Low walk sources assembled:22 replacements;42 original walk cells+8 idle+portrait preserved')
if __name__=='__main__':main()
