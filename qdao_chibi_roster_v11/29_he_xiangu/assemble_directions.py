"""Deterministic layout of original ImageGen 2x2 walk drawings; no synthesized poses."""
from pathlib import Path
import sys,json,importlib.util,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sprite',Path.home()/'.agents/skills/generate2dsprite/scripts/generate2dsprite.py')
sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp)
spec2=importlib.util.spec_from_file_location('roster',ROOT/'process_roster.py')
rp=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(rp)
char=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
out={}
record={'operation':'layout only: chroma cleanup, complete component bounding crops, one isotropic scale for each direction, per-frame foot translation','mirrored':False,'synthetic':False,'sources':{}}
for direction in ['S','W','E','N','SW','NW','NE','SE']:
 path=char/'sources'/('walk_'+direction+'_2x2.png')
 if not path.exists(): raise FileNotFoundError(path)
 raw=Image.open(path).convert('RGBA')
 clean=sp.remove_bg_magenta(raw.copy())
 comps=sp.connected_components(clean,min_area=500)
 if len(comps)!=4: raise ValueError(f'{direction}: {len(comps)} main components instead of 4')
 comps.sort(key=lambda c:(int(((c['bbox'][1]+c['bbox'][3])/2)>raw.height/2),c['bbox'][0]))
 frames=[];boxes=[]
 for c in comps:
  if c['touches_edge']: raise ValueError(f'{direction} source silhouette touches native image edge')
  box=sp.pad_bbox(c['bbox'],2,raw.width,raw.height)
  boxes.append(box);frames.append(clean.crop(box))
 selected=[{'file':path.relative_to(char).as_posix(),'cell_index':i,'sha256':rp.sha(path)} for i in range(4)]
 if direction in ('NE','SE'):
  correction=char/'sources'/('walk_NE_correction1.png' if direction=='NE' else 'walk_SE_correction2.png')
  cr=Image.open(correction).convert('RGBA');cc=sp.remove_bg_magenta(cr.copy())
  cp=sp.connected_components(cc,min_area=500)
  if len(cp)!=4: raise ValueError('NE correction must contain four complete components')
  cp.sort(key=lambda c:(int(((c['bbox'][1]+c['bbox'][3])/2)>cr.height/2),c['bbox'][0]))
  chosen=cp[3]
  if chosen['touches_edge']: raise ValueError('NE corrected frame4 touches edge')
  replacement_box=sp.pad_bbox(chosen['bbox'],2,cr.width,cr.height)
  frames[3]=cc.crop(replacement_box)
  selected[3]={'file':correction.relative_to(char).as_posix(),'cell_index':3,'sha256':rp.sha(correction),'component_box':replacement_box,'native_size':list(cr.size),'prompt_file':'prompts/'+correction.stem+'.txt'}
 heights=[rp.bounds(f)[3]-rp.bounds(f)[1] for f in frames]
 common=420/max(heights)
 aligned=[]
 for f in frames:
  p,info=rp.normalized_frame(f,common); aligned.append(p)
 out[direction]=aligned
 record['sources'][direction]={'file':path.relative_to(char).as_posix(),'source':'built-in image_gen','sha256':rp.sha(path),'native_size':list(raw.size),'layout':'2x2 reading order TL TR BL BR','component_boxes':boxes,'same_scale_all_four_frames':common,'native_subject_heights':heights}
 record['sources'][direction]['selected_frame_sources']=selected
 record['sources'][direction]['generation_prompt']='prompts/walk_'+direction+'_2x2.txt'
 corrprompt=char/'prompts'/('walk_'+direction+'_correction1.txt')
 if corrprompt.exists(): record['sources'][direction]['correction_prompt']=corrprompt.relative_to(char).as_posix()
 print(direction,heights,common)
for kind,dirs in rp.ROWS.items():
 final=rp.compose([f for d in dirs for f in out[d]],4)
 final.save(char/'sources'/(kind+'_assembled.png'))
 prompt='This is a deterministic 4x4 layout assembled from four built-in ImageGen 2x2 directional walk sheets. Original generation prompts: '+', '.join('prompts/walk_'+d+'_2x2.txt' for d in dirs)+'. Row order '+','.join(dirs)+'. Layout provenance in sources/assembly.json. No synthetic, copied, mirrored, rotated or deformed poses.'
 (char/'prompts'/(kind+'_assembled.txt')).write_text(prompt,encoding='utf8')
(char/'sources'/'assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')

