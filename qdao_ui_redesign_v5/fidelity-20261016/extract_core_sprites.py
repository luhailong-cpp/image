from pathlib import Path
from PIL import Image
import hashlib,json,datetime,re,shutil
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'client/Assets/Resources/UI/Ugui/CoreFidelity20261016'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
config=json.loads((ROOT.parents[1]/'config/image-generation.json').read_text(encoding='utf-8-sig'))
sources=[('login-clean.png','clean-login.txt',ROOT.parent/'01_login_2560x1080.png','exec-9d761e34-e7d5-4931-8c82-2c32a7944fee.png'),('server-clean.png','clean-server.txt',ROOT.parent/'02_server_select_2560x1080.png','exec-50d0a534-91fc-4b3b-9019-0f358368bb40.png'),('role-controls-clean.png','clean-role-controls.txt',ROOT.parent/'03_character_select_2560x1080.png','exec-a0c5a1e4-31e8-4b7a-a750-dc349cde710c.png'),('role-empty-shell.png','empty-role-shell.txt',ROOT/'art/role-controls-clean.png','exec-bf9c90ee-11e5-4d42-96a5-15a908c4d1de.png')]
for name,prompt,ref,cache in sources:
 p=ROOT/'art'/name;im=Image.open(p)
 stamp=re.search(rb'c2pa\.created.{0,32}?(20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z)',p.read_bytes(),re.S)
 write(p.with_name(p.name+'.generation.json'),{'file':name,'sha256':sha(p),'generatedAt':stamp.group(1).decode() if stamp else now,'generatedAtBasis':'embedded c2pa.created.when declaration, signature not verified' if stamp else 'recorded during current task','width':im.width,'height':im.height,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'prompt':str(ROOT/'prompts'/prompt),'referenced_image_paths':[str(ref)],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具无model/quality选择器，没有披露可核实的具体版本与质量。','references':[{'path':str(ref),'sha256':sha(ref),'role':'edit-target and exact approved style'}],'evidence':{'outputPath':'C:/Users/luyua/.codex/generated_images/01a147f6-78cd-7e50-8857-3622cb8822f5/'+cache,'returnedKeys':['image_url','output_hint']},'review':{'acceptedForRuntime':True,'nativeUnityParityVerified':False}})
images={name:Image.open(ROOT/'art'/name).convert('RGBA') for name,_,_,_ in sources}
items=[]
def meta(path,key,border):
 guid=hashlib.sha256(('core-fidelity-20261016/'+key).encode()).hexdigest()[:32]
 path.with_name(path.name+'.meta').write_text(f'''fileFormatVersion: 2
guid: {guid}
TextureImporter:
  serializedVersion: 13
  internalIDToNameTable: []
  externalObjects: {{}}
  mipmaps:
    enableMipMap: 0
    sRGBTexture: 1
  textureType: 8
  textureShape: 1
  textureSettings:
    filterMode: 1
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  maxTextureSize: 4096
  textureCompression: 0
  spriteMode: 1
  spriteMeshType: 0
  spritePixelsToUnits: 100
  spritePivot: {{x: 0.5, y: 0.5}}
  spriteBorder: {{x: {border[0]}, y: {border[1]}, z: {border[2]}, w: {border[3]}}}
  alphaIsTransparency: 1
  spriteSheet:
    serializedVersion: 2
    sprites: []
    spriteID: {guid}
    internalID: 0
    outline: []
    physicsShape: []
    bones: []
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
''',encoding='utf-8')
def crop(key,source,rect=None,border=(0,0,0,0)):
 im=images[source];rect=rect or (0,0,im.width,im.height);x,y,w,h=rect
 p=OUT/(key+'.png');im.crop((x,y,x+w,y+h)).save(p);meta(p,key,border)
 origin=ROOT/'art'/source
 write(p.with_name(p.name+'.generation.json'),{'file':p.name,'sha256':sha(p),'derivedAt':now,'width':w,'height':h,'operation':'Native pixel crop, no resampling; source displayed with one uniform 2560/1932 scale','derivedFrom':[{'path':str(origin),'sha256':sha(origin),'generationRecord':str(origin)+'.generation.json'}],'actualModel':None,'actualQuality':None,'modelBasis':'Inherited from exact source record; model/quality are host-managed unknown'})
 items.append({'key':key,'assetPath':p.relative_to(ROOT/'client').as_posix(),'sha256':sha(p),'source':str(origin),'sourceRectXYWH':list(rect),'borderLeftBottomRightTop':list(border),'width':w,'height':h})
crop('login_shell','login-clean.png')
crop('login_server_bar','login-clean.png',(173,410,615,79),(23,18,23,18))
crop('login_choose','login-clean.png',(610,417,166,62),(17,13,17,13))
crop('login_enter','login-clean.png',(205,510,553,126),(35,25,35,25))
crop('server_shell','server-clean.png')
crop('server_card_selected','server-clean.png',(576,265,487,80),(19,12,19,12))
crop('server_card_normal','server-clean.png',(1112,265,485,81),(19,12,19,12))
crop('server_card_disabled','server-clean.png',(1111,464,489,75),(25,15,25,15))
crop('server_category_normal','server-clean.png',(278,339,255,54),(17,12,17,12))
crop('server_category_selected','server-clean.png',(278,495,255,54),(17,12,17,12))
crop('server_search','server-clean.png',(278,263,255,50),(17,12,17,12))
crop('server_back','server-clean.png',(1227,679,148,52),(17,13,17,13))
crop('server_enter','server-clean.png',(1397,678,236,55),(21,13,21,13))
crop('server_summary','server-clean.png',(278,676,910,57),(17,13,17,13))
crop('role_shell','role-empty-shell.png')
crop('role_card_selected','role-controls-clean.png',(130,163,401,177),(20,18,20,18))
crop('role_card_normal','role-controls-clean.png',(130,352,401,172),(20,18,20,18))
crop('role_back','role-controls-clean.png',(188,719,280,79),(26,19,26,19))
crop('role_enter','role-controls-clean.png',(1410,641,434,123),(38,22,38,22))
p=Path('E:/work/mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV14/04_mountain_guardian_boy/portrait.png')
portrait=OUT/'portraits/04_mountain_guardian_boy.png';portrait.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,portrait);meta(portrait,'portraits/04_mountain_guardian_boy',(0,0,0,0))
write(portrait.with_name(portrait.name+'.generation.json'),{'file':portrait.name,'sha256':sha(portrait),'operation':'Byte-identical UI Sprite copy of current same-identity standalone portrait, independent of full walking-animation completeness','derivedFrom':[{'path':str(p),'sha256':sha(p),'generationRecord':str(p.parent/'manifest.json')}],'newAiGeneration':False,'identity':'04_mountain_guardian_boy','identityFallback':False})
items.append({'key':'portraits/04_mountain_guardian_boy','assetPath':portrait.relative_to(ROOT/'client').as_posix(),'sha256':sha(portrait),'source':str(p),'width':1024,'height':1024,'borderLeftBottomRightTop':[0,0,0,0]})
write(ROOT/'sprite-manifest.json',{'sourceCanvas':[1932,814],'designCanvas':[2560,1080],'sprites':items,'nativeUnityParityVerified':False})
print(json.dumps({'sprites':len(items)}))
