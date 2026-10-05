import sys,json,hashlib,datetime
from pathlib import Path
from PIL import Image
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/06-xiluo")
frame=sys.argv[1]
receipt=json.loads((root/'receipts/cast/E'/f'{frame}.json').read_text(encoding='utf-8'))
src=Path(receipt['sourcePath'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=Image.open(src)
native.load()
im=native.convert('RGBA')
dst=root/'runtime/cast/E'/f'{frame}.png'
dst.parent.mkdir(parents=True,exist_ok=True)
op={'type':'whole_canvas_resize','resample':'LANCZOS','from':list(im.size),'to':[1024,1024],'crop':None,'translation':None,'perFrameAlignment':False}
if im.size != (1024,1024):
    im=im.resize((1024,1024),Image.Resampling.LANCZOS)
else:
    op['type']='RGBA_PNG_export_no_geometry_change'
im.save(dst)
a=im.getchannel('A')
record={
'file':dst.relative_to(root).as_posix(),'sha256':sha(dst),'generatedAt':receipt['completedAt'],'tool':'image_gen.imagegen','route':'builtin',
'configSnapshot':json.loads(Path(r'D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),
'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':receipt['referencePaths']},
'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未开放 model/quality 选择器，返回未披露型号或质量。',
'prompt':f'prompts/cast/E/{frame}.txt','references':[{'path':p,'role':(['E identity and front camera','W identity for shell and attachments only','primary approved painted materials/style','previous verified cast E frame continuity'][i])} for i,p in enumerate(receipt['referencePaths'])],
'evidence':{'receipt':f'receipts/cast/E/{frame}.json','returnedFields':['image_url','output_hint'],'modelField':None,'qualityField':None},
'native':{'sourcePath':str(src),'width':native.width,'height':native.height,'mode':native.mode,'format':native.format,'sha256':sha(src)},
'derivedFrom':{'path':str(src),'sha256':sha(src)},'operation':op,
'exported':{'width':1024,'height':1024,'format':'PNG','mode':'RGBA','alphaExtrema':list(a.getextrema()),'alphaBBox':list(a.getbbox()),'transparentPixels':a.histogram()[0]},
'frame':int(frame),'action':'cast','direction':'E','durationMs':45,'pivot':[0.5,0.08],'anchorPx':[512,942],
'event':'cast_release' if frame=='10' else None,
'visualReview':{'status':'individually_viewed','notes':receipt['visualNotes'],'dynamicReview':'parent_preview_pending'},
'gameIntegration':'not_tested'}
rec=root/'records/cast/E'/f'{frame}.generation.json'
rec.parent.mkdir(parents=True,exist_ok=True)
rec.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frame':frame,'native':record['native'],'exported':record['exported'],'sha256':record['sha256']},ensure_ascii=False))

