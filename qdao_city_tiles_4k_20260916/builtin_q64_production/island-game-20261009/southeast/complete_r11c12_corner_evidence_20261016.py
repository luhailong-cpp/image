from workflow import *
from PIL import Image
mf=ROOT/'qa'/'r11_c12-external-local-20261013'/'manifest.json';m=read(mf)
assert sha(mf)=='dc28bb6e7259362316c3fcf3d856e636a2b8a2d553e2f6fb151abe051857f579'
for x in m['sources'].values():assert sha(Path(x['file']))==x['sha256']
entries=[e for e in m['entries'] if e['kind']=='actual_external_seam'];assert len(entries)==16
for e in entries:assert e['status']=='visual_passed' and sha(Path(e['file']))==e['sha256']
r=read(ROOT/'production-resume-20261012.json');by={x['tile']:x for x in r['currentAdoptedCandidates']}
q=ROOT/'qa'/'r11_c12-complete-corners-20261016';q.mkdir(exist_ok=False)
corners={'NW':[(10,11),(10,12),(11,11),(11,12)],'NE':[(10,12),(10,13),(11,12),(11,13)],'SW':[(11,11),(11,12),(12,11),(12,12)],'SE':[(11,12),(11,13),(12,12),(12,13)]}
out=[]
for name,coords in corners.items():
 im=Image.new('RGB',(512,512));ss=[]
 for k,(rr,cc) in enumerate(coords):
  tid=f'r{rr:02}_c{cc:02}';rec=by[tid];f=Path(rec['candidate']);assert sha(f)==rec['sha256'];x0=3840 if k%2==0 else 0;y0=3840 if k<2 else 0;box=[x0,y0,x0+256,y0+256];dest=[(k%2)*256,(k//2)*256];im.paste(Image.open(f).convert('RGB').crop(box),dest);ss.append({'tile':tid,'file':str(f),'sha256':sha(f),'sourceCrop':box,'destination':dest})
 f=q/f'{name}.png';im.save(f);out.append({'id':name,'file':str(f),'sha256':sha(f),'sources':ss,'status':'pending_visual'})
write(q/'manifest.json',{'tile':'r11_c12','candidate':by['r11_c12']['candidate'],'candidateSha256':by['r11_c12']['sha256'],'prior16ExternalEdgesVerifiedUnchanged':True,'priorManifest':str(mf),'priorManifestSha256':sha(mf),'entries':out,'operation':'exact native-pixel crops/hard paste; no resize/blend','formalAccepted':False})
print(q)
