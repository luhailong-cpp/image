"""SW-only immutable request and result archival; never calls an image API."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess, sys
sys.dont_write_bytecode = True
HERE=Path(__file__).resolve().parent; GEN=HERE.parent/'05-generation'; ROOT=HERE.parents[2]
PHASES={
1:'First contact. The SCREEN-LEFT boot is forward toward lower-left, heel newly touching the invisible floor; SCREEN-RIGHT boot trails farther away and slightly higher, its toe just leaving ground. Small short walk stride, both legs separate. Left screen lane is the new support.',
2:'Loading the first contact. SCREEN-LEFT boot stays forward and planted, knee slightly yields. SCREEN-RIGHT trailing heel rises and its toe barely touches, about to lift. A small change after SW01, no support-leg swap.',
3:'Early first swing. SCREEN-LEFT boot stays planted supporting the body. SCREEN-RIGHT boot just lifts from its trailing position, knee begins bending, foot still behind and slightly higher than planted boot. Smaller lift than SW05.',
4:'Approaching first passing. SCREEN-LEFT boot supports under body. SCREEN-RIGHT knee bends and comes forward, airborne boot moves nearer the support ankle in its own right screen lane. Intermediate lift between SW03 and SW05.',
5:'First passing key. SCREEN-LEFT boot is firmly planted supporting her. SCREEN-RIGHT knee is raised and bent, its boot distinctly airborne about one short boot-height above floor, advancing forward in its own lane. Exactly one raised boot, right screen lane. Relaxed walking, not a kick.',
6:'After first passing. SCREEN-LEFT boot remains supporting and begins a small heel rise. SCREEN-RIGHT knee starts extending forward toward lower-left, airborne boot lower than SW05 but not contacting. Distinct new leg geometry.',
7:'Approaching opposite contact. SCREEN-LEFT boot trails with heel raised and toe planted. SCREEN-RIGHT boot extends forward in its own screen lane, heel lowered almost to floor, leg less bent than SW06. Do not cross boots.',
8:'Just before opposite contact. SCREEN-RIGHT forward heel is a tiny gap above floor, nearly SW09; SCREEN-LEFT trailing foot has raised heel and toe planted. Small stride and stable head height.',
9:'Opposite contact key. SCREEN-RIGHT boot is the forward boot and heel newly touching the invisible floor; SCREEN-LEFT boot trails farther away, slightly higher, heel raised with toe at floor. Opposite support assignment to SW01; keep each boot in its own screen lane.',
10:'Loading opposite contact. SCREEN-RIGHT boot remains forward and planted, knee slightly yields. SCREEN-LEFT trailing heel rises and its toe barely touches, about to lift. Small change after SW09, right screen lane supports.',
11:'Early second swing. SCREEN-RIGHT boot stays planted supporting the body. SCREEN-LEFT boot just lifts from its trailing position, knee begins bending, foot still behind and slightly higher than planted boot. Smaller lift than SW13.',
12:'Approaching second passing. SCREEN-RIGHT boot supports under body. SCREEN-LEFT knee bends and comes forward, airborne boot nears support ankle in its own left screen lane. Intermediate lift between SW11 and SW13.',
13:'Second passing key. SCREEN-RIGHT boot is firmly planted supporting her. SCREEN-LEFT knee is raised and bent, its boot distinctly airborne about one short boot-height above floor, advancing forward in its own lane. Exactly opposite raised-leg assignment to SW05. Relaxed walk, not a kick.',
14:'After second passing. SCREEN-RIGHT boot remains supporting and begins a small heel rise. SCREEN-LEFT knee begins extending forward toward lower-left, airborne boot lower than SW13 but not contacting. Distinct new leg geometry.',
15:'Approaching loop contact. SCREEN-RIGHT boot trails with heel raised and toe planted. SCREEN-LEFT boot extends forward, heel lowered nearly to floor, leg less bent than SW14. Same anatomical size and head height as SW01.',
16:'Immediately before loop contact. SCREEN-LEFT forward heel has a tiny gap above floor, nearly SW01 contact; SCREEN-RIGHT trailing foot has raised heel and toe planted. Tiny difference into SW01, stable head/crown/torso and camera, no foot-lane crossing.'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(a):
 archive=GEN/f'SW{a.frame:02d}-single-v{a.version}';archive.mkdir(exist_ok=True)
 assert not (archive/'request.json').exists(),'Use a fresh attempt version'
 refs=[ROOT/'qdao_original_roster_v13/candidate/05_celestial_musician_girl/idle/SW.png',GEN/'references/portrait-inspection.png',ROOT/'designs/jubaozhai-ui/02-characters.png']
 roles='Image1 is the authoritative SOUTHWEST front-left three-quarter camera and costume/equipment layout. Its old512 canvas empty margin is NOT a framing guide. Image2 fixes exact portrait identity and painted details only, NOT camera. Image3 is the confirmed PRIMARY STYLE reference: bright, clean, rounded, finely hand-painted material and finish; copy no UI or other characters.'
 for ref in a.phase_refs:
  candidate=GEN/ref/'raw.png';assert candidate.is_file(),candidate;refs.append(candidate)
  roles+=f' Image{len(refs)} is {ref}, preserving anatomy, framing and costume while drawing the specified DIFFERENT leg phase.'
 assert len(refs)<=5 and all(p.is_file() for p in refs)
 prompt=f'''Use case: identity-preserve. Create ONE genuinely newly painted full single walking sprite SW{a.frame:02d} of this exact celestial musician girl.
{roles}
CAMERA is SOUTHWEST front-left three-quarter, walking diagonally toward SCREEN LOWER LEFT; face and nose point left, BOTH purple eyes readable with farther eye foreshortened, not straight front/back/side. Lock exact identity: high purple bun with gold lotus crown and purple jewel chains, long flowing purple hair, pale-lavender translucent ribbons, round smiling face with purple forehead mark, white-lavender gold-embroidered robe and wide sleeves, green waist knot, lavender puff trousers, white-purple boots. She carries the SAME purple-gold zither diagonally across her chest from lower SCREEN LEFT to upper SCREEN RIGHT, hands fixed in the same positions as image1. No instrument side reversal or extra instrument. Stable chibi proportions, large round head and short limbs; no costume redesign.
ACTION SW{a.frame:02d}: {PHASES[a.frame]}
Exactly two correctly attached legs and two separate boots. Keep SCREEN-LEFT and SCREEN-RIGHT leg lanes distinct through the walk. At least one boot supports on an invisible floor. Small comfortable walk; minimal natural torso bob. Head, facial proportions, hair volume, shoulders, zither size and angle stay steady. Do not copy, mirror, interpolate, warp, translate an existing pose or produce a sheet.
COMPOSITION: square native1254x1254 or larger, minimum1024 each edge. Entire character fills about94% native canvas height: crown top about3%, lowest supporting sole about97%; centered upper-body axis about50% width. Deliberately use MORE canvas occupancy than old image1, preserving anatomical proportions; do not inherit its large blank margins. Safe unclipped narrow margin all around, all ribbons/crown/boots fully visible.
True TRANSPARENT RGBA background, clean naturally antialiased silhouette. Intentional lavender and purple clothing/ribbons must be preserved, with naturally translucent ribbon edges. No magenta/blue matte spill, no floor/shadow/checkerboard/text/labels/grid. Finest available polished hand-painted fidelity.'''
 if a.extra:prompt+='\n'+a.extra
 req={'schema':1,'tool':'built-in image_gen','actual_model':'host-managed-unverified','configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text()),'actual_request':{'prompt':prompt,'referenced_image_paths':[str(p).replace('\\','/') for p in refs],'started_at':datetime.now(timezone.utc).isoformat()},'reference_bindings_at_start':[{'path':str(p).replace('\\','/'),'sha256':sha(p)} for p in refs],'paid_api_calls':0,'status':'request_prepared_not_yet_submitted'}
 (archive/'prompt.txt').write_bytes(prompt.encode());write(archive/'request.json',req)
 print(json.dumps({'archive':str(archive),'request':req['actual_request']},ensure_ascii=False))
def finish(a):
 archive=GEN/f'SW{a.frame:02d}-single-v{a.version}'
 for script,args in [('archive_builtin_result.py',['--archive',str(archive),'--original',a.original,'--tool-result',str(archive/'tool-result.json')]),('archive_metadata.py',['--archive',str(archive)]),('import_frame.py',['--archive',str(archive),'--batch-id',archive.name,'--direction','SW','--frame',str(a.frame),'--staging-root',str(archive/'staging')])]:subprocess.run([sys.executable,str(HERE/script),*args],check=True)
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 a=sub.add_parser('prepare');a.add_argument('--frame',type=int,required=True,choices=range(1,17));a.add_argument('--version',type=int,default=1);a.add_argument('--phase-refs',nargs='*',default=[]);a.add_argument('--extra',default='')
 a=sub.add_parser('finish');a.add_argument('--frame',type=int,required=True);a.add_argument('--version',type=int,default=1);a.add_argument('--original',required=True)
 a=p.parse_args();prepare(a) if a.command=='prepare' else finish(a)
if __name__=='__main__':main()
