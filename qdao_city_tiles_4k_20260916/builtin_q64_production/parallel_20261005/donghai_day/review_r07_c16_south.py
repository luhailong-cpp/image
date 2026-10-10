from pathlib import Path
import assembly_r07_c16 as a
R=Path(__file__).resolve().parent;T=R/'r07_c16';D=T/'repairs/integrated-south-v2';Q=D/'qa'
def ref(p):return dict(file=str(p),sha256=a.sha(p))
assert a.sha(D/'candidate.png')=='3f5be4ea2f6cb9e54121761646fc0b0c218af12738fa7493c198a1f4b9944bc2'
items=[]
for name,note in [('rope-insertion','Rope tapered into the authoritative south endpoint; wooden collar and spar contact are coherent.'),('rope-joint','Former broad rope width mismatch removed; native lower rope remains immutable.'),('spar-insertion','Tiny step at the diagonal spar insertion edge removed by centered local native AI correction.')]:
 items.append(dict(ref(Q/(name+'.png')),actualView=True,nativePixels=True,result='pass-local-scope',observation=note))
for name in ['corner-nw','corner-ne','corner-sw','corner-se','overview-preview-1024']:
 items.append(dict(ref(Q/'assembly'/(name+'.png')),actualView=True,result='pass-local-scope',observation='Existing scene intact, clean water and continuous visible objects; this does not approve unbound west common edge.'))
items.append(dict(ref(Q/'assembly/south-r07-r08-common-edge-full.png'),actualView=True,nativePixelsRepacked=True,result='partial-pass-repair-pending',observation='Rope join and remaining water segments pass; mast/spar near x880..1300 retains horizontal value transition at y4096, assigned to fill16_left for bounded north-only correction.'))
items.append(dict(ref(Q/'assembly/south-halo-comparison-full.png'),actualView=True,nativePixelsRepacked=True,result='pass-halo-identity-scope',observation='Final extended bottom115 has exact authoritative south first115; whole common-edge acceptance still pending mast value correction.'))
peer=a.load_json(T/'repairs/internal-color-match/visual-review.json');cmp=a.load_json(D/'manifest.json')['qaComparisonToWaterCandidate'];identity={Path(e['file']).name:e for e in cmp};internal=[]
for e in peer['sheets']:
 name=Path(e['file']).name;dest=Q/'assembly'/name;c=identity[name]
 if c['exactSame']:
  internal.append(dict(ref(dest),result='pass-internal-scope',actualViewInheritedFrom=dict(ref(Path(e['file'])),review=ref(T/'repairs/internal-color-match/visual-review.json')),exactShaIdentity=True))
 else:
  assert name=='internal-vertical-x2048-full.png' and a.sha(dest)=='0ee7c2e7ada945ba9e48b9828fcee7779314b2997b46908a2a511f9f02574d32'
  internal.append(dict(ref(dest),result='pass-internal-scope',actualViewBy='fill16_left',evidence='Agent message: actual view of integrated-south-v1 identical sheet; continuous water, no new hard value step or fine net pattern. Exact SHA verified in v2.'))
assert len(internal)==15
a.save_json(D/'local-review.json',dict(createdAtUtc=a.utc_now(),reviewer='close_joint14',candidate=ref(D/'candidate.png'),result='pass-rope-spar-internal-and-corners-scope',items=items,internalReview=internal,remaining=['south-mast-value-transition-x880..1300','west-common-edge-awaits-stable-r07_c15'],formalAccepted=False))
native=[]
for folder,decision,note in [('south-rope','rejected','Native image retained too much lower-rope width drift.'),('south-rope-anchored','rejected','Still widened rope despite authoritative halo anchor.'),('south-rope-thin','selected','Exact endpoint-constrained native repair narrowed north rope; source south kept unchanged by integration mask.'),('south-spar-edit','rejected','Off-center tiny-notch repair changed lower spar edge beyond intended integration.'),('south-spar-center','selected','Centered contour correction eliminated tiny spar step while preserving collar and rope outside integration.')]:
 p=T/'repairs'/folder/'edited-native.png';native.append(dict(ref(p),generationRecord=ref(Path(str(p)+'.generation.json')),actualView=True,decision=decision,observation=note))
a.save_json(T/'repairs/south-native-selection-review.json',dict(createdAtUtc=a.utc_now(),reviewer='close_joint14',nativeImages=native,actualModel=None,actualQuality=None,sourceSouthPreserved=True,spatialResampling=False))
print(a.sha(D/'local-review.json'))
