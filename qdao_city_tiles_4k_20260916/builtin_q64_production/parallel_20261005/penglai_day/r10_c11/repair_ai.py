from pathlib import Path
import sys,json
from PIL import Image
sys.dont_write_bytecode=True
T=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/r10_c11');R=T/'repairs';sys.path.insert(0,str(T));import helper as h
h.p.ROOT=R;(R/'native').mkdir(exist_ok=True);(R/'evidence').mkdir(exist_ok=True)
def prepare():
 raw=T/'tiles/r10_c11-candidate.png';im=Image.open(raw).convert('RGB')
 for name,x in [('cliff-left',0),('cliff-center',1024)]:
  target=R/(name+'-target.png');im.crop((x,2445,x+1254,3699)).save(target);h.p.derived(target,[raw],{'method':'native exact seam context','boxLTRB':[x,2445,x+1254,3699]})
  prompt='Use case: precise native seam repair. Image1 is the actual assembled map patch and EDIT TARGET. Image2 is the approved PRIMARY painting style only; never add UI. Repair ONLY the artificial horizontal material seam at y627 through the cliff rock faces in Image1. Make the handpainted rock shading and strokes continuous across that boundary. Preserve all existing rock silhouettes, large cracks, vegetation, water shoreline and foam exactly in their current positions. Do not change rock count or alter the crack topology. Keep every boundary endpoint and the outer250 pixels substantially unchanged, with all rebuilding around middle. Bright clean rounded Taoist Q fantasy illustration, same restrained warm ivory rock faces and cool blue-gray shadow, crisp native edges. No new cracks, no added rocks, no additional bushes, no denser texture, no noise, no blur, no camera/crop/scale change. Return same square native1254x1254 composition.'
  call={'prompt':prompt,'referenced_image_paths':[target.as_posix(),h.STYLE],'transparent_background':False};(R/(name+'.prompt.txt')).write_text(prompt,encoding='utf8');h.p.write(R/(name+'.call.json'),call)
def ingest(source,name):
 call=h.p.read(R/(name+'.call.json'));dest=h.p.ingest(source,name,R/(name+'.prompt.txt'),call['referenced_image_paths'],'native_seam_repair');j=h.p.read(str(dest)+'.generation.json');j['evidence']['toolOutputHintFile']=str(R/'evidence'/f'{name}.tool-result.json');h.p.write(str(dest)+'.generation.json',j)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
