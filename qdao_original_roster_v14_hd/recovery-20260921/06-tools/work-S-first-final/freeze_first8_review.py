from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
STAGE=Path(__file__).resolve().parent
OUT=STAGE/'candidate/06_thunder_caster_boy'
ROOT=STAGE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
old=ROOT/'qdao_original_roster_v13/candidate/06_thunder_caster_boy/walk/S'
legacy=read(STAGE/'legacy-byte-manifest.json')
assert {p.name:sha(p) for p in old.glob('*.png')}==legacy
sources=read(OUT/'processing/frame-sources.json')
notes={
1:'屏左腿前伸、屏右腿后收，前靴少量露底与旧01一致；头身短圆，发梢、衣摆、法杖细饰和靴边在深浅底均清洁。',
2:'与01的连续过渡保持，后脚稍抬，手持物未换手；头脸、手与躯干比例稳定，深浅底无可见洋红边或白边。',
3:'v1确有头脸/手/符牌同步偏小，不能仅归为屈膝。v2重绘修复体型后屏左靴底稍多；v3只纠正靴尖向下，保留已修体型与旧03的屏左支持、屏右后摆关系。与04并排不再明显跳体型；深浅底边缘清洁。',
4:'屏右腿前摆且鞋底朝向观察者，屏左腿支持，符合旧04；与修正后03头脸、手及符牌相近，较宽衣摆属于对应相位，边缘完整。',
5:'屏右膝提起、靴子收在膝下，屏左腿支持，保持旧05高抬腿关系；无肢体粘连，衣摆和细发在深浅底无明显污染。',
6:'屏右腿从提膝进入向前伸展，靴底较05更可见，符合旧06；轻微高度差由姿势和发束起伏构成，没有同03 v1那样的整体缩小，边缘清洁。',
7:'屏右前摆腿降低，屏左靴支持，保持旧07；双腿连接正确，头身与相邻帧相容，发饰、法杖和鞋底轮廓在深浅底无明显色边。',
8:'屏右腿进一步向前落下、屏左腿后收，旧08的行走关系保持；两手道具、脸型与衣饰统一，深浅底未见白黑晕边或旧洋红污染。'}
frames=[]
for n in range(1,9):
    key=f'walk/S/{n:02d}.png';p=OUT/key;src=sources[key];im=Image.open(p)
    assert im.size==(1024,1024) and im.mode=='RGBA'
    assert sha(p)==src['output_sha256']
    assert src['common_scale']==.88 and src['anchor_after_px']==[512.,942]
    assert src['chroma_profile']=='native-alpha' and src['cleanup']['changed_pixels']==0
    assert src['whole_cell_scale']<1
    raw=OUT/src['source']['path'];assert sha(raw)==src['source']['sha256']
    assert Image.open(raw).size==(1254,1254)
    bbox=im.getchannel('A').point(lambda v:255 if v>32 else 0).getbbox()
    frames.append({'frame':n,'file':key,'sha256':sha(p),'source':src['source'],'old512_sha256':legacy[f'{n:02d}.png'],
      'status':'passed','visually_inspected':['same_canvas_contact','old512_pose_contact','1024_dark_background','1024_light_background'],
      'visible_alpha_bbox_gt32':list(bbox),'visible_height_px':bbox[3]-bbox[1],
      'pose_proportion_alpha_assessment':notes[n]})
review={'schema':'qdao-06-S-first8-independent-visual-review-v1','reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
 'reviewer':'review_s_first8','scope':'06_thunder_caster_boy S01-S08 staging only','status':'passed','frozen_for_parent_assembly':True,
 'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际型号或质量。',
 'new_builtin_calls_by_this_reviewer':2,'paid_api_calls':0,'accepted_replacement_batch':'S03-edge-final-v3',
 'superseded_candidates':[{'batch':'S03-edge-final-v1','reason':'可见整体体型偏小，03到04变化不是纯姿态差异。'},
                           {'batch':'S03-edge-final-v2','reason':'体型修正通过，支持靴仍略上翘；由v3针对靴尖修正。'}],
 'preserved_legacy_s_pngs_byte_for_byte':len(legacy),
 'processing':'All native1254 sources use fixed whole-cell scale 0.7185964912280702 (common_scale0.88), then integer anchor translation to foot942; no per-bbox scale, no RGB/alpha recoloring, no numerical upscale.',
 'visual_summary':'S03 v3修复后，八帧保留对应旧相位、短圆Q版头身及两手道具身份；同画布对照没有明显整体缩放跳变，深浅底无可见旧色边。髪丝、衣摆和装饰有逐帧手绘差别，不声称像素级相同。',
 'limitations':['This is file/visual staging review, not engine playback/E2E.','S08-to-S09, S16-to-S01 and all-direction review belong to parent assembly.','No final package, shared state, other direction or other character was modified.'],
 'contact_sheet':'review/S01-08-review-contact.png','old_pose_contact':'review/S01-08-old-pose-contact.png','frames':frames}
p=OUT/'review/first8-visual-review.json';p.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'review':str(p),'sha256':sha(p),'heights':[f['visible_height_px'] for f in frames],'S03_sha256':frames[2]['sha256'],'legacy_verified':len(legacy)},ensure_ascii=False))
