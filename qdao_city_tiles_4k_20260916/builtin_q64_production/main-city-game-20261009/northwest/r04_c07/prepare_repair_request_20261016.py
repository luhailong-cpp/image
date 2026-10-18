from pathlib import Path
import sys,json
from PIL import Image
T=Path(__file__).resolve().parent; Z=T.parent;sys.path.insert(0,str(Z));import production_v2 as p
pid,oldid,newid=sys.argv[1:4]
rules=(p.REPO/'AGENTS.md').read_text(encoding='utf-8-sig');split=p.read(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert T.name not in {t for b in split['batches'] if b['map']=='main-city-game-20261009' and b['status']=='allocated_root_reserved' for t in b['tiles']}
rulesRecord={'agentsSha256':p.sha(p.REPO/'AGENTS.md'),'splitSha256':p.sha(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'rulesActuallyRead':True}
d=p.read(T/'layout-only'/(oldid+'.actual-core-guide.png.derivation.json'))
native=T/'native'/(oldid+'.png');base=Image.open(native).convert('RGB')
for a in d['nativeAnchors']:base.paste(Image.open(a['file']).convert('RGB').crop(a['sourceBox']),a['targetBox'][:2])
guide=T/'layout-only'/(newid+'.actual-core-guide.png');p.save_png(guide,base)
d['role']='Edit target with authoritative native anchors; failed old source is repair context only, not selected'
d['editBase']={'file':str(native),'sha256':p.sha(native)};d['rules']=rulesRecord
p.write_json(guide.with_suffix('.png.derivation.json'),d)
a=d['nativeAnchors'][0];src=Image.open(a['file']).convert('RGB');w=d['worldBox'];b=a['worldBox'];x=max(0,min(w[0]-b[0],src.width-1254));y=0
ctx=T/'layout-only'/(newid+'.south-context.png');p.save_png(ctx,src.crop((x,y,x+1254,y+1254)))
p.write_json(ctx.with_suffix('.png.derivation.json'),{'role':'Actual south final context only; unscaled crop not a new source','file':str(a['file']),'sha256':a['sha256'],'crop':[x,y,x+1254,y+1254],'worldBox':[b[0]+x,b[1]+y,b[0]+x+1254,b[1]+y+1254],'sourceResampled':False})
scene=sys.argv[4]
prompt=f'''Use case: precise-object-edit. Return a native opaque 1254x1254 image at exactly the same field of view as Image 1. Image 1 is the edit target for {T.name}/{newid}, world box {w}. Image 2 is an unscaled crop from the already approved SOUTH neighbor, for stone scale and material context only; do not copy or move its full extent into output. Correct only the specified paving-joint defects in Image 1. Fixed bottom anchor y1139..1253 is authoritative neighbor art: retain it exactly. Center crop [115,115,1139,1139] will be used. {scene} Keep all other geometry, palette, stone texture, light, camera, and object scale unchanged. The ground is a flat horizontal plane throughout. Match precise continuous seam endpoints with no staircase, dogleg, doubled joint or T-shaped dead end. No new objects, decorations, lettering, border, comparison, blur or resize.'''
args={'prompt':prompt,'referenced_image_paths':[str(guide),str(ctx)],'transparent_background':False}
if sys.argv[-1]=='single':
 args['referenced_image_paths']=[str(guide)]
 args['prompt']=prompt.replace('Image 2 is an unscaled crop from the already approved SOUTH neighbor, for stone scale and material context only; do not copy or move its full extent into output.','Only this target is supplied, with exact same-world native anchor strips already pasted in place.')
p.write_json(T/'planned'/(newid+'.parameters.json'),args)
p.write_json(T/'receipts'/(newid+'.rules-read.json'),rulesRecord)
p.record_request(T.name,newid,T/'planned'/(newid+'.parameters.json'))
print(json.dumps(args))

