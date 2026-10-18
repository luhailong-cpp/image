from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json,sys
B=Path(__file__).resolve().parents[1];T=B/'r15_c06';p=T/'pipeline/prompts';a='resume-20261017-v02';patch='p01_01'
src=Path("C:\\Users\\luyua\\.codex\\generated_images\\01a12076-0b9d-76b2-949d-c4cf520a83be\\exec-bb1c96f5-fb13-4b3a-b247-669a4c714d52.png");seed=T/'pipeline/guides/p01_01.resume-20261017-v01.continuity-seed.png';out=T/f'pipeline/guides/{patch}.{a}.native-strips-restored-guidance.png'
assert not out.exists()
sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest()
with Image.open(src) as im:im2=im.convert('RGB')
with Image.open(seed) as im:
 im2.paste(im.crop((0,230,230,1254)),(0,230));im2.paste(im.crop((0,0,1254,230)),(0,0))
im2.save(out)
d={'file':str(out),'sha256':sha(out),'operation':'exact crop and paste of genuine native TOP230 and LEFT230 onto unselected native; guidance only','gameArt':False,'sourceResampling':False,'sources':[{'file':str(src),'sha256':sha(src)},{'file':str(seed),'sha256':sha(seed)}],'formalAccepted':False}
dp=Path(str(out)+'.derivation.json');dp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=json.loads((p/f'{patch}.resume-20261017-v01.request.json').read_text(encoding='utf-8-sig'))
prompt="""Use case: precise-object-edit. Edit Image1 same exact native1254 crop. Remove the INVENTED diagonal grid and strip divider, leave only TWO real diagonal joints from native anchors. Preserve exact TOP230 and LEFT230 inputs. Real joint A enters TOP at (85,0), crosses(300,230), then continue straight DOWN RIGHT across the interior to the real horizontal joint at y970 near x1040. Real joint B enters LEFT at(0,790), crosses(230,680), continue straight UP RIGHT to the right edge near y190. These two joints simply cross. Remove ALL other new diagonal/square tile joints in central field, remove the artificial y230 horizontal divider, remove invented vertical joints at x245/x975 in the lower pale band and x245/x860 in blue. Preserve only original real horizontal grout at y970 and true gray/blue border at y1147, unchanged height. Blue exists only below1147. Fill removed lines with broad quiet continuous cool pale gray stone, match native gray TOP/LEFT with subtle broad shading. Image5 is quiet native gray material only, not geometry. No grid, frames, dense cellular marks, new cracks, new stone rows or objects, no blue/cream roads replacing joints. No architectural object, text, people, UI, zoomout. Image2 approved wholecity geometry only, Image3 daylight material, Image4 Daoist Q hand paint. First image has mechanically restored exact native strips as guidance, not final art."""
pp=p/f'{patch}.{a}.prompt.txt';rp=p/f'{patch}.{a}.request.json';assert not pp.exists() and not rp.exists();pp.write_text(prompt+'\n',encoding='utf-8')
r.update(prompt=prompt+'\n',promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat(),editBaseRequest={'file':str(p/f'{patch}.resume-20261017-v01.request.json'),'sha256':sha(p/f'{patch}.resume-20261017-v01.request.json')})
r['references'][0]={'file':str(out),'sha256':sha(out),'role':'mechanical exact native strips restored onto actual returned native, edit guidance only, no final art','derivationFile':str(dp),'derivationSha256':sha(dp)}
r['referenced_image_paths']=[x['file'] for x in r['references']]
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dis=p/f'{patch}.resume-20261017-v01.disposition.json';assert not dis.exists()
dis.write_text(json.dumps({'source':str(src),'sha256':sha(src),'actualNativeViewed':True,'selected':False,'reason':'Invented diagonal tile grid, artificial y230 divider and broken native incoming joints. Functional blue border retained; do not propagate invented grout.','formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(rp),'guidance':str(out)},ensure_ascii=False))

