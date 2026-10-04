import json,hashlib,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
suffix=sys.argv[1] if len(sys.argv)>1 else '20261003'
record_path=ROOT/'records'/f'run_W_global_camera_registration_{suffix}.json'
if record_path.exists(): raise FileExistsError('Preserve previous registration evidence: '+str(record_path))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
S=901/1024;TX=61;TY=97
before=[];after=[]
for dst in sorted((ROOT/'runtime/run/W').glob('*.png')):
 recpath=dst.with_name(dst.name+'.generation.json');r=json.loads(recpath.read_text(encoding='utf-8'))
 before.append({'file':dst.relative_to(ROOT).as_posix(),'sha256':sha(dst),'generationRecordBefore':r})
 src=ROOT/r['derivedFrom'][0]['file'];native=Image.open(src);native.load()
 assert native.mode=='RGBA' and native.size==(1254,1254)
 out=Image.new('RGBA',(1024,1024));out.alpha_composite(native.resize((901,901),Image.Resampling.LANCZOS),(TX,TY));out.save(dst)
 r['sha256']=sha(dst)
 r['operation']='Uniform full-native-canvas resize 1254 to 901 then place at fixed (61,97) in 1024 RGBA. Same operation on all existing W frames. No bbox-derived parameters, no per-frame alignment, no anatomy modification.'
 r['cameraRegistration']={'applied':True,'purpose':'global camera/scale normalization toward approved idle only','nativeInputSize':[1254,1254],'resampledSize':[901,901],'placement':[TX,TY],'sameForEveryWestFrame':True,'matrixNativeToRuntime':[[901/1254,0,TX],[0,901/1254,TY],[0,0,1]],'equivalentMatrixFromUnregistered1024':[[S,0,TX],[0,S,TY],[0,0,1]],'noPerFrameBBoxFit':True,'sourceNativeSha256':sha(src),'selectionEvidence':'review/run_W_key_camera_proposal_20261003.json'}
 r['anchor']={'type':'global-camera transformed manual ground/root trial','x':S*512+TX,'y':S*960+TY,'sourceCanvasRootTrial':[512,960],'normalizedUnityPivot':[ (S*512+TX)/1024,1-(S*960+TY)/1024 ],'verified':False,'unverifiedReason':'Reference line and matrix do not prove contact. Individual poses and perspective feet require review; client unavailable.'}
 recpath.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 after.append({'file':r['file'],'sha256':r['sha256'],'nativeSource':r['derivedFrom'][0],'cameraRegistration':r['cameraRegistration'],'anchor':r['anchor']})
record_path.write_text(json.dumps({'before':before,'after':after,'change':'single uniform global registration; not a grounding/anatomy fix','sameMatrixForAllFrames':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(after),'sameMatrix':True,'scale':S,'tx':TX,'ty':TY,'rootTrial':[S*512+TX,S*960+TY]},ensure_ascii=False))


