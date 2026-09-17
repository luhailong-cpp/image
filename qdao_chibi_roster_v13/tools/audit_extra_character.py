from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json, datetime

out = Path('E:/work/image/qdao_chibi_roster_v13')
source = Path('E:/work/image/character_move_8dir')
client = Path('E:/work/mmorpg-client')
live = client / 'Assets/Resources/World/Characters/QdaoHeadbandBoy'
review = out / 'extra-character-baseline-review'
review.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest_path = source / 'manifest.json'
m = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
directions = [('S','south'),('E','east'),('N','north'),('W','west'),('NE','northeast'),('SW','southwest'),('NW','northwest'),('SE','southeast')]
record = {'audit_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'read-only asset audit; deterministic contact-sheet layout only; no source or game resource changes','source_manifest':{'path':str(manifest_path),'sha256':sha(manifest_path)},'source_4frame':[],'runtime_8frame':[],'runtime_idle':[],'code_snapshot':[]}
for short,long in directions:
    for frame in m['directions'][long]['frames']:
        p=source/frame['file']
        with Image.open(p) as im: size=list(im.size); mode=im.mode
        actual=sha(p)
        record['source_4frame'].append({'path':str(p),'sha256':actual,'manifest_sha256':frame['sha256'],'matches_manifest':actual==frame['sha256'],'size':size,'mode':mode,'direction':short})
    p=live / f'walk_{short}.png'
    with Image.open(p) as raw:
        im=raw.convert('RGBA')
        frames=[im.crop((i*512,0,(i+1)*512,512)) for i in range(8)]
        pixel_shas=[hashlib.sha256(f.tobytes()).hexdigest() for f in frames]
        record['runtime_8frame'].append({'path':str(p),'sha256':sha(p),'size':list(im.size),'mode':raw.mode,'direction':short,'cell_rgba_sha256':pixel_shas,'unique_pixel_cells':len(set(pixel_shas))})
    p=live / f'idle_{short}.png'
    with Image.open(p) as im: size=list(im.size); mode=im.mode
    record['runtime_idle'].append({'path':str(p),'sha256':sha(p),'size':size,'mode':mode,'direction':short})
for rel in ['Assets/Scripts/World/QdaoCharacterCatalog.cs','Assets/Scripts/World/QdaoBoySpriteAnimator.cs','Assets/Scripts/UI/Ugui/Battle/BattleArtCatalog.cs']:
    p=client/rel
    record['code_snapshot'].append({'path':str(p),'sha256':sha(p)})
identity=Path('E:/work/image/qdao_chibi_game_pack_v4/hero-transparent_1024.png')
record['identity_reference']={'path':str(identity),'sha256':sha(identity)}
lu=Path('E:/work/image/qdao_chibi_roster_v12/candidate-stable-body/24_lu_dongbin/manifest.json')
record['lu_v12_manifest']={'path':str(lu),'sha256':sha(lu),'matches_frozen':sha(lu)=='3dbc699023fd7fe6f45304fd91ecea2f088e107d4c727d375dc1b23c31e68c68'}
record['timing']={'legacy_frames':8,'reference_speed_units_s':9,'frame_pixel_height':512,'ppu':52,'cycle_distance_per_frame_height':0.5625,'cycle_world_distance':512/52*0.5625,'frames_per_world_unit':8/(512/52*0.5625),'fps_at_reference_speed':9*8/(512/52*0.5625),'cycle_ms_at_reference_speed':1000*(512/52*0.5625)/9,'preserved_cycle_16frame_ms_at_reference_speed':1000*(512/52*0.5625)/9/16,'art4frame_recommended_frame_ms':120,'art4frame_recommended_cycle_ms':480}

# Review-only full-cell resampling. No alpha-bbox resizing, warping, interpolation, or new poses.
font_path='C:/Windows/Fonts/arial.ttf'
font=ImageFont.truetype(font_path,18)
small=ImageFont.truetype(font_path,15)
big=ImageFont.truetype(font_path,26)
cell=144; x0=24; gap=12; panel_w=x0*2+9*(cell+gap)-gap
record['review_panels']=[]
for pair in range(4):
    board=Image.new('RGB',(panel_w,800),(27,39,38))
    draw=ImageDraw.Draw(board)
    draw.text((24,14),'HEADBAND BOY | baseline audit',(226,212,169),font=big)
    draw.text((24,51),'Top row: current game idle + 8 cells. Bottom row: user-specified 4-frame art + identity reference.',(211,219,211),font=small)
    draw.text((24,75),'Every full square canvas displays at 144 px. No body normalization. Review image only.',(161,182,172),font=small)
    for local in range(2):
        short,long=directions[pair*2+local]
        y=114+local*336
        draw.text((24,y),f'{short} / {long.upper()}    CURRENT GAME: 8 frames; cycle ~615 ms at 9 units/s',(237,233,212),font=font)
        with Image.open(live/f'walk_{short}.png') as im:
            cells=[im.convert('RGBA').crop((i*512,0,(i+1)*512,512)) for i in range(8)]
        with Image.open(live/f'idle_{short}.png') as im: cells.insert(0,im.convert('RGBA'))
        for i,im in enumerate(cells):
            x=x0+i*(cell+gap); yy=y+24
            draw.rectangle((x,yy,x+cell,yy+cell),fill=(54,65,61))
            im=im.resize((cell,cell),Image.Resampling.LANCZOS)
            board.paste(im,(x,yy),im)
            draw.text((x+4,yy+2),'idle' if i==0 else f'{i:02}',(235,215,161),font=small)
        yy=y+184
        for i in range(4):
            with Image.open(source/f'{long}_frame_{i+1:02}.png') as raw: im=raw.convert('RGBA').resize((cell,cell),Image.Resampling.LANCZOS)
            x=x0+i*(cell+gap)
            draw.rectangle((x,yy,x+cell,yy+cell),fill=(54,65,61));board.paste(im,(x,yy),im)
            draw.text((x+4,yy+2),f'4F {i+1:02}',(235,215,161),font=small)
        x=x0+4*(cell+gap)
        with Image.open(identity) as raw: im=raw.convert('RGBA').resize((cell,cell),Image.Resampling.LANCZOS)
        draw.rectangle((x,yy,x+cell,yy+cell),fill=(54,65,61));board.paste(im,(x,yy),im)
        draw.text((x+4,yy+2),'identity',(235,215,161),font=small)
        draw.text((x0+5*(cell+gap),yy+35),'4-frame art: 1254 x 1254 RGBA',(211,219,211),font=small)
        draw.text((x0+5*(cell+gap),yy+62),'Recommended cycle: 4 x 120 = 480 ms',(211,219,211),font=small)
        draw.text((x0+5*(cell+gap),yy+89),'Source README predates game integration.',(211,219,211),font=small)
    p=review/f'baseline-{directions[pair*2][0]}-{directions[pair*2+1][0]}.jpg'
    board.save(p,quality=92)
    record['review_panels'].append({'path':str(p),'sha256':sha(p),'size':list(board.size),'method':'full-square-cell crop and whole-canvas uniform resampling to 144x144 for layout; no pose creation'})
record['all_source_frame_shas_match_manifest']=all(x['matches_manifest'] for x in record['source_4frame'])
record['all_current_strips_have_8_pixel_unique_cells']=all(x['unique_pixel_cells']==8 for x in record['runtime_8frame'])
record_path=out/'extra-character-baseline-audit.json'
record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')

lines=['# 补充角色基线只读调查', '',f"调查时间：{record['audit_utc']}。此报告为素材与代码静态调查，不代表本次 V13 已制作、已接入或运行验收通过。",'',
'用户给出的路径 `E:/work/image/character/_move/_8dir` 实际对应 `E:/work/image/character_move_8dir`。该角色为金发带道童，短棕发、玉绿金边短背心、米白短袍裤、太极金葫芦，与年轻吕洞宾不同。', '',
'## 两个有效基线', '',
'| 项目 | 用户指定目录 | 游戏目前采用的道童 |','|---|---|---|',
'| 来源 | `E:/work/image/character_move_8dir` | `E:/work/mmorpg-client/Assets/Resources/World/Characters/QdaoHeadbandBoy` |',
'| 行走 | 每向4张独立PNG，8向共32张 | 每向8格条带，8向共64个格 |',
'| 尺寸 | 每张1254×1254 RGBA | 条带4096×512；每格512×512 |',
'| 站立 | 该目录没有独立idle | `idle_N/NE/E/SE/S/SW/W/NW.png`，8张512×512 |',
'| 肖像/身份参考 | `E:/work/image/qdao_chibi_game_pack_v4/hero-transparent_1024.png` | 正式世界目录没有 portrait；catalog也无该ID的肖像定义 |',
'| 原节奏 | 美术推荐120ms×4=480ms，未声明旧工程实际节奏 | 距离驱动；9世界单位/s时周期约615.384615ms |',
'| 升到16帧保留旧动作 | 旧4帧映射1/5/9/13，每向新增12张，共96张 | 从正式条带无损切64个旧格至奇数位，每向新增8张，共64张 |','',
'`character_move_8dir/README.md` 和 manifest 的“未接入”只描述2026-09-06该四帧包。后续客户端已接入同身份道童八帧，不能据旧说明认定游戏没有道童。', '',
'## 正式游戏绑定与时序', '',
'`Assets/Scripts/World/QdaoCharacterCatalog.cs`：`LegacyId = "QdaoHeadbandBoy"`，`DefaultId = "24_lu_dongbin"`。8个 Entries 仅含23–30号角色，道童不在 Entries；`Find("QdaoHeadbandBoy")` 返回null，动画器据此采用 legacy分支。道童不是吕洞宾的别名。', '',
'现有职业/性别映射：职业1男吕洞宾/女灯穗小使；职业2男韩湘子/女月兔机关师；职业3男墨鸢游侠/女何仙姑；职业4男狮鼓护卫/女桂香药婆；未知职业默认吕洞宾。新增道童版本必须保持该映射。', '',
'`QdaoBoySpriteAnimator.cs`：`ResourceFolder = "World/Characters/QdaoHeadbandBoy"`，`FramesPerDirection = 8`，`ReferenceRunSpeed = 9f`，`PixelsPerUnit = 52f`，`FramePixelHeight = 512f`，`CycleDistancePerFrameHeight = 0.5625f`。', '',
'由代码计算：`CycleWorldDistance = 512/52×0.5625 = 5.538461538`；`FramesPerWorldUnit = 8/CycleWorldDistance = 1.444444444`；`RunFramesPerSecond = 13`；现行周期 `8/13×1000 = 615.384615ms`。保持周期与速度升级到16帧时应为26 FPS，即约38.461538ms/帧。若强制30ms，则周期480ms，相同步态距离变成4.32世界单位，因此不是保持该角色原周期。', '',
'现有道童加载 `walk_<DIR>` 条带，并加载独立 `idle_<DIR>`；idle pivot=(0.5,0.08)，PPU=52。legacy停步先推进到每向既定收势位置再显示idle，其表为 `[2,1,1,6,2,5,2,5]`（零基，N/NE/E/SE/S/SW/W/NW）。V12直接停idle，不能不加区分地变更legacy行为。', '',
'`Assets/Scripts/UI/Ugui/Battle/BattleArtCatalog.cs` 的 `PlayerWalkRoot` 与 `DefaultCharacterId` 仍为 `QdaoHeadbandBoy`，战斗也引用该历史身份。', '',
'## 来源链与文件核验', '',
f"四帧manifest真实SHA-256：`{record['source_manifest']['sha256']}`。32个源PNG全部与manifest记录SHA一致：`{record['all_source_frame_shas_match_manifest']}`。", '',
'八帧正式游戏的每个条带、每张idle、64格RGBA内容哈希，以及全部32张四帧源图SHA，均记录在 [extra-character-baseline-audit.json](extra-character-baseline-audit.json)。八向均有8个像素唯一格；哈希唯一不等于视觉动作已经通过本轮验收。', '',
'四帧逐向原生生成标识及哈希：`character_move_8dir/records/<south/north/east/west/southeast/southwest/northeast/northwest>.json`；逐字提示词：`prompts/<direction>.prompt.txt`；汇总工具输出路径：`generation-records.json`。记录说明原生2×2母表1254²，单格约627²，1254成品经过透明处理、重采样及对齐；未保留母表于正式目录。', '',
'当前八帧的N/S修复有直接来源：`E:/work/mmorpg-client/Docs/ArtEvidence/qdao-run-ns-20260909/raw-N.png`、`raw-S.png`；配套 `pipeline-meta-N.json`、`pipeline-meta-S.json`、`run-scale-profile.json`、`runtime-qc.json`。其余六向沿用当时原有正式条带，本次未找到对应逐字生成调用，不冒称已重建其上游来源。', '',
'当前独立idle直接来源：`E:/work/mmorpg-client/Docs/ArtEvidence/qdao-idle-20260909/raw-sheet.png`；配套 `prompt-used.txt`、`raw-sheet-clean.png`、`pipeline-meta.json`、`runtime-qc.json`。2026-09-09素材QA位于 `Docs/tianyong-idle-assets-2026-09.md` 与 `Docs/tianyong-run-ns-2026-09.md`，当时运行验证总报告 `Docs/tianyong-city-move-2026-09.md`。这些是历史证据，不能当作本次V13测试。', '',
f"吕洞宾V12冻结manifest核验通过：`{record['lu_v12_manifest']['sha256']}` 与任务及 completion-20260916.json 相同。调查开始时，image内无既有qdao_chibi_roster_v13目录，正式客户端Characters内仅QdaoHeadbandBoy/QdaoRosterV11/QdaoRosterV12，未发现已发布V13。随后当前主任务建立V13/tools，为本轮在途工作。", '',
'## 对比联系图与处理边界', '',
'联系图上排为现用idle及8个完整512格，下排为用户指定4帧及身份参考。各完整正方形画布统一显示为144px，没有按人物bbox重缩放，不做新动作、不修改源图和正式游戏资源。', '']
for p in record['review_panels']:
    rel=Path(p['path']).relative_to(out).as_posix();lines.append(f'- [{Path(rel).name}]({rel})')
lines+=['','## 后续决策','',
'推荐以正式8帧道童为基线补64个过渡姿态并保持原有约615ms周期，保留其独立idle及既有身份。另一个选项是严格以用户指定4帧重建16帧（新增96张），采用该包推荐的480ms；两者的动作基础与周期均不同。主代理已向用户异步询问基线选择。本调查不自行批准其中任一选项，未进行依赖选择的素材生成或游戏代码修改。','']
(out/'extra-character-baseline-audit.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'audit':str(out/'extra-character-baseline-audit.md'),'source_sha_match':record['all_source_frame_shas_match_manifest'],'unique_8frame_strips':record['all_current_strips_have_8_pixel_unique_cells'],'review_panels':[p['path'] for p in record['review_panels']],'timing':record['timing']},indent=2))
