"""Import one AI edge-restored idle without touching the old 512 source."""
from pathlib import Path
from types import SimpleNamespace
import argparse,json,shutil
from PIL import Image,ImageDraw
import import_frame as shared
HERE=Path(__file__).resolve().parent;CHAR=shared.CHARACTER
p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--batch-id',required=True);p.add_argument('--direction',choices=['N','NE','E','SE','S','SW','W','NW'],required=True);p.add_argument('--staging-root',type=Path,default=HERE/'work-idle-final');a=p.parse_args()
archive=a.archive.resolve();stage=a.staging_root.resolve();assert stage.is_relative_to(HERE.resolve())
binding=shared.migration_binding(archive);out=stage/'candidate'/CHAR;key=f'idle/{a.direction}.png'
assert not (out/'source'/a.batch_id).exists()
pipe=shared.module('idle_restore_pipeline06',HERE/'alpha_pipeline.py');pipe.output=lambda character:out if character==CHAR else None;pipe.preview=lambda:None
pipe.import_sheet(SimpleNamespace(command='import-idle',character=CHAR,direction=a.direction,source=archive/'raw.png',prompt=archive/'prompt.txt',receipt=archive/'generation-receipt.json',batch_id=a.batch_id,common_scale=.88,chroma_profile='native-alpha',rows=1,cols=1,source_cell_indices=None,idle_order=None,output_frames=None,start_frame=1))
v=shared.module('idle_restore_verify06',HERE/'alpha_verify.py');v.ROOT=stage;v.mod=lambda name:shared.module('idle_verify_'+name,shared.ROOT/'tools/vendor'/f'{name}.py')
result=v.verify(CHAR,a.direction,False,None,idle_only=True)
shared.write(out/f'review/validation-idle-{a.direction}.json',result)
original=shared.IMAGE_ROOT/'qdao_original_roster_v13/candidate'/CHAR/key
shared.write(out/(key+'.generation.json'),{'file':key,'sha256':shared.sha(out/key),'derivedFrom':{'path':str(archive/'raw.png'),'sha256':shared.sha(archive/'raw.png'),'generationRecord':str(archive/'raw.png.generation.json'),'receipt':str(archive/'generation-receipt.json')},'restorationReference':{'path':str(original),'sha256':shared.sha(original),'size':[512,512],'preserved_original_bytes':True},'operation':'AI-edge-restoration then whole-cell .88 downsample and integer anchor','profile':'native-alpha','actualModel':None,'actualQuality':None})
shared.write(out/'recovery-bindings'/a.batch_id/'migration-binding.json',binding)
for mode,color in [('dark',(30,38,46)),('light',(240,238,228))]:
 im=Image.open(out/key);canvas=Image.new('RGB',(1024,1088),color);canvas.paste(im,(0,48),im);ImageDraw.Draw(canvas).text((16,16),'idle '+a.direction+' / AI edge restored',fill='white' if mode=='dark' else 'black');dest=out/f'review/backgrounds/idle-{a.direction}-{mode}.png';dest.parent.mkdir(parents=True,exist_ok=True);canvas.save(dest)
print(json.dumps({'key':key,'sha256':shared.sha(out/key),'independent_reconstruction':result,'old_png_untouched':str(original)}))
