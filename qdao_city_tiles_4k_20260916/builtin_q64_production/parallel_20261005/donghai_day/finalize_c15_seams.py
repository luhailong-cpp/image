"""Finish authorized east edge through the native halo and widen roof placement."""
from pathlib import Path
import sys,copy,uuid
import numpy as np
from PIL import Image
import integrate_c15_repairs as j
R=j.R;T=j.T;D=T/'repairs/approved-integration';P=T/'repairs/final-integration'
j.D=D;j.M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);j.Q=D/'qa';j.C=D/'candidate.png';j.EX=D/'extended-context.png';j.joint.MASKS=j.M
def build():
 assert '--color' in sys.argv
 assert j.sha(P/'candidate.png')=='d0b5a6339cf0fdb0b43701aa56eef39299bd5b221e299b85fa7176c07e20456d'
 m=j.load(P/'manifest.json');base=j.rgb(P/'candidate.png');extended=j.rgb(P/'extended-context.png');assert np.array_equal(extended[115:4211,115:4211],base)
 image=base.copy();sources=[]
 d=T/'repairs/root-finishing/roof';arr,e=j.valid_patch(d/'edited-native.png');meta=j.load(d/'input.png.generation.json');frozen=j.rgb(T/'repairs/consolidated/candidate.png');box=meta['sourceRectXYXY']
 assert j.raw(j.cut(frozen,box))==meta['rawSourceRGBSha256']
 j.insert(image,arr,box,64,'roof-full-end',rects=[[1840,0,2620,630]])
 e.update(sourceROIValidated=True,sourceRectXYXY=box,placementReason='extend correction through complete blue fascia end instead of ending mid-board');sources.append(e)
 extended[115:4211,115:4211]=image
 before_extended=extended.copy();d=T/'repairs/right-halo-finish';patch,e=j.valid_patch(d/'edited-native.png');meta=j.load(d/'input.png.generation.json');srcbox=meta['sourceRectInExtendedXYXY']
 assert j.sha(meta['source']['file'])==meta['source']['sha256'] and j.raw(j.cut(j.rgb(meta['source']['file']),srcbox))==meta['rawSourceRGBSha256']
 # Coordinates in extended 4326px image; right endpoint is entire native halo edge.
 rect=[3315,3015,4326,4025];local=[rect[0]-srcbox[0],rect[1]-srcbox[1],rect[2]-srcbox[0],rect[3]-srcbox[1]]
 old=j.cut(extended,rect).copy();piece=j.cut(patch,local);alpha=j.rect_alpha(old,piece,rect,96,'east-hull-through-halo',('right',));matched,correction=j.match_boundary_color(old,piece,alpha,'east-hull-through-halo')
 extended[rect[1]:rect[3],rect[0]:rect[2]]=j.a.blend(old,matched,alpha)
 full=np.zeros((4326,4326),np.uint8);full[rect[1]:rect[3],rect[0]:rect[2]]=alpha
 assert np.array_equal(extended[full==0],before_extended[full==0])
 mask=j.save(j.M/'east-hull-through-halo-alpha.png',Image.fromarray(alpha));e.update(sourceROIValidated=True,sourceRectInExtendedXYXY=srcbox,sourceRectInTileAndRightHaloXYXY=meta['sourceRectInTileAndRightHaloXYXY']);sources.append(e)
 j.INSERTIONS.append({'id':'east-hull-through-halo','rectInExtendedXYXY':rect,'rectInTileAndHaloXYXY':[x-115 for x in rect],'edgeSearchPixels':96,'rightEdgeFullToNativeHalo':True,'alpha':mask,'localBoundaryColorMatch':correction,'exactOriginalAtAlphaZero':True,'changeReason':'correct actual stepped hull/waterline through unbound east boundary and synchronize 115px halo'})
 image=extended[115:4211,115:4211].copy();assert np.array_equal(image[:,:128],base[:,:128])
 currentmask=np.maximum(j.GLOBAL_MASK,full[115:4211,115:4211]);assert np.array_equal(image[currentmask==0],base[currentmask==0])
 previousmask=j.rgb(m['unionMask']['file'])[:,:,0];union=np.maximum(previousmask,currentmask)
 candidate=j.save(j.C,Image.fromarray(image));exinfo=j.save(j.EX,Image.fromarray(extended));unioninfo=j.save(j.M/'all-insertions-union.png',Image.fromarray(union))
 east_box=[3968,0,4096,4096];halo_box=[4211,115,4326,4211]
 eastproof={'oldCoreEast128RGBSha256':j.raw(j.cut(base,east_box)),'newCoreEast128RGBSha256':j.raw(j.cut(image,east_box)),'oldRight115HaloRGBSha256':j.raw(j.cut(before_extended,halo_box)),'newRight115HaloRGBSha256':j.raw(j.cut(extended,halo_box)),'west128ExactlyPreserved':True,'changedCoreRectXYXY':[3200,2900,4096,3910],'changedHaloRectInExtendedXYXY':[4211,3015,4326,4025]}
 j.a.QA=j.Q/'assembly';west,_=j.a.checked_west();qa=j.a.write_qa(Image.fromarray(image),Image.fromarray(extended),west);extra=j.qa_extra(image)
 for name,b in [('east-hull-detail',[3350,3100,4211,3820]),('roof-full-end-detail',[1780,0,2675,700])]:
  x0,y0,x1,y1=b;info=j.save(j.Q/(name+'.png'),Image.fromarray(extended).crop((x0+115,y0+115,x1+115,y1+115)));extra.append(dict(info,sourceRectInTileAndHaloXYXY=b,nativePixelScale=1,resized=False,visualInspection='pending'))
 m.update(createdAtUtc=j.a.utc_now(),priorCandidate=j.ref(P/'candidate.png'),priorIntegrationManifest=j.ref(P/'manifest.json'),candidate=candidate,extendedContext=exinfo,unionMask=unioninfo,qa=qa,insertionQA=extra,visualReview='pending',westAndEast128ColumnsExactlyPreserved=False,west128ColumnsExactlyPreserved=True,eastBoundaryCorrection=eastproof,integrationTool=j.ref(Path(__file__)),sharedIntegrationTool=j.ref(R/'integrate_c15_repairs.py'))
 m['nativeRepairs']+=sources;m['seams']+=j.SEAMS;m['insertions']+=j.INSERTIONS
 j.js(D/'manifest.json',m);print(__import__('json').dumps({'candidate':candidate,'extendedContext':exinfo,'qa':str(j.Q),'eastBoundaryCorrection':eastproof}))
if __name__=='__main__':
 if '--commit' in sys.argv:j.commit()
 else:build()
