from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image

base=Path(__file__).resolve().parent
assert base.name=='r09_c09' and base.parent.name=='lanxian_day'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
observations={
 4:'Existing long diagonal stone joint and rounded green leaf clusters retained, no additional objects. Broad low-contrast stone brush shapes remain for assembled seam review.',
 3:'Existing red post, gold finial and beads, two cropped pairs of spiral crossarms and small lower-right leaf cluster retained. No text or additional lantern. Broad stone shading requires assembled seam review.',
 2:'Quiet open stone, existing low curved groove and two far-right cropped red spiral arm tips retained. No added shaft, plants or floor joints. Broad low-contrast brush shapes remain.',
 1:'Empty ivory stone retained with only the original cropped bottom curved groove. No added objects or floor joints. Broad low-contrast diagonal brush shapes remain for assembly review.'
}
items=[]
for col in (4,3,2,1):
 cell=f'r03_c{col:02d}'
 path=base/'native'/f'{cell}.png';rp=Path(str(path)+'.generation.json');rec=read(rp)
 jp=Path(rec['sourceJob']);job=read(jp);receipt_path=Path(rec['evidence']['toolResultPath']);receipt=read(receipt_path)
 with Image.open(path) as im:size=im.size;fmt=im.format
 checks={
 'imageHashMatches':sha(path)==rec['sha256'],
 'sourcePngByteIdentical':sha(receipt['sourceOutputPath'])==sha(path)==rec['evidence']['sourceOutputSha256'],
 'dimensions1254Square':size==(1254,1254) and fmt=='PNG',
 'sourceJobHashMatches':sha(jp)==rec['sourceJobSha256'],
 'receiptHashMatches':sha(receipt_path)==rec['evidence']['toolResultSha256'],
 'promptFileHashMatches':sha(rec['prompt'])==rec['promptSha256'],
 'actualPromptMatchesReceipt':Path(rec['prompt']).read_text(encoding='utf-8')==receipt['prompt']==job['prompt']==rec['submittedParameters']['prompt'],
 'onlyGuideAndStyleSubmitted':len(rec['references'])==2 and Path(rec['references'][0]['path']).name==f'{cell}.layout-only.png' and Path(rec['references'][1]['path']).name=='04-guild.png' and rec['submittedParameters']['referenced_image_paths']==[x['path'] for x in receipt['references']],
 'actualAndSubmittedModelQualityNull':all(rec[k] is None for k in ('actualModel','actualQuality')) and all(rec['submittedParameters'][k] is None for k in ('model','quality')),
 'referenceHashesMatch':all(sha(x['path'])==x['sha256'] for x in rec['references']),
 'contextSourceHashesMatch':all(sha(x['file'])==x['sha256'] for x in job['constraints'])
 }
 assert all(checks.values()),(cell,checks)
 items.append({'cell':cell,'native':str(path),'sha256':sha(path),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'generatedAt':rec['generatedAt'],'receipt':str(receipt_path),'checks':checks,'actualVisualReview':{'guideViewed':True,'style04GuildViewed':True,'outputViewed':True,'outputViewMethod':'Full native generatedImage tool display inspected at 1254 square; local guide and approved style viewed using view_image before each call.','observation':observations[col],'singleImageVisibleArtificialBreakIdentified':False,'isFullSeamAcceptance':False},'status':'native_candidate_ready_for_assembly_and_seam_QA'})
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r09_c09','worker':'westward_row03','row':3,'traversal':[x['cell'] for x in items],'nativeCount':4,'nativePixels':[1254,1254],'rejectedNativeCount':0,'actualBuiltinCalls':4,'allRecordedHashesVerified':True,'allGuidesStyleAndGeneratedImagesActuallyViewed':True,'items':items,'guidePixelsNeverUsedAsFinalArt':True,'formalAccepted':False,'wholeTileQaComplete':False,'modelQualityEvidence':'Target config snapshot retained per image; submitted and actual model/quality null because builtin exposed no selectors or returned evidence.','pending':'Assemble all 16 native cells and inspect exact crop joins, external north/east boundaries and guide context bands. Source audit is not seam acceptance.'}
dest=base/'worker-row03.json'
assert not dest.exists()
dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(dest),'sha256':sha(dest),'allChecksPassed':True,'nativeCount':len(items)}))
