from native_work import *
ident='r03_c09_cross_local_seams16_foliage_v1'
native=[34074,10125,35328,11379]
im=Image.new('RGB',(1254,1254));sources=[]
sel=read(ZONE/'selection-r03_c09.json');assert sel['cores'][2][1:3]==['r03_c09_p03_02','r03_c09_p03_03']
for name,world in [('r03_c09_p03_02',[34074,10125,34816,11379]),('r03_c09_p03_03',[34816,10125,35328,11379])]:
    p=patch(name)['nativeWorldBox'];f=ZONE/'native'/f'{name}.png';crop=[world[0]-p[0],world[1]-p[1],world[2]-p[0],world[3]-p[1]];at=[world[0]-native[0],world[1]-native[1]]
    im.paste(Image.open(f).crop(crop),at);sources.append({'file':f.as_posix(),'sha256':sha(f),'sourceCrop':crop,'targetPaste':at})
g=ZONE/'guides'/f'{ident}.png';assert not g.exists();im.save(g)
core=[34189,10240,35213,11264]
write(g.with_suffix('.png.derivation.json'),{'operation':'exact native source crop/paste, no generation, filtering or resampling','sources':sources,'nativeWorldBox':native,'coreWorldBox':core,'coreCrop':[115,115,1139,1139],'tileLocalPaste':[1421,2048],'finalArt':False,'issue':'Original p03_02 sourcex1024 corresponds to edit targetx627; existing actual core joinx742 is already coherent.'})
refs=[{'file':g.as_posix(),'sha256':sha(g),'role':'sole edit target, exact native local composite; vertical darker material division at x627 is defect; actual source join at x742 is coherent'}]
for p in ['designs/mail-ui-v1/01-mail-event.png','designs/team-ui-v2/team-ui-v2.png']:
    f=ROOT/p;refs.append({'file':f.as_posix(),'sha256':sha(f),'role':'approved Daoist hand-painted finish only; no UI, figures or night'})
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
prompt='Use case: precise-object-edit. Output one opaque native1254x1254 PNG. Image1 is the exact edit target, and must retain identical framing, scale, camera and object positions. Repair only the unnatural perfectly vertical darker density/exposure edge running at x627 through the leafy shrub. The leaf silhouettes already align; do NOT move or resize the leaves, flowers, stems, ivory pillar or wall. Fix the tiny discontinuity in the painted foliage lighting/material across x627, making each existing leaf and dark gap read continuously with natural varying highlights and shadows. Concentrate in x530-720,y230-1040; gently restore hand-painted detail there instead of blurring. Preserve the source pixels outside this narrow local region, particularly the entire outer200px on all four sides and the stone pillar. Keep the existing coherent actual join at x742 intact. Avoid any rectangular brightened band, broad tonal wash, uniform vertical stripe, new foliage, changed veins, deleted flowers, or shifted silhouettes. No blur, rescale, global repaint, new geometry or added object. References2-3 only guide approved Daoist Q hand-painted finish; import none of their UI, text, figures, architecture or night lighting. The exact existing daylight foliage image must remain recognizable and coordinate-locked.'
(ZONE/'prompts'/f'{ident}.prompt.txt').write_text(prompt,encoding='utf-8')
q=ZONE/'qa/local-seams16-foliage-20261016';q.mkdir(exist_ok=True)
write(q/'audit.json',{'time':now(),'id':ident,'maximumNewBuiltinCalls':1,'sources':sources,'allocatedBy':'root follow-up; only third issue, first two outcomes retained','state':'prepared','selectionWritten':False,'progressWritten':False,'sharedGitMutated':False})
print(prompt)
