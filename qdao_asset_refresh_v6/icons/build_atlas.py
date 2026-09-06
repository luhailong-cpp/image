"""Rebuild the unchanged FairyGUI icon atlas geometry from the final 600px icons."""
from pathlib import Path
import argparse,json,hashlib,os,xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
PACK=ROOT/'q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600'
HERE=Path(__file__).resolve().parent
ATLAS=PACK/'fairygui_atlas';JSON=ATLAS/'qstyle_fairygui_atlas_600.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p,base):return Path(os.path.relpath(p,base)).as_posix()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();meta=json.loads(JSON.read_text(encoding='utf8'));xml=ET.parse(ATLAS/'qstyle_fairygui_atlas_600.xml').getroot();xml_frames={n.attrib['name']:n.attrib for n in xml}
 assert (meta['width'],meta['height'],meta['count'],meta['iconSize'],meta['padding'])==(7912,6088,124,600,8)
 png=ATLAS/meta['image'];atlas=Image.open(png).convert('RGBA') if a.check else Image.new('RGBA',(7912,6088),(0,0,0,0))
 records=[json.loads(p.read_text(encoding='utf8')) for p in sorted((HERE/'records').glob('batch[0-9][0-9].json'))];assert len(records)==8 and all(r['published'] for r in records)
 output_map={o['path']:(o,r) for r in records for o in r['outputs']};assert len(output_map)==124
 baseline=json.loads((ROOT/'docs/ART_ASSET_AUDIT.json').read_text(encoding='utf8'));old={x['path']:x for x in baseline['assets']};checks=[]
 for f in meta['frames']:
  src=PACK/f['group']/f['source_file'].replace('\\','/').split('/')[-1];im=Image.open(src).convert('RGBA');data=np.asarray(im);alpha=data[:,:,3];bbox=im.getchannel('A').getbbox();key=src.relative_to(ROOT).as_posix();rec,batch=output_map[key]
  assert im.size==(600,600) and alpha.min()==0 and alpha.max()==255
  assert bbox and bbox[0]>0 and bbox[1]>0 and bbox[2]<600 and bbox[3]<600
  assert not np.any((data[:,:,0]>160)&(data[:,:,2]>160)&(data[:,:,1]<100)&(alpha>10)),str(src)+' magenta spill'
  assert sha(src)==rec['sha256'] and sha(src)!=old[key]['baseline_sha256']
  for field in ['x','y','width','height','frameX','frameY','frameWidth','frameHeight']:assert int(xml_frames[f['name']][field])==f[field]
  rect=(f['x'],f['y'],f['x']+600,f['y']+600)
  if a.check:assert atlas.crop(rect).tobytes()==im.tobytes()
  else:atlas.paste(im,(f['x'],f['y']))
  f['source_file']=rel(src,ATLAS);checks.append({'path':key,'size':[600,600],'mode':'RGBA','alpha_range':[0,255],'bbox':list(bbox),'sha256':sha(src),'changed_from_baseline':True,'batch':batch['batch'],'cell_index':rec['cell_index']})
 if not a.check:
  atlas.save(png,optimize=True);meta['art_version']='daoist-q-v6';meta['source_paths_relative_to']='this JSON directory';meta['atlas_sha256']=sha(png);JSON.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  for group in ['west_eight_immortals_redrawn_100_600x600','character_artifacts_redrawn_24_600x600']:
   manifest=PACK/group/'manifest.json';prev=json.loads(manifest.read_text(encoding='utf8'));items=[]
   for it in prev['items']:
    src=PACK/group/it['file'];o,b=output_map[src.relative_to(ROOT).as_posix()]
    items.append({'index':it['index'],'name':it['name'],'file':it['file'],'size':[600,600],'mode':'RGBA','sha256':o['sha256'],'generation_record':rel(HERE/'records'/f"batch{b['batch']:02d}.json",manifest.parent),'cell_index':o['cell_index']})
   manifest.write_text(json.dumps({'count':len(items),'size':[600,600],'redrawn':True,'art_version':'daoist-q-v6','items':items},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  (PACK/'manifest_redrawn_600x600.json').write_text(json.dumps({'count':124,'size':[600,600],'redrawn':True,'art_version':'daoist-q-v6','groups':['west_eight_immortals_redrawn_100_600x600','character_artifacts_redrawn_24_600x600'],'generation_records':rel(HERE/'records',PACK),'source_sheets_policy':'Superseded source sheets and temporary extraction previews are removed after final validation; prompts, native hashes and processing records retained.','atlas':'fairygui_atlas/qstyle_fairygui_atlas_600.png'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  (HERE/'manifest.json').write_text(json.dumps({'art_version':'daoist-q-v6','count':124,'baseline_commit':'60134a6','image_generator':'built-in image_gen','skill':'generate2dsprite','grid_batches':8,'native_sizes':[r['raw_native_size'] for r in records],'final_size':[600,600],'native_size_note':'Final600pxiconcanvasisresampledfromactualnativegridcells;itdoesnotclaim600nativeAIpixelspericon.','atlas':{'path':png.relative_to(ROOT).as_posix(),'size':[7912,6088],'count':124,'frame_layout_preserved':True,'xml_unchanged':True,'sha256':sha(png)},'assets':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 validation={'count':124,'all_dimensions_600x600':True,'all_true_rgba':True,'all_changed_from_baseline':True,'all_transparent_borders':True,'magenta_spill_pixels':0,'atlas_size':[7912,6088],'atlas_sha256':sha(png),'xml_names_and_layout_unchanged':True,'exact_atlas_pixels_checked':a.check,'native_records':len(records)}
 (HERE/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(validation))
if __name__=='__main__':main()
