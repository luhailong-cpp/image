from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import production as p

root=p.ROOT
def run():
    patch_ids=[f'p{r}{c}' for r in range(1,5) for c in range(1,5)]
    found={n:root/'native'/(n+'.png') for n in patch_ids if (root/'native'/(n+'.png')).exists() and (root/'native'/(n+'.png.generation.json')).exists()}
    im=Image.new('RGB',(4096,4096),(40,46,51));draw=ImageDraw.Draw(im)
    prov=[]
    for r in range(4):
        for c in range(4):
            n=f'p{r+1}{c+1}'
            if n in found:
                patch=Image.open(found[n]).convert('RGB');assert patch.size==(1254,1254),(n,patch.size)
                im.paste(patch.crop((115,115,1139,1139)),(c*1024,r*1024))
                prov.append({'file':str(found[n]),'sha256':p.sha(found[n]),'generationRecord':str(found[n])+'.generation.json','sourceCropLTRB':[115,115,1139,1139],'destinationXY':[c*1024,r*1024]})
            else:
                draw.text((c*1024+400,r*1024+500),'MISSING '+n,fill=(200,200,200),font_size=36)
    preview=root/'current-preview.png';im.resize((1254,1254),Image.Resampling.LANCZOS).save(preview)
    p.write(str(preview)+'.generation.json',{'file':str(preview),'sha256':p.sha(preview),'operation':'preview downsample of current native cores, dark missing cells are not production pixels','derivedFrom':prov,'nativeDetailPatchesPresent':len(found),'formalAccepted':False})
    prog=p.read(root/'progress.json');prog.update({'updatedAt':p.stamp(),'newNativeDetailPatches':len(found),'nativePatchesRequiredForCurrentTile':16,'newCompleteCandidateTiles':0,'currentPreview':str(preview),'status':'generating_native_details' if len(found)<16 else 'checking_native_seams'});p.write(root/'progress.json',prog)
    if len(found)==16:
        out=root/'tiles/r09_c13-raw-candidate.png';im.save(out)
        p.write(str(out)+'.generation.json',{'file':str(out),'sha256':p.sha(out),'createdAt':p.stamp(),'width':4096,'height':4096,'operation':'integer crop and paste of16 native1254 images; core1024; no resize or blend; pending seam QA','derivedFrom':prov,'globalPixelRectXYWH':[49152,32768,4096,4096],'formalAccepted':False})
        qa=root/'qa';qa.mkdir(exist_ok=True)
        crops=[]
        for axis in ['x','y']:
            for line in [1024,2048,3072]:
                for seg in range(4):
                    box=(line-160,seg*1024,line+160,(seg+1)*1024) if axis=='x' else (seg*1024,line-160,(seg+1)*1024,line+160)
                    fn=qa/f'{axis}{line}-s{seg+1}.png';crop=im.crop(box)
                    if axis=='x':crop=crop.transpose(Image.Transpose.ROTATE_90)
                    crop.save(fn);crops.append({'file':str(fn),'sha256':p.sha(fn),'source':str(out),'boxLTRB':box,'nativeScale':True,'viewed':False})
        for yy in [1024,2048,3072]:
            for xx in [1024,2048,3072]:
                fn=qa/f'junction-{xx}-{yy}.png';box=(xx-160,yy-160,xx+160,yy+160);im.crop(box).save(fn)
                crops.append({'file':str(fn),'sha256':p.sha(fn),'source':str(out),'boxLTRB':box,'nativeScale':True,'viewed':False})
        neighbor=Image.open(p.H['baselineCandidates'][-1]['file']).convert('RGB')
        for seg in range(4):
            joint=Image.new('RGB',(640,1024));joint.paste(neighbor.crop((3776,seg*1024,4096,(seg+1)*1024)),(0,0));joint.paste(im.crop((0,seg*1024,320,(seg+1)*1024)),(320,0))
            fn=qa/f'c12-c13-shared-s{seg+1}.png';joint.transpose(Image.Transpose.ROTATE_90).save(fn);crops.append({'file':str(fn),'sha256':p.sha(fn),'sources':[p.H['baselineCandidates'][-1]['file'],str(out)],'sharedGlobalX':49152,'globalYRange':[32768+seg*1024,32768+(seg+1)*1024],'nativeScale':True,'viewed':False})
        corner=Image.new('RGB',(640,640));corner.paste(neighbor.crop((3776,0,4096,320)),(0,0));corner.paste(im.crop((0,0,320,320)),(320,0));corner.paste(neighbor.crop((3776,3776,4096,4096)),(0,320));corner.paste(im.crop((0,3776,320,4096)),(320,320));corner.save(qa/'shared-edge-endpoints.png')
        for c in range(4):
            box=[(0,0,320,320),(3776,0,4096,320),(0,3776,320,4096),(3776,3776,4096,4096)][c];fn=qa/f'outer-corner-{c+1}.png';im.crop(box).save(fn);crops.append({'file':str(fn),'sha256':p.sha(fn),'source':str(out),'boxLTRB':box,'nativeScale':True,'viewed':False,'adjacentTilesMissing':True})
        p.write(qa/'index.json',{'tile':'r09_c13','rawCandidate':str(out),'rawCandidateSha256':p.sha(out),'crops':crops,'formalAccepted':False})
        errors=[]
        for r in range(4):
            for c in range(4):
                a=np.array(Image.open(found[f'p{r+1}{c+1}']).convert('RGB')).astype(float)
                for dr,dc in [(0,1),(1,0)]:
                    rr,cc=r+dr,c+dc
                    if rr>3 or cc>3:continue
                    b=np.array(Image.open(found[f'p{rr+1}{cc+1}']).convert('RGB')).astype(float)
                    aa,bb=(a[:,1024:],b[:,:230]) if dc else (a[1024:,:],b[:230,:])
                    errors.append({'a':f'p{r+1}{c+1}','b':f'p{rr+1}{cc+1}','overlapMAE':float(np.mean(np.abs(aa-bb))),'usage':'diagnostic only, not acceptance'})
        p.write(qa/'overlap-diagnostics.json',errors)
    print({'native':len(found),'new4K':0,'preview':str(preview)})
if __name__=='__main__':run()
