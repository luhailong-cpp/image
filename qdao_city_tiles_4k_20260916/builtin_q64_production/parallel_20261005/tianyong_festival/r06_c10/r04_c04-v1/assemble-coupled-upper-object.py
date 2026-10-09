from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
D=Path(__file__).parent;F=D/'final-v5';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
n=np.array(Image.open(D/'native.png').convert('RGB'));r=np.array(Image.open(D/'repair-v3/native.png').convert('RGB'));c=np.array(Image.open(D/'repair-v3/target.png').convert('RGBA'))
y,x=np.indices((1254,1254));sm=lambda v:np.clip(v,0,1)**2*(3-2*np.clip(v,0,1))
cw=np.where(c[:,:,3]==255,sm((y-560)/80),0);j=np.rint(r*(1-cw[:,:,None])+c[:,:,:3]*cw[:,:,None]).astype('uint8')
full=np.zeros((1954,1254,3),dtype='uint8');full[:700]=n[:700];full[700:]=j
w=sm((np.arange(80)-40)/40)[:,None,None];full[700:780]=np.rint(n[700:780]*(1-w)+j[:80]*w).astype('uint8')
Image.fromarray(full).save(F/'joined.png');Image.fromarray(j).save(F/'focused-joint.png');Image.fromarray(np.rint(cw*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('body',(0,650,1254,1454)),('return-tail',(0,1120,1139,1500))]:Image.fromarray(full).crop(box).save(Q/(name+'.png'))
record={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'repair':ref(D/'repair-v3/native.png'),'context':ref(D/'repair-v3/target.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'mainNativeWindowGlobalLTRB':[39821,23437,41075,24691],'repairWindowGlobalLTRB':[39821,24137,41075,25391],'assembledUnionWindowGlobalLTRB':[39821,23437,41075,25391],'repairToMainTranslation':[0,700],'translationIsExactWorldCropMapping':True,'topBlendMainY':[740,780],'sourceWeightFocusedY':[560,640],'sourceExactBelowFocused640':bool(np.array_equal(j[640:,:1139],c[640:,:1139,:3])),'actualModel':None,'actualQuality':None,'formalAccepted':False,'notes':['Coupled redraw includes the complete upper object and base, ending in already known ground below. No large warp or resizing.','Joined dimensions1254x1954 are an exact world-space native composition of two1254-square AI windows with700px vertical offset.']}
(F/'assembly.json').write_text(json.dumps(record,indent=2),encoding='utf8')
q=read(D/'request.json');q['selectedFinalDirectory']='final-v5';q['manifestWindowTileLocalLTRB']=[2957,2957,4211,4911];q['manifestWindowGlobalLTRB']=[39821,23437,41075,25391];q['bottomReturnMainYEnd']=1340;(D/'request.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(ref(F/'joined.png')))

