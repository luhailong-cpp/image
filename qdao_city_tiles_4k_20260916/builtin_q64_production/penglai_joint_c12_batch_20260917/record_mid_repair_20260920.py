import sys,json,hashlib,shutil
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
R=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/penglai_mid_autumn/r09_c10_c11_c12_joint/repairs_v2_20260920')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ident,host=sys.argv[1:];host=Path(host);out=R/'native'/f'{ident}.png';assert not out.exists()
j=next(j for j in json.loads((R/'plan.json').read_text())['jobs'] if j['id']==ident)
ref=Path(j['guide']);assert sha(ref)==j['guideSha256'];prompt=R/'prompts'/f'{ident}.prompt.txt';txt=prompt.read_text().rstrip()
im=Image.open(host);assert im.size==(1254,1254) and im.convert('RGBA').getchannel('A').getextrema()==(255,255)
shutil.copy2(host,out);assert sha(host)==sha(out)
rec={'schemaVersion':1,'id':ident,'appearance':'penglai_mid_autumn','role':'native_local_seam_repair','route':'builtin_image_gen','createdAtUtc':datetime.now(timezone.utc).isoformat(),'requestedProduct':'ChatGPT Images 2.5','requestedModelTarget':'gpt-image-2.5-sunburst','requestedQualityTarget':'max','backendModelVerified':False,'actualModel':None,'actualQuality':None,'actualNativePixels':[1254,1254],'sourceOutputPath':str(host),'sourceOutputSha256':sha(host),'outputFile':str(out),'outputSha256':sha(out),'promptFile':str(prompt),'promptSha256':sha(prompt),'submittedPromptSha256':hashlib.sha256(txt.encode()).hexdigest(),'submittedImages':[{'path':str(ref),'sha256':sha(ref)}],'toolCall':{'name':'image_gen.imagegen','prompt':txt,'referenced_image_paths':[ref.as_posix()],'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'sourceCropLTRB':j['sourceCropLTRB'],'proposedPasteROIInTriple':j['pasteROIInTriple'],'sourceBytesPreserved':True,'finalArtUpscaled':False,'resizedAfterGeneration':False,'visualStatus':'pending_composite_review'}
out.with_suffix('.record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'id':ident,'sha256':sha(out)}))
