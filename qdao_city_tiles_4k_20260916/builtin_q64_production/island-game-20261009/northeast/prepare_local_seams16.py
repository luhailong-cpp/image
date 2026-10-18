from native_work import *
batch=ZONE/'qa/local-seams16-20261016'
batch.mkdir(exist_ok=True)
ids=['r03_c09_cross_local_seams16_top_v1','r03_c09_cross_local_seams16_middle_v1']
selected=read(ZONE/'selection-r03_c09.json')
assert selected['cores'][0][1]=='r03_c09_p01_02_v3'
assert selected['cores'][1][1]=='r03_c09_p02_02'
refs=[{'file':(ROOT/'designs/mail-ui-v1/01-mail-event.png').as_posix(),'role':'approved Daoist hand-painted style only; no UI, text, figures or night'}, {'file':(ROOT/'designs/team-ui-v2/team-ui-v2.png').as_posix(),'role':'approved Daoist hand-painted style only; no UI or figures'}]
for e in refs: e['sha256']=sha(e['file'])
for index,ident in enumerate(ids):
    native=[34189,8077+index*1024,35443,9331+index*1024]
    im=Image.new('RGB',(1254,1254));sources=[]
    for row in range(max(0,index-1),min(3,index+2)):
        low=max(native[1],8192+row*1024 if row>0 else native[1]);high=min(native[3],8192+(row+1)*1024)
        if low>=high:continue
        for col in (1,2):
            name=selected['cores'][row][col];f=ZONE/'native'/f'{name}.png';pb=patch(name)['nativeWorldBox']
            left=max(native[0],32768+col*1024);right=min(native[2],32768+(col+1)*1024)
            crop=[left-pb[0],low-pb[1],right-pb[0],high-pb[1]];at=[left-native[0],low-native[1]]
            im.paste(Image.open(f).crop(crop),at);sources.append({'file':f.as_posix(),'sha256':sha(f),'sourceCrop':crop,'targetPaste':at})
    guide=ZONE/'guides'/f'{ident}.png';assert not guide.exists();im.save(guide)
    coreCrop=[115,115,1139,1139];core=[native[0]+115,native[1]+115,native[2]-115,native[3]-115]
    write(guide.with_suffix('.png.derivation.json'),{'operation':'exact selected native pixel assembly, no resampling or blending','sources':sources,'nativeWorldBox':native,'coreWorldBox':core,'coreCrop':coreCrop,'tileLocalPaste':[core[0]-32768,core[1]-8192],'finalArt':False})
    inputs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'sole edit target; exact native composite, join x627; preserve exterior geometry'},*refs]
    write(ZONE/'prompts'/f'{ident}.inputs.json',inputs)
    if index==0:
        request='Repair only the small disconnected and kinked diagonal grout contours around x550-700, y400-800 in the center of image 1. This is one continuous stone courtyard. Join each existing thin grout line smoothly to the corresponding existing line on the other side; remove spurious step/jog/overlapping edge at vertical center x627. Keep the same number, shape and positions of all paving slabs outside that narrow neighborhood. Do not replace the pavement pattern. Preserve all correct grout endpoints exactly.'
    else:
        request='Repair the narrow vertical compositing boundary through x627 in image 1: in upper stone area smoothly reconcile the too-dense/too-sharp left stone grain with the right stone texture while keeping every grout line endpoint and slab contour exactly where it is. Lower down reconnect any cut green leaf silhouettes across x627 without relocating the flower clusters, sphere, post, coping or foliage mass. Remove a mechanical vertical density line, not naturally varying leaf shadows. Preserve all correct shapes and their precise positions.'
    prompt='Use case: precise-object-edit. Output one opaque native 1254x1254 PNG at exactly the same framing, scale, orientation and pixel placement as image 1. '+request+' Edit target is image 1 only. References 2-3 constrain hand-painted Daoist Q finish, but do not import their UI, characters, text, panels, night or architecture. Preserve daylight, natural pale grey stone, warm ivory wall and existing leaves. Keep at least the outer 250 pixels on all four sides identical to image 1. Keep everything outside x450-800 unchanged. Make local painted-detail repairs at native resolution; no global recoloring, blur, zoom, rescale, perspective change, new object or altered masonry geometry. This is a small restoration, and the unedited surrounding source must remain exact.'
    (ZONE/'prompts'/f'{ident}.prompt.txt').write_text(prompt,encoding='utf-8')
write(batch/'audit.json',{'time':now(),'reviewer':'/root/local_seams16','predecessorRecovery':'No new r03_c09 seam sources or requests found from predecessor. Old cross_p0102_right_repair dates to Oct13 and is rejected at all four crop edges.','sourceSelectionSnapshot':selected,'sourceSelectionSha256':sha(ZONE/'selection-r03_c09.json'),'ids':ids,'status':'prepared','newCallsAllowed':2,'actualModel':None,'noSharedGitMutation':True})
print(json.dumps({'ids':ids,'audit':str(batch/'audit.json')}))
