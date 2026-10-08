from pathlib import Path
import sys
sys.dont_write_bytecode=True
from PIL import Image
import helper as h
R=h.ROOT

def build():
    sources=[R/'native'/f'p{r}{c}.png' for r in range(1,5) for c in range(1,5)]
    assert all(p.exists() for p in sources),'All sixteen native detail patches are required'
    canvas=Image.new('RGB',(4096,4096))
    for i,p in enumerate(sources):
        im=Image.open(p).convert('RGB');assert im.size==(1254,1254)
        canvas.paste(im.crop((115,115,1139,1139)),((i%4)*1024,(i//4)*1024))
    dest=R/'tiles/r10_c13-candidate.png';canvas.save(dest)
    h.p.derived(dest,sources,{'method':'16 native 1024-square detail cores, integer hardcut, no resampling or feathering','sourceCoreBoxLTRB':[115,115,1139,1139],'formalAccepted':False})
    for axis in ['x','y']:
        for line in [1024,2048,3072]:
            board=Image.new('RGB',(1024,1024))
            for k in range(4):
                if axis=='x':
                    crop=canvas.crop((line-128,k*1024,line+128,(k+1)*1024)).transpose(Image.Transpose.ROTATE_90)
                else:crop=canvas.crop((k*1024,line-128,(k+1)*1024,line+128))
                board.paste(crop,(0,k*256))
            out=R/'qa'/f'internal-{axis}{line}-native.png';board.save(out);h.p.derived(out,[dest],{'method':'four native seam strips, vertically stacked; x seams rotated90 degrees','axis':axis,'line':line,'halfWidth':128,'resampling':None,'productionArt':False})
    board=Image.new('RGB',(960,960));boxes=[]
    for r,y in enumerate([1024,2048,3072]):
        for c,x in enumerate([1024,2048,3072]):
            box=(x-160,y-160,x+160,y+160);board.paste(canvas.crop(box),(c*320,r*320));boxes.append(box)
    out=R/'qa/nine-intersections-native.png';board.save(out);h.p.derived(out,[dest],{'method':'nine native320px intersection crops, 3x3 stack','sourceBoxesLTRB':boxes,'resampling':None})
    h.update('complete_native_pixel_candidate_pending_seam_qa')
    print(str(dest),h.p.sha(dest))

if __name__=='__main__':build()
