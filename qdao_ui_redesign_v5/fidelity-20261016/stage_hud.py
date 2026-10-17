from pathlib import Path
import json,hashlib,shutil,datetime
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=ROOT/'hud-client'
files=[];guards=[]
for name in ['BattleUiStyle.cs','BattleUiWidgets.cs']:
 p=CLIENT/'Assets/Scripts/UI/Ugui/Battle'/name
 s=p.read_text(encoding='utf-8-sig')
 if name=='BattleUiStyle.cs':
  for a,b in [('HudEntryWidth  = 330f','HudEntryWidth  = 336f'),('HudEntryHeight = 80f','HudEntryHeight = 81.6f'),('HudEntryGap    = 24f','HudEntryGap    = 22.4f'),('HudEntryFontSize = 32f','HudEntryFontSize = 36f'),('70px','64px'),('HudEntryWidth - 70f','HudEntryWidth - 64f')]:
   if a not in s:raise RuntimeError('HUD source changed: '+a)
   s=s.replace(a,b,1)
 else:
  old='''            ConfigureButtonVisual(widget.Button, widget.Plate);
            widget.Label = QdaoUguiFactory.CreateText($"{name}Text", widget.Plate.transform,
                32f, 0f, width - 64f, height, text, fontSize,
                QdaoRefreshArt.Ivory, TextAlignmentOptions.Center);
            widget.Label.fontStyle = fontStyle;'''
  new='''            // Approved v10 HUD skin is independent of the older RefreshV8 panel family.
            var approvedSkin = Resources.Load<Sprite>("UI/Ugui/CoreFidelity20261016/hud_button");
            if (approvedSkin != null)
            {
                widget.Plate.sprite = approvedSkin;
                widget.Plate.type = Image.Type.Simple;
                widget.Plate.preserveAspect = true;
            }
            ConfigureButtonVisual(widget.Button, widget.Plate);
            widget.Label = QdaoUguiFactory.CreateText($"{name}Text", widget.Plate.transform,
                32f, 0f, width - 64f, height, text, fontSize,
                QdaoRefreshArt.Ivory, TextAlignmentOptions.Center);
            QdaoUguiTypography.ApplyButton(widget.Label);
            widget.Label.fontStyle = fontStyle;'''
  if old not in s:raise RuntimeError('HUD button method source changed')
  s=s.replace(old,new,1)
 dest=out/p.relative_to(CLIENT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(s,encoding='utf-8')
 shutil.copyfile(p.with_name(p.name+'.meta'),dest.with_name(dest.name+'.meta'))
 guards.append({'target':p.relative_to(CLIENT).as_posix(),'sha256Before':sha(p)})
source=ROOT.parent/'components/png/primary_button_normal.png'
dest=out/'Assets/Resources/UI/Ugui/CoreFidelity20261016/hud_button.png'
dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
guid=hashlib.sha256(b'core-fidelity-20261016/hud_button').hexdigest()[:32]
meta='''fileFormatVersion: 2
guid: GUID
TextureImporter:
  serializedVersion: 13
  internalIDToNameTable: []
  externalObjects: {}
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
  spritePivot: {x: 0.5, y: 0.5}
  spriteBorder: {x: 0, y: 0, z: 0, w: 0}
  alphaIsTransparency: 1
  spriteSheet:
    serializedVersion: 2
    sprites: []
    spriteID: GUID
    internalID: 0
    outline: []
    physicsShape: []
    bones: []
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {}
'''.replace('GUID',guid)
dest.with_name(dest.name+'.meta').write_text(meta,encoding='utf-8')
record={'file':'hud_button.png','sha256':sha(dest),'derivedFrom':[{'path':str(source),'sha256':sha(source),'generationRecord':str(ROOT.parents[1]/'qdao_ui_style_recut_v10/source-map.common.json')}],'operation':'Byte-identical copy of approved v10 HUD button; display is uniform 336x81.6 as authored HUD contract','newAiGeneration':False}
dest.with_name(dest.name+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in out.rglob('*'):
 if p.is_file() and p.suffix in ['.cs','.meta','.png']:files.append({'source':p.relative_to(ROOT).as_posix(),'target':p.relative_to(out).as_posix(),'sha256':sha(p)})
result={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'destinationRoot':str(CLIENT),'files':files,'guards':guards,'scope':'HUD-only phase, independent of login/server/role payload','contract':'qdao_ui_redesign_v5/hud/placement.json','originalThreePositions':[[2160,176,336,81.6],[2160,280,336,81.6],[2160,384,336,81.6]],'businessCallbacksUnchanged':True,'TeamFollowAvoidance':'TeamFollow.ToggleX derives from TeamUiRoot.EntryX + HudEntryWidth + 16; shared width +6 moves toggle by the same +6 and preserves its 16px gap, with no overlap. Right column x stays 2160.','nativeValidationPending':True}
(ROOT/'hud-install-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(files),'sourceGuards':guards,'rightColumnX':2160},ensure_ascii=False))
