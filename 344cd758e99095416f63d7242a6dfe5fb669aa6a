"""Mechanical joining of existing generated raster patches, never creative art generation.
Keeps native pixel dimensions. Records any subpixel resampling and local colour matching.
Not a substitute for regeneration when scene objects or large geometry disagree.
"""
import cv2
import numpy as np
def registered_join(context, native_patch, mask, *, edges=("left","right","top","bottom"), max_shift=8.0, flow_inner=300.0, flow_full=120.0, tone_inner=330.0, tone_full=150.0, match_tone=True):
    assert context.shape==native_patch.shape and context.dtype==native_patch.dtype==np.uint8
    h,w=context.shape[:2];assert mask.shape==(h,w) and mask.dtype==np.uint8
    yy,xx=np.mgrid[:h,:w].astype(np.float32)
    ds={"left":xx,"right":w-1-xx,"top":yy,"bottom":h-1-yy}
    distance=np.minimum.reduce([ds[e] for e in edges])
    def taper(inner,full):
        assert inner>full>=0
        weight=np.clip((inner-distance)/(inner-full),0,1)
        return weight*weight*(3-2*weight)
    flow=cv2.calcOpticalFlowFarneback(cv2.cvtColor(context,cv2.COLOR_RGB2GRAY),cv2.cvtColor(native_patch,cv2.COLOR_RGB2GRAY),None,0.5,4,51,5,7,1.5,0)
    flow=np.clip(cv2.GaussianBlur(flow,(0,0),5),-max_shift,max_shift)*taper(flow_inner,flow_full)[:,:,None]
    aligned=cv2.remap(native_patch,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    correction=np.zeros_like(aligned,dtype=np.float32)
    if match_tone:
        correction=np.clip(cv2.GaussianBlur(context.astype(np.float32)-aligned.astype(np.float32),(0,0),24),-18,18)*taper(tone_inner,tone_full)[:,:,None]
    matched=np.clip(np.rint(aligned.astype(np.float32)+correction),0,255).astype(np.uint8)
    alpha=mask.astype(np.uint32)[:,:,None]
    result=((context.astype(np.uint32)*(255-alpha)+matched.astype(np.uint32)*alpha+127)//255).astype(np.uint8)
    assert np.array_equal(result[mask==0],context[mask==0])
    interior=(distance>=max(flow_inner,tone_inner)) & (mask==255)
    assert np.array_equal(result[interior],native_patch[interior])
    report={"kind":"mechanical_generated_patch_registration","sourceResampling":"subpixel geometric registration, native dimensions retained","nativePixels":[w,h],"outputPixels":[w,h],"sourceUpscaledTo4K":False,"underlyingArtworkBlurred":False,"maximumAllowedShiftPixels":max_shift,"actualMaxShiftXY":np.abs(flow).max(axis=(0,1)).tolist(),"localColorMatching":match_tone,"maxLocalColorCorrectionRGB":np.abs(correction).max(axis=(0,1)).tolist(),"edges":list(edges),"flowInner":flow_inner,"flowFull":flow_full,"toneInner":tone_inner,"toneFull":tone_full,"zeroMaskPixelsUnchanged":True,"nativeInteriorPixelsUnchanged":True,"preservedInteriorPixelCount":int(interior.sum()),"visualAcceptanceRequiresInspection":True}
    return result,flow,correction,report
