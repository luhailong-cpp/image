from repair import *
import numpy as np
out=R/'both-side';out.mkdir(exist_ok=True)
old=Image.open(BASE).convert('RGB');newfile=TASK/'tiles/r09_c13-raw-candidate.png';new=Image.open(newfile).convert('RGB')
sources=[R/'repair-v3.png']+[R/f's{i}-repair-v1.png' for i in [2,3,4]]
strip=Image.new('RGB',(1024,4096))
placements=[]
for i,p in enumerate(sources):
    im=Image.open(p).convert('RGB');strip.paste(im.crop((115,115,1139,1139)),(0,i*1024))
    placements.append({'source':str(p),'sourceSha256':sha(p),'sourceCropLTRB':[115,115,1139,1139],'destinationXY':[0,i*1024]})
sp=out/'joint-strip-native-v1.png';strip.save(sp)
derived(sp,sources,{'method':'native crop and assembly','nativeGlobalRectXYWH':[48640,32768,1024,4096],'placements':placements,'resampling':None,'status':'candidate_pending_outer_perimeter_and_internal_junction_QA'})
old.paste(strip.crop((0,0,512,4096)),(3584,0));new.paste(strip.crop((512,0,1024,4096)),(0,0))
cp=out/'c12-right-revised-candidate-v1.png';npth=out/'c13-left-revised-candidate-v1.png';old.save(cp);new.save(npth)
derived(cp,[BASE,sp],{'method':'native masked replacement into new derivative only','sourceCropLTRB':[0,0,512,4096],'destRectLTRB':[3584,0,4096,4096],'originalSourceUnchanged':True,'formalAccepted':False})
derived(npth,[newfile,sp],{'method':'native masked replacement into new derivative only','sourceCropLTRB':[512,0,1024,4096],'destRectLTRB':[0,0,512,4096],'formalAccepted':False})
mask=Image.new('L',(4096,4096),0);mask.paste(255,(3584,0,4096,4096));mask.save(out/'c12-mask.png');derived(out/'c12-mask.png',[cp],{'method':'exact binary mask','rectLTRB':[3584,0,4096,4096]})
mask=Image.new('L',(4096,4096),0);mask.paste(255,(0,0,512,4096));mask.save(out/'c13-mask.png');derived(out/'c13-mask.png',[npth],{'method':'exact binary mask','rectLTRB':[0,0,512,4096]})
wide=Image.new('RGB',(1536,4096));wide.paste(old.crop((3328,0,4096,4096)),(0,0));wide.paste(new.crop((0,0,768,4096)),(768,0))
wp=out/'joint-context-native-v1.png';wide.save(wp);derived(wp,[cp,npth],{'method':'native exact context assembly','globalOriginXY':[48384,32768]})
for seg in range(4):
    for label,x in [('left-outer',256),('shared',768),('right-outer',1280)]:
        box=(x-128,seg*1024,x+128,(seg+1)*1024);q=out/f'qa-{label}-s{seg+1}.png';wide.crop(box).transpose(Image.Transpose.ROTATE_90).save(q)
        derived(q,[wp],{'method':'native crop and90degree rotation','boxLTRB':box,'centerLineOriginalX':x})
for y in [1024,2048,3072]:
    q=out/f'qa-junction-y{y}.png';box=(128,y-160,1408,y+160);wide.crop(box).save(q);derived(q,[wp],{'method':'native crop','boxLTRB':box})
write(out/'proposal-v1.json',{'createdAt':now(),'status':'proposed_both_side_not_accepted','originalC12File':str(BASE),'originalC12Sha256':sha(BASE),'matchesHandoff':sha(BASE)==H['baselineCandidates'][-1]['sha256'],'newC12File':str(cp),'newC12Sha256':sha(cp),'newC13File':str(npth),'newC13Sha256':sha(npth),'jointStrip':str(sp),'c12Left3584ColumnsPixelIdentical':bool(np.array_equal(np.array(old)[:,:3584],np.array(Image.open(BASE).convert('RGB'))[:,:3584])),'c13Beyond512ColumnsPixelIdentical':bool(np.array_equal(np.array(new)[:,512:],np.array(Image.open(newfile).convert('RGB'))[:,512:])),'singleContinuousPixelSourceAcrossSharedEdge':True,'fields':None,'resampling':None,'sharedGlobalX':49152,'globalModifiedRectXYWH':[48640,32768,1024,4096],'formalAccepted':False,'next':'Inspect all12 outer/shared edge crops plus3 segment joints before finite perimeter correction.'})
