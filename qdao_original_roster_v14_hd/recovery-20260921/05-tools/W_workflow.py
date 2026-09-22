"""Prepare exact W-only requests and archive genuine builtin results. No generation API."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess, sys
HERE=Path(__file__).resolve().parent; GEN=HERE.parent/'05-generation'; ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PHASES={
1:'First contact: the NEAR leg (camera-facing, visibly in front) reaches a SMALL distance forward toward SCREEN LEFT, its heel just touching the invisible ground. The FAR leg trails slightly toward SCREEN RIGHT, toe touching with heel raised. Both boots visible and separate. Short natural stride, not a split.',
2:'Just after near-leg first contact: NEAR boot is planted slightly LEFT of the hips, its knee gently yielding. FAR rear boot stays behind to RIGHT with only toe just touching, heel a little higher. Small change from frame01; keep near leg as support.',
3:'Early recoil: NEAR boot remains flat supporting just LEFT of hips, knee mildly bent. FAR foot has just left its trailing RIGHT toe, lifting a little behind, not yet passing the support foot. Preserve the near support leg.',
4:'Approaching first passing: NEAR boot supports under hips, knee straightening. FAR foot swings forward from the RIGHT rear toward the support ankle, its heel raised and knee bent; far foot remains slightly behind support foot.',
5:'First passing: NEAR boot alone is planted directly under the hip supporting the body. FAR knee bends forward toward SCREEN LEFT; FAR boot is visibly airborne just forward of the support ankle, toe angled slightly downward. Small walk passing pose, no kick.',
6:'After first passing: NEAR boot remains planted slightly RIGHT of the hips, beginning heel lift. FAR bent leg swings gently ahead to LEFT, farther forward than frame05, its boot still lifted, knee lowering slightly.',
7:'Preparing opposite contact: NEAR boot supports behind to SCREEN RIGHT with heel lifted, toe planted. FAR leg extends forward to LEFT, its heel lowering but still just above ground. Modest short stride.',
8:'Immediately before opposite contact: FAR leg extends slightly forward LEFT, boot heel a tiny gap above ground. NEAR leg trails RIGHT with toe planted and heel high. Almost frame09 but far foot not yet touching.',
9:'Opposite contact: the FAR leg (partly behind the camera-facing leg) reaches a SMALL distance forward toward SCREEN LEFT, its heel just touching the invisible ground. The NEAR leg trails slightly toward SCREEN RIGHT with toe touching and heel raised. Exactly opposite support transition to frame01, same small stride and anatomical size.',
10:'Just after far-leg contact: FAR boot planted slightly LEFT of hips, knee gently yielding. NEAR rear boot trails RIGHT, only toe just touching, heel a little higher. Small change from frame09; far leg supports.',
11:'Early second recoil: FAR boot flat supporting just LEFT of hips. NEAR foot has just left its trailing RIGHT toe, lifting a little behind, not yet passing support foot. Keep far support leg.',
12:'Approaching second passing: FAR boot supports under hip, knee straightening. NEAR foot swings forward from RIGHT rear toward support ankle, heel raised and knee bent, remaining slightly behind support foot.',
13:'Second passing: FAR boot alone is planted directly under the hip supporting the body. NEAR knee bends forward toward SCREEN LEFT; NEAR boot is visibly airborne just forward of support ankle, toe angled slightly downward. Opposite leg assignment to frame05, small passing pose.',
14:'After second passing: FAR boot planted slightly RIGHT of hips, beginning heel lift. NEAR bent leg swings gently ahead LEFT, farther forward than frame13, boot still lifted and knee lowering slightly.',
15:'Preparing loop contact: FAR boot supports behind SCREEN RIGHT, heel raised and toe planted. NEAR leg extends forward LEFT, heel lowering but still above ground. Transition toward frame01 with no body size or crown height jump.',
16:'Immediately before loop contact: NEAR leg extends slightly forward LEFT, heel only a tiny gap above ground. FAR leg trails RIGHT with toe planted and heel high. Almost frame01 but near heel not quite touching; tiny change into frame01, no height or camera change.'}
def prepare(a):
 archive=GEN/f'W{a.frame:02d}-single-v{a.version}';archive.mkdir(exist_ok=True)
 assert not (archive/'request.json').exists(),'Use a fresh attempt version'
 refs=[ROOT/'qdao_original_roster_v13/candidate/05_celestial_musician_girl/idle/W.png',GEN/'references/portrait-inspection.png',ROOT/'designs/jubaozhai-ui/02-characters.png']
 roles='Image1 fixes the WEST true left-facing side camera, robe/hair/instrument placement and body proportions; it is an old 512 reference, NOT a canvas occupancy guide. Image2 fixes exact original character identity and costume detail only, NOT front camera. Image3 is the confirmed PRIMARY STYLE reference: match the clean bright rounded finely hand-painted finish, do not copy its UI or characters.'
 phase_refs=[]
 for n in a.phase_refs:
  version={5:3,9:2,10:2}.get(n,1)
  candidate=GEN/f'W{n:02d}-single-v{version}/raw.png'
  assert candidate.is_file(),candidate
  refs.append(candidate);phase_refs.append(n)
  roles+=f' Image{len(refs)} is W{n:02d}, a phase and anatomical-size reference; draw the new requested phase instead of duplicating it.'
 if a.phase_first:
  assert phase_refs,'A primary phase is required'
  refs=[refs[3],refs[0],refs[1],refs[2],*refs[4:]]
  roles=f'Image1 is the selected W{phase_refs[0]:02d} phase: keep its exact side-camera, anatomy, scale, costume, and existing foreground/background leg identity while newly drawing the requested gait advance. Image2 is old W idle, direction and identity only, not canvas margins. Image3 is the original portrait, costume detail only, not front camera. Image4 is the confirmed PRIMARY STYLE reference, matching its clean bright rounded hand-painted finish but no UI or other character. '
  if len(phase_refs)>1:roles+=f'Image5 is W{phase_refs[1]:02d}, a second phase and stable body-size reference.'
 assert len(refs)<=5 and all(p.is_file() for p in refs)
 prompt=f'''Use case: identity-preserve. Draw ONE newly painted single walking-animation frame W{a.frame:02d} of the exact celestial musician girl.
{roles}
CAMERA: exact WEST side profile facing SCREEN LEFT. One visible purple eye, tiny left-facing nose, hair flowing behind to RIGHT, zither held in front toward LEFT as image1. Never front view or back diagonal. Keep the same purple lotus gold crown, high purple bun, long purple hair, translucent pale-lavender ribbons, white-lavender robe with fine gold embroidery, lavender puff trousers, white-purple gold-trim boots, and purple-gold zither. Keep head, shoulders, torso, hands and zither stable, only tiny natural walk bob. Large round chibi head and short limbs, identical clothing volumes.
POSE W{a.frame:02d}: {PHASES[a.frame]}
Exactly TWO correctly attached legs and two boots. At least one support boot touches a single invisible ground line. No hovering, running, wide split, foot-lane swap or extra limb. Newly draw this genuine phase, no copy, mirror, interpolation, warp or translated duplicate.
COMPOSITION: single native SQUARE at 1254x1254 or larger, minimum1024 each edge. Fill about94% of total height: crown top approximately3% and lowest supporting sole approximately97%. This is larger occupancy than image1's old canvas; keep anatomy proportions, enlarge the whole newly drawn figure's framing. Center upper-body axis around50% width; safe unclipped margin all around. Do not inherit old image1 empty margins. Stable full-body size across every phase.
Genuine TRANSPARENT RGBA background, opaque painted body and naturally translucent ribbons, clean antialiased edges. Purple is intentional clothing/hair: preserve it. No colored background, floor, cast shadow, checkerboard, text, panels or labels. Finest available polished hand-painted fidelity.'''
 if a.extra:prompt+='\n'+a.extra
 req={'schema':1,'tool':'built-in image_gen','actual_model':'host-managed-unverified','configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text()),'actual_request':{'prompt':prompt,'referenced_image_paths':[str(p).replace('\\','/') for p in refs],'started_at':datetime.now(timezone.utc).isoformat()},'reference_bindings_at_start':[{'path':str(p).replace('\\','/'),'sha256':sha(p)} for p in refs],'paid_api_calls':0,'status':'request_prepared_not_yet_submitted'}
 (archive/'prompt.txt').write_bytes(prompt.encode());write(archive/'request.json',req)
 print(json.dumps({'archive':str(archive),'request':req['actual_request']},ensure_ascii=False))
def finish(a):
 archive=GEN/f'W{a.frame:02d}-single-v{a.version}'
 for script,args in [('archive_builtin_result.py',['--archive',str(archive),'--original',a.original,'--tool-result',str(archive/'tool-result.json')]),('archive_metadata.py',['--archive',str(archive)]),('import_frame.py',['--archive',str(archive),'--batch-id',archive.name,'--direction','W','--frame',str(a.frame),'--staging-root',str(archive/'staging')])]:
  subprocess.run([sys.executable,str(HERE/script),*args],check=True)
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 p1=sub.add_parser('prepare');p1.add_argument('--frame',type=int,required=True,choices=range(1,17));p1.add_argument('--version',type=int,default=1);p1.add_argument('--phase-refs',type=int,nargs='*',default=[]);p1.add_argument('--phase-first',action='store_true');p1.add_argument('--extra',default='')
 p2=sub.add_parser('finish');p2.add_argument('--frame',type=int,required=True);p2.add_argument('--version',type=int,default=1);p2.add_argument('--original',required=True)
 a=p.parse_args();prepare(a) if a.command=='prepare' else finish(a)
if __name__=='__main__':main()
