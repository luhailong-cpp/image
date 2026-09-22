"""Prepare NW-only builtin requests and archive genuine results; no generation API."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent;GEN=HERE.parent/'05-generation';ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PHASES={
1:'First contact. Anatomical LEFT leg (screen-left leg lane) reaches a small step FORWARD toward upper-left; heel contacts ground. RIGHT leg (screen-right lane) trails toward lower-right, heel lifted and toe contacts ground. Short stride with visibly separate boots.',
2:'After left contact. LEFT boot planted forward upper-left, knee softly yielding. RIGHT boot behind lower-right rolls onto its toe, heel rises slightly. Left remains the support leg.',
3:'First recoil. LEFT boot remains planted supporting; RIGHT rear foot leaves the ground, knee bends mildly and boot lifts just behind its own right-leg lane. Right foot has not yet passed left support.',
4:'Before first passing. LEFT leg supports nearly under hips. RIGHT bent knee swings ahead, its raised boot approaches the support ankle from behind but remains in its own screen-right lane.',
5:'First passing. LEFT boot planted directly under hip is the only support. RIGHT knee bends forward upper-left, RIGHT boot airborne beside and just ahead of support ankle, toe down. Keep two leg lanes visible, modest low foot lift.',
6:'After first passing. LEFT boot supports slightly behind hips, heel begins lifting. RIGHT leg swings a little farther forward upper-left with boot still airborne; right knee begins extending.',
7:'Before opposite landing. LEFT boot supports behind lower-right on toe with heel raised. RIGHT leg extends a short step forward upper-left, heel lowering but still above invisible ground.',
8:'Just before right heel contact. LEFT toe remains planted behind lower-right; RIGHT leg extended short distance forward upper-left, heel separated from ground by a tiny gap. Small change into09.',
9:'Opposite contact. RIGHT leg (screen-right leg lane) reaches a small step FORWARD toward upper-left, heel contacts ground. LEFT leg (screen-left lane) trails lower-right with heel lifted and toe contacts ground. Opposite feet assignment to01, same short stride.',
10:'After right contact. RIGHT boot planted forward upper-left, knee softly yielding. LEFT rear boot rolls onto its toe with heel rising a little. Right remains support.',
11:'Second recoil. RIGHT boot remains planted supporting. LEFT rear foot leaves ground, knee bends mildly and boot lifts behind within screen-left leg lane. Left foot has not passed support yet.',
12:'Before second passing. RIGHT leg supports nearly under hips. LEFT knee swings forward, raised boot approaches support ankle from behind but stays in its own screen-left lane.',
13:'Second passing. RIGHT boot planted directly under hip is the only support. LEFT knee bends forward upper-left, LEFT boot airborne beside and just ahead of support ankle, toe down. Opposite feet assignment to05; modest low foot lift.',
14:'After second passing. RIGHT boot supports slightly behind hips, heel begins lifting. LEFT leg swings slightly farther ahead upper-left with boot still airborne, knee begins extending.',
15:'Before loop landing. RIGHT boot supports behind lower-right on toe with heel raised. LEFT leg extends a short step ahead upper-left, heel lowering but still above ground. Same anatomy and crown height as01.',
16:'Immediately before loop contact. RIGHT toe remains planted behind lower-right. LEFT leg extends short distance ahead upper-left, heel a tiny gap above ground. Almost01 but heel not yet in contact. Tiny change into01 with no camera or stature jump.'}
def prepare(a):
 archive=GEN/f'NW{a.frame:02d}-single-v{a.version}';archive.mkdir(exist_ok=True)
 assert not (archive/'request.json').exists(),'Fresh version required'
 refs=[ROOT/'qdao_original_roster_v13/candidate/05_celestial_musician_girl/idle/NW.png',GEN/'references/portrait-inspection.png',ROOT/'designs/jubaozhai-ui/02-characters.png']
 roles='Image1 locks the exact NORTHWEST rear-left three-quarter camera, identity, hair silhouette, clothing and partly hidden zither. Its old512 canvas margins are NOT a framing guide. Image2 locks original character identity and costume details, NOT frontal camera. Image3 is the confirmed PRIMARY STYLE reference: clean bright rounded finely hand-painted finish; do not copy its UI or characters.'
 for ref in a.phase_refs:
  p=ROOT/ref if ref.endswith('.png') else GEN/ref/'raw.png';assert p.is_file(),p;refs.append(p);roles+=f' Image{len(refs)} is {ref}, phase reference ONLY; transfer its leg depth relationship into the NW camera, not its facing direction, and newly draw requested phase, do not duplicate or mirror pixels.'
 assert len(refs)<=5 and all(p.is_file() for p in refs)
 prompt=f'''Use case: identity-preserve. Produce ONE newly painted single walking-animation frame NW{a.frame:02d} of this exact celestial musician girl.
{roles}
CAMERA: NORTHWEST, facing upper-left and AWAY from viewer, rear-left three-quarter view exactly as image1. Back of head and long purple hair dominate; only a sliver of left cheek/ear, no visible frontal eye. Zither is held in FRONT of chest away from viewer, its rounded purple/gold end peeks at SCREEN LEFT. Do not mirror NE; preserve original asymmetric instrument, hair ornaments and costume construction. Same purple high bun, purple lotus and gold crown chain, long flowing purple hair, translucent pale lavender ribbons, white lavender gold-embroidered robe, short lavender puff trousers and white purple gold-trimmed boots. Large chibi head, short limbs and compact body. Upper torso, instrument, hands and head remain stable; maximum tiny natural walk bob, ribbons vary only slightly.
POSE NW{a.frame:02d}: {PHASES[a.frame]}
Exactly two correctly attached legs and two distinct boots. Feet move diagonally upper-left/lower-right within their OWN anatomical lanes and never cross or swap legs. At least one foot touches invisible ground. No floating, running, kick or wide split. This must be a genuine independently drawn animation phase, no copied/mirrored/interpolated/warped/translated duplicate.
COMPOSITION: native SQUARE 1254x1254 or larger, minimum1024 each edge, complete full body. Crown top approximately3% and lowest supporting sole approximately97%, figure fills94% of height. Keep original anatomy but use much larger canvas occupancy than old512 image1. Stable upper-body axis around50% width, safe unclipped margins. Same physical body size throughout sequence.
Genuine TRANSPARENT RGBA background, opaque painted figure and naturally translucent ribbons, clean antialiased edges. Purple belongs to real hair/clothing and must remain. No floor, cast shadow, colored background, checkerboard, text, labels, panels or multiple figures. Finest polished hand-painted fidelity.'''
 if a.extra:prompt+='\n'+a.extra
 req={'schema':1,'tool':'built-in image_gen','actual_model':'host-managed-unverified','configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text()),'actual_request':{'prompt':prompt,'referenced_image_paths':[str(p).replace('\\','/') for p in refs],'started_at':datetime.now(timezone.utc).isoformat()},'reference_bindings_at_start':[{'path':str(p).replace('\\','/'),'sha256':sha(p)} for p in refs],'paid_api_calls':0,'status':'request_prepared_not_yet_submitted'}
 (archive/'prompt.txt').write_bytes(prompt.encode());write(archive/'request.json',req);print(json.dumps({'archive':str(archive),'request':req['actual_request']}))
def finish(a):
 archive=GEN/f'NW{a.frame:02d}-single-v{a.version}'
 for script,args in [('archive_builtin_result.py',['--archive',str(archive),'--original',a.original,'--tool-result',str(archive/'tool-result.json')]),('archive_metadata.py',['--archive',str(archive)]),('import_frame.py',['--archive',str(archive),'--batch-id',archive.name,'--direction','NW','--frame',str(a.frame),'--staging-root',str(archive/'staging')])]:subprocess.run([sys.executable,str(HERE/script),*args],check=True)
def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
 a=s.add_parser('prepare');a.add_argument('--frame',type=int,required=True,choices=range(1,17));a.add_argument('--version',type=int,default=1);a.add_argument('--phase-refs',nargs='*',default=[]);a.add_argument('--extra',default='')
 a=s.add_parser('finish');a.add_argument('--frame',type=int,required=True);a.add_argument('--version',type=int,default=1);a.add_argument('--original',required=True)
 a=p.parse_args();prepare(a) if a.command=='prepare' else finish(a)
if __name__=='__main__':main()
