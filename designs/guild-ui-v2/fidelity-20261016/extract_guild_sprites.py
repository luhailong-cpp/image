from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,datetime,re
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'client/Assets/Resources/UI/Ugui/GuildFidelity20261016'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
config=json.loads((ROOT.parents[2]/'config/image-generation.json').read_text(encoding='utf-8-sig'))
original=ROOT.parents[1]/'gameplay-ui/04-guild.png'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
entries=[('guild-controls-clean.png','clean-guild-controls.txt',[original],'exec-c712f25c-4a29-450d-a7a6-ce4187c783e0.png'),('guild-empty-shell.png','empty-guild-shell.txt',[ROOT/'art/guild-controls-clean.png'],'exec-ad24cd5d-1835-4929-a287-c6999debd861.png'),('guild-progress-empty.png','empty-progress-track.txt',[ROOT/'art/guild-controls-clean.png'],'exec-a9740c37-58ad-4d73-a70f-e12400a706e3.png')]
for name,prompt,refs,cache in entries:
 p=ROOT/'art'/name
 with Image.open(p) as im:size=im.size
 stamp=re.search(rb'c2pa\.created.{0,32}?(20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)',p.read_bytes(),re.S)
 write(p.with_name(p.name+'.generation.json'),{'file':name,'sha256':sha(p),'generatedAt':stamp.group(1).decode() if stamp else now,'generatedAtBasis':'PNG declared c2pa.created.when, signature not validated' if stamp else 'recorded after call in this session','width':size[0],'height':size[1],'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'officialVerification':{'verifiedInThisTask':True,'release':config['sources']['release'],'model':config['sources']['model'],'quality':config['sources']['quality'],'finding':'Images 2.5 and premium Sunburst/max remain available; builtin has no model/quality selectors'},'submittedParameters':{'model':None,'quality':None,'prompt':str(ROOT/'prompts'/prompt),'referenced_image_paths':[str(x) for x in refs],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具未披露可核实的具体模型版本和质量参数。配置目标不是实际返回证据。','references':[{'path':str(p),'sha256':sha(p),'role':'edit-target'} for p in refs],'evidence':{'toolOutputPath':'C:/Users/luyua/.codex/generated_images/01a147f6-78cd-7e50-8857-3622cb8822f5/'+cache,'returnedKeys':['image_url','output_hint'],'embeddedAgentFamily':'gpt-image family label only, not a version/quality confirmation'},'review':{'status':'accepted for current runtime extraction','nativeUnityParityVerified':False}})
master=Image.open(ROOT/'art/guild-controls-clean.png').convert('RGBA')
empty=Image.open(ROOT/'art/guild-empty-shell.png').convert('RGBA')
progress=Image.open(ROOT/'art/guild-progress-empty.png').convert('RGBA')
orig=Image.open(original).convert('RGBA')
sprites=[]
def save(key,rect,border=(0,0,0,0),source='guild-controls-clean.png',circle=False):
 image=orig if source=='original' else empty if source=='guild-empty-shell.png' else progress if source=='guild-progress-empty.png' else master
 x,y,w,h=rect
 crop=image.crop((x,y,x+w,y+h))
 if circle:
  mask=Image.new('L',crop.size,0);ImageDraw.Draw(mask).ellipse((0,0,w-1,h-1),fill=255);crop.putalpha(mask)
 path=OUT/(key+'.png');crop.save(path)
 source_path=original if source=='original' else ROOT/'art'/source
 op='Native-pixel crop; no resampling'+('; circular alpha cutout only for default portrait frame' if circle else '')
 record={'file':path.name,'sha256':sha(path),'derivedAt':now,'width':w,'height':h,'format':'PNG','derivedFrom':[{'path':str(source_path),'sha256':sha(source_path),'generationRecord':str(ROOT.parents[1]/'gameplay-ui/04-guild.record.json') if source=='original' else str(source_path)+'.generation.json'}],'operation':op,'actualModel':None,'actualQuality':None,'modelBasis':'Inherited source record; actual version/quality not asserted by crop'}
 write(path.with_name(path.name+'.generation.json'),record)
 guid=hashlib.sha256(('guild-fidelity-20261016/'+key).encode()).hexdigest()[:32]
 path.with_name(path.name+'.meta').write_text(f'''fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
  isReadable: 0
  textureType: 8
  textureShape: 1
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  textureFormat: 1
  maxTextureSize: 4096
  textureCompression: 0
  compressionQuality: 100
  spriteMode: 1
  spritePixelsToUnits: 100
  spriteMeshType: 0
  spriteExtrude: 1
  spritePivot: {{x: 0.5, y: 0.5}}
  spriteBorder: {{x: {border[0]}, y: {border[1]}, z: {border[2]}, w: {border[3]}}}
  alphaIsTransparency: 1
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: {guid}
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  assetBundleName:
  assetBundleVariant:
''',encoding='utf-8')
 sprites.append({'key':key,'source':str(source_path),'sourceRectXYWH':list(rect),'assetPath':str(path.relative_to(ROOT/'client')).replace('\\','/'),'width':w,'height':h,'sha256':sha(path),'borderLeftBottomRightTop':list(border),'operation':op})
save('guild_empty_shell',(0,0,1932,814),source='guild-empty-shell.png')
save('guild_tab_selected',(189,85,316,65),(18,16,18,16))
save('guild_tab_normal',(515,88,273,62),(18,16,18,16))
save('guild_crest',(212,171,207,188))
save('guild_level_plate',(456,245,171,55),(21,15,21,15))
save('guild_announcement',(181,559,546,144),(18,15,18,15))
save('guild_row_normal',(795,256,957,55),(7,3,7,3))
save('guild_row_self',(795,311,957,57),(7,3,7,3))
save('guild_table_header',(795,217,957,40),(7,3,7,3))
save('guild_button_secondary',(340,710,229,58),(21,17,21,17))
save('guild_button_primary',(1365,692,414,80),(39,22,39,22))
save('guild_close',(1782,25,83,78))
save('guild_progress_track',(316,509,392,37),(13,12,13,12),source='guild-progress-empty.png')
save('guild_progress_fill',(329,516,250,22),(3,3,3,3))
for key,rect in [('guild_entry_donate',(795,552,218,126)),('guild_entry_scroll',(1026,552,220,126)),('guild_entry_activity',(1264,552,219,126)),('guild_entry_shop',(1496,552,245,126))]:save(key,rect,(14,13,14,13))
for i,y in enumerate([258,311,367,425,481],1):save('guild_portrait_'+str(i),(855,y,63,58),source='original',circle=True)
save('guild_self_mark',(807,322,36,36),source='original',circle=True)
write(ROOT/'sprite-manifest.json',{'schemaVersion':1,'sourceCanvas':[1932,814],'designCanvas':[2560,1080],'uniformScale':min(2560/1932,1080/814),'sprites':sprites,'nativeUnityParityVerified':False})
print(json.dumps({'sprites':len(sprites),'payload':str(OUT)}))
