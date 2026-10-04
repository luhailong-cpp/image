import json, sys, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
GROUP=ROOT/'provenance/run-south'
CONFIG=Path('D:/work/image/config/image-generation.json')
STYLE='D:/work/image/designs/jubaozhai-ui/02-characters.png'
IDLE='D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/09-delivery-preview/final/runtime/idle'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(d,f):
 assert d in ['S','SE','SW','W'] and 1<=f<=16
 lead='anatomical LEFT' if f<=8 else 'anatomical RIGHT'
 other='anatomical RIGHT' if f<=8 else 'anatomical LEFT'
 phase=(f-1)%8
 stages=[
  f'{lead} boot touches down ahead, knee slightly flexed absorbing first contact; {other} leg trails back with heel lifted and bent knee. Torso y neutral.',
  f'{lead} leg supports full weight, knee deeply but naturally compresses, heel planted; {other} foot leaves ground and folds behind. Torso 12 pixels lower.',
  f'{lead} stance boot below hip, knee starts straightening; {other} folded knee passes under pelvis moving forward; distinct visible two ankles. Torso 5 pixels lower.',
  f'{lead} leg extends behind the hip pushing off from toes, heel rises; {other} knee drives forward with bent shin; body starts rising.',
  f'First brief flight: BOTH boots clear the imaginary floor by at least 20 pixels, {lead} leg trails with knee folding, {other} knee forward; torso 12 pixels higher.',
  f'Flight apex: BOTH boots clear imaginary floor by 30 pixels, {other} shin starts unfolding forward, {lead} knee folded back. Torso 18 pixels higher.',
  f'Descending flight: {other} foot reaches forward almost ready to touch ground, {lead} heel folds up behind. BOTH boots still off floor by 8 pixels; torso 8 pixels higher.',
  f'Pre-contact: {other} heel just 2 pixels above virtual ground, knee slightly bent forward, {lead} foot folded back. Torso returns near neutral for next foot contact.'
 ]
 armphase=[-1,-0.7,-0.2,0.4,0.8,1,0.6,0.1][phase]
 if f>8: armphase=-armphase
 arms=('Left bow arm swings BACK from shoulder, elbow bends and hand comes near left hip; RIGHT empty arm swings FORWARD with elbow bent and hand in front of waist.' if armphase<-.3 else 'Left bow arm swings FORWARD from shoulder, elbow naturally flexed, bow grip ahead of left hip; RIGHT empty arm swings BACK beside right hip.' if armphase>.3 else 'Both arms cross the middle of their running arcs: LEFT bow hand beside left hip, RIGHT EMPTY hand near right waist; elbows bent naturally, no static idle pose.')
 angle={'S':'Straight front facing viewer, running toward camera/screen bottom. Anatomical LEFT is SCREEN RIGHT (bow); anatomical RIGHT is SCREEN LEFT (empty hand and quiver). Keep both eyes symmetrical and frontal torso. Use real depth foreshortening, not side view.', 'SE':'Front three-quarter facing screen bottom-right, same camera yaw as reference. Anatomical LEFT holds bow on screen right, visible near empty RIGHT arm swings on screen left; quiver remains over right shoulder visible screen left.', 'SW':'Front three-quarter facing screen bottom-left, same camera yaw as reference; preserve anatomical hand sides from reference; independently draw, never mirror.', 'W':'Side view facing screen left, same camera yaw as reference. LEFT far arm holds bow, RIGHT near empty arm swings.'}[d]
 prompt=f'''Use case: stylized-concept. Produce ONE native at least 1024x1024 transparent RGBA animation frame, not a sheet. 09 bamboo archer girl RUN {d} frame {f:02d}/16 at 30ms per frame.
Image 1 is exact identity, camera, proportions, fixed canvas placement and original palette reference. Image 2 is approved main drawing style. Repaint a genuinely new articulated running pose, same brown high ponytail and jade bamboo-leaf/gold crown, green eyes, ivory/jade/gold short robe, white shorts/boots, yin-yang buckle. Warm clean softly painted Daoist chibi, identical head size/materials, no orange hair drift.
CAMERA: {angle}
POSE PHASE: {stages[phase]}
COORDINATED ARMS: {arms} Shoulder and elbow angles MUST actually change with this running phase. Arms counter-swing opposite their corresponding legs. No duplicated static carry pose.
ANATOMY: Exactly two legs, two knees, two feet, two arms. Complete long bamboo bow is always held in anatomical LEFT hand with fingers closing around its grip; anatomical RIGHT hand stays EMPTY. Entire long upper/lower bow tips and single slack straight string visible inside canvas, no arrow nocked. Right-shoulder quiver remains fixed. Bow swings naturally as rigid whole with left hand, modest angle to avoid cropping, never changes hand/length. Legs alternate support and short flight, feet stay under realistic hip lanes (not extreme split or marching high knees). Skirt may reveal knees, must not merge boots.
FRAME LOCK: fixed square full canvas, same camera, same chibi body and head scale as image1. Body root x512, virtual floor y940 on 1024 basis, only specified natural small vertical bob; preserve full body and bow within margin. Render true foreshortening for forward/back depth movement and explicit support/flight; DO NOT translate every lowest foot to ground, zoom to bbox, crop, mirror, warp, or interpolate. No floor, shadow, text, particles, checkerboard, effects, duplicate character. Actual alpha transparency only.'''
 if d=='SE':
  advancing=lead if phase<2 else other
  retracting=other if phase<2 else lead
  prompt+=f'\nCRITICAL SE LEG DEPTH: anatomical RIGHT leg is the NEAR leg, its thigh originates below screen-left half of shorts; anatomical LEFT leg is FAR, its thigh emerges under screen-right shorts. This frame {advancing} is advancing toward screen bottom-right, and {retracting} is retracting toward screen upper-left. Respect this actual joint chain; articulate hip-knee-ankle, do not repeat the same leading leg in every frame. '
  if phase in [4,5]:prompt+='Both knees are visibly flexed for suspended running flight; neither leg is a straight vertical weight-bearing pole. Strong air gap under BOTH boots, especially the leading boot.'
 refs=[f'{IDLE}/{d}.png',STYLE]
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 path=GROUP/f'{d}-{f:02d}-{stamp}.request.json'
 args={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':True}
 req={'startedAt':datetime.now(timezone.utc).isoformat(),'slot':f'run-{d}-{f:02d}','action':'run','direction':d,'frame':f,'configSnapshot':json.loads(CONFIG.read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None},'referenceMetadata':[{'path':p,'sha256':sha(p),'purpose':'identity, camera, scale and original palette' if i==0 else 'approved main drawing style'} for i,p in enumerate(refs)],'args':args}
 write(path,req)
 print(json.dumps({'request':str(path),'args':args},ensure_ascii=False))
def register(reqpath,receiptpath):
 req=json.loads(Path(reqpath).read_text(encoding='utf-8')); receipt=json.loads(Path(receiptpath).read_text(encoding='utf-8'))
 d,f=req['direction'],req['frame'];native=Path(receipt['nativeSourcePath']);im=Image.open(native)
 assert im.mode=='RGBA' and min(im.size)>=1024,(im.mode,im.size)
 ns=list(im.size);nativehash=sha(native)
 pix=np.array(im); pix[pix[:,:,3]<=2]=0
 outimg=Image.fromarray(pix,'RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
 pix=np.array(outimg);pix[pix[:,:,3]<=2]=0
 out=ROOT/f'runtime/run/{d}/{f:02d}.png';out.parent.mkdir(parents=True,exist_ok=True)
 recordpath=out.with_suffix('.png.generation.json')
 if recordpath.exists():
  prior=json.loads(recordpath.read_text(encoding='utf-8'))
  write(GROUP/f'history/{d}-{f:02d}-{prior["sha256"][:16]}.generation.json',prior)
 Image.fromarray(pix,'RGBA').save(out)
 record={'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'generatedAt':receipt['completedAt'],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':dict(req['submittedParameters'],transparent_background=True,referenced_image_paths=req['args']['referenced_image_paths']),'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed builtin; tool does not expose model/quality parameters or disclose returned model/quality.','evidence':{'request':str(Path(reqpath).relative_to(ROOT)).replace('\\','/'),'receipt':str(Path(receiptpath).relative_to(ROOT)).replace('\\','/')},'prompt':req['args']['prompt'],'references':req['referenceMetadata'],'width':1024,'height':1024,'nativeSize':ns,'nativeCellSize':ns,'format':'PNG','derivedFrom':{'path':str(native),'sha256':nativehash,'nativeSize':ns},'operation':'Clear only alpha<=2 pixels before and after uniform whole-canvas Lanczos resize to 1024; no bbox scaling, translation, floor snapping, mirroring, deformation or interpolation.'}
 write(recordpath,record)
 selection=ROOT/'selection/run-south.json';sel=json.loads(selection.read_text(encoding='utf-8')) if selection.exists() else {'frames':[]}
 sel['frames']=[x for x in sel['frames'] if not(x['direction']==d and x['frame']==f)]
 sel['frames'].append({'action':'run','direction':d,'frame':f,'file':record['file'],'sha256':record['sha256'],'generationRecord':recordpath.relative_to(ROOT).as_posix(),'generationRecordSha256':sha(recordpath),'sourceNativeSize':ns})
 write(selection,sel)
 print(json.dumps({'file':str(out),'sha256':record['sha256'],'nativeSize':ns}))
if sys.argv[1]=='prepare':prepare(sys.argv[2],int(sys.argv[3]))
elif sys.argv[1]=='register':register(sys.argv[2],sys.argv[3])
