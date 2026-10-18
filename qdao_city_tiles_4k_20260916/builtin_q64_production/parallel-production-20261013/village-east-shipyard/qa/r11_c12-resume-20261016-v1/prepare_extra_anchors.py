import sys,json
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import batch_production as b
def prepare(patch, anchors, description, excluded=None):
 with b.batch_writer_lock():
  g=b.gate(required=True);s=b.state();tile='r11_c12';geo=b.geometry(tile,patch);folder=b.OUT/tile
  assert not [c for c in g.get('actualCoordinateConflicts',[]) if c['tile']==tile and c.get('patch') in (None,patch)]
  version=1
  while (folder/f'requests/{patch}-v{version}.request.json').exists():version+=1
  layout=Path(b.read(b.MAP/'production-contract.json')['layoutReference']);scale=1254/57344
  with Image.open(layout) as im:
   guide=im.convert('RGB').transform((1254,1254),Image.Transform.EXTENT,tuple(x*scale for x in geo['nativeGlobalBox']),resample=Image.Resampling.BICUBIC)
   margin=2048;world=[geo['nativeGlobalBox'][0]-margin,geo['nativeGlobalBox'][1]-margin,geo['nativeGlobalBox'][2]+margin,geo['nativeGlobalBox'][3]+margin]
   context=im.convert('RGB').transform((768,768),Image.Transform.EXTENT,tuple(x*scale for x in world),resample=Image.Resampling.BICUBIC)
  ImageDraw.Draw(context).rectangle((294,294,474,474),outline=(255,0,180),width=3)
  lp=folder/f'layout-only/{patch}-v{version}-layout-only.png';guide.save(lp)
  cp=folder/f'layout-only/{patch}-v{version}-layout-context-target-box.png';context.save(cp)
  conditioned=guide.copy();refs=[];pasted=[]
  specs={'left':([1024,0,1254,1254],[0,0],'east'),'right':([0,0,230,1254],[1024,0],'west'),'top':([0,1024,1254,1254],[0,0],'south'),'bottom':([0,0,1254,230],[0,1024],'north')}
  for direction,neighbor in anchors:
   rec=s['selected'][tile+'_'+neighbor];crop,dest,edge=specs[direction]
   assert rec.get('continuationAllowed',{}).get(edge) is not False
   assert b.sha(rec['path'])==rec['sha256']
   with Image.open(rec['path']) as im:
    part=im.convert('RGB').crop(crop);conditioned.paste(part,dest)
   rp=folder/f'layout-only/{patch}-v{version}-{direction}-native-overlap.png';part.save(rp)
   ref=b.info(rp,direction+' unscaled immediate-native overlap');ref.update(originalNativeSource=rec,sourceCrop=crop,pasteAt=dest,classification='reference input only; not new generated art');refs.append(ref)
   pasted.append({'direction':direction,'source':rec,'sourceCrop':crop,'pasteAt':dest,'operation':'unscaled exact world-coordinate adjacent overlap'})
  target=folder/f'layout-only/{patch}-v{version}-conditioned-target.png';conditioned.save(target)
  style=b.ROOT/'designs/mail-ui-v1/01-mail-event.png'
  allrefs=[b.info(target,'edit target; sharp strips fixed, blurry layout to redraw')]+refs+[b.info(lp,'exact coordinate layout only; geometry guide'),b.info(style,'approved Daoist Q painterly style, no UI night people copied')]
  role_text='; '.join(f'Image{i+1}: '+r['role'] for i,r in enumerate(allrefs))
  prompt=f'''Use case: precise-object-edit / native game-map continuation. Produce one opaque 1254x1254 native patch {tile}/{patch}, final unscaled core [115,115,1139,1139].
Input roles: {role_text}.
Image1 contains original finished native strips at the named sides, each exactly 230 pixels. Preserve their position and scale, and connect every diagonal plank edge, end joint, grain, shadow, rope and waterline into the newly rendered middle. The blurry remainder only locates approved geometry; replace it with sharp hand-painted native detail, never enlarge/sharpen it as final. Do not draw a pasted edge or hard material step at 230/1024 boundaries. No zoom out, rotation, reframing, fitting whole cropped objects inside target, nor copying an adjacent whole object.
Scene: {description}
Style: refined rounded Daoist Q high-definition hand-painted game environment, warm natural wooden planks, blue-green sea and clean soft daylight shadows. Match existing native brushwork, exact perspective, board width and color. Target native world box {geo['nativeGlobalBox']}. Tight cropped location only.
Constraints: retain approved original object counts and footprints; preserve open routes. No extra posts, caps, furniture, barrels, ships, buildings, bridge, land, NPC, animal, text, UI, watermark or frame. Cropped objects continue beyond image; do not invent termination/base. Output exactly 1254 square opaque sharp native artwork.'''
  req={'schemaVersion':1,'submittedAtUtc':b.now(),'key':tile+'_'+patch,'version':version,'tool':'image_gen__imagegen','generationMode':'builtin','prompt':prompt,'referenced_image_paths':[r['path'] for r in allrefs],'referenceRolesAndHashes':allrefs,'transparent_background':False,'geometry':geo,'conditionedGuide':{'file':b.info(target),'layoutOnlySource':b.info(layout),'pastedNativeReferences':pasted,'classification':'reference conditioning only; no layout pixels final'},'excludedFailedAnchors':excluded or [],'ownerGate':g,'rootInstructionsReadBeforeCall':b.info(b.ROOT/'AGENTS.md'),'splitReadBeforeCall':b.info(b.ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'widerContextForHumanReviewOnly':b.info(cp),'actualModel':None,'actualQuality':None,'paidApiUsed':False,'status':'prepared_not_yet_submitted'}
  rp=folder/f'requests/{patch}-v{version}.request.json';b.save(rp,req);rp.with_suffix('.prompt.txt').write_text(prompt,encoding='utf-8');s['requests'].append(str(rp));b.checkpoint(s,'prepared extra stable anchors '+req['key']);print(json.dumps({'request':str(rp),'target':str(target),'guide':str(lp),'context':str(cp)}))
if __name__=='__main__':
 if sys.argv[1]=='p32':prepare('p32',[('left','p31'),('right','p33')],'ONLY open warm wooden deck with the same diagonal boards, long joints, clean grain and soft original post shadows. No independent pole, furniture, water hole or other object. The original front-pile cap remains outside the frame in left neighbor; do not duplicate it.')
 if sys.argv[1]=='p42':prepare('p42',[('left','p41'),('right','p43'),('top','p32')],'Continue the original diagonal front lip of the dock, original short connector wood/rope where approved, blue water beneath. The upper half remains open wood deck. No tall pole or new cap; neighboring pile remains outside left. Keep original lower sea negative space; do not fill water with boards.')
 if sys.argv[1]=='p22':prepare('p22',[('right','p23'),('bottom','p32')],'Mainly open warm wood deck. Preserve the original diagonal blue-water corner only along upper-right. No independent support post in this core, no added cap or barrel; only original tall net-column lower fragment may touch extreme top-left as exact approved guide. Connect diagonal board widths precisely with RIGHT and BOTTOM sharp native strips.',[{'key':'r11_c12_p12','direction':'south','reason':'known short-column incorrect termination excluded, retained pending'},{'key':'r11_c12_p21','direction':'east','reason':'uncleared shaft/base footprint excluded, retained pending'}])

