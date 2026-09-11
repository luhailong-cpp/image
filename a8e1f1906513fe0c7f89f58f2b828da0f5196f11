"""Selective exposure refinement, always applied to immutable original pixels.

User-approved local grading: linear-light highlight rolloff, neutral highlight
control, shadow protection and exact alpha/chroma preservation. No AI API calls.
"""
from __future__ import annotations
from io import BytesIO
import numpy as np
from PIL import Image, PngImagePlugin

VERSION = 'selective-exposure-1.0'
PRESETS = {
    'scene': dict(ev=.62, neutral_ev=.10, start=.055, end=.78),
    'screen': dict(ev=.52, neutral_ev=.09, start=.065, end=.80),
    'ui': dict(ev=.38, neutral_ev=.07, start=.12, end=.85),
    'ui_soft': dict(ev=.24, neutral_ev=.04, start=.16, end=.88),
    'character': dict(ev=.25, neutral_ev=.07, start=.16, end=.88),
    'item': dict(ev=.14, neutral_ev=.04, start=.22, end=.90),
    'cloud': dict(ev=.23, neutral_ev=.04, start=.16, end=.90),
    'preserve': dict(ev=0., neutral_ev=0., start=.20, end=.90),
}
SRGB = np.arange(256, dtype=np.float32) / 255
LINEAR = np.where(SRGB <= .04045, SRGB / 12.92, ((SRGB + .055) / 1.055) ** 2.4)
WEIGHTS = np.array([.2126, .7152, .0722], dtype=np.float32)

def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t*t*(3-2*t)

def grade_rgb(rgb, preset, protect_chroma=False):
    """Accept any uint8 array ending in three channels; preserve hue in linear RGB."""
    cfg = PRESETS[preset]
    if not cfg['ev']:
        return rgb.copy()
    linear = LINEAR[rgb]
    y = linear @ WEIGHTS
    span = (linear.max(axis=-1)-linear.min(axis=-1)) / np.maximum(linear.max(axis=-1), .001)
    neutral = 1-smooth(.10, .42, span)
    exposure = cfg['ev']*smooth(cfg['start'],cfg['end'],y)
    exposure += cfg['neutral_ev']*neutral*smooth(.55,.97,y)
    graded = linear * np.exp2(-exposure)[...,None]
    out = np.where(graded <= .0031308, 12.92*graded, 1.055*np.power(graded, 1/2.4)-.055)
    out = np.clip(np.rint(out*255),0,255).astype(np.uint8)
    # No channel can become brighter; no contrast clipping or raised black point.
    out = np.minimum(out,rgb)
    if protect_chroma:
        r,g,b = rgb[...,0].astype(np.int16),rgb[...,1].astype(np.int16),rgb[...,2].astype(np.int16)
        matte=(r>150)&(b>130)&(g<125)&(np.minimum(r,b)>g+45)
        out[matte]=rgb[matte]
    return out

def grade_image(im, preset, protect_chroma=False):
    if preset == 'preserve':
        return im.copy()
    if im.mode not in ('RGB','RGBA'):
        raise ValueError(f'Production raster mode needs explicit handling: {im.mode}')
    out = im.copy()
    # Strip processing keeps peak memory bounded on 10240px compatibility art.
    for top in range(0,im.height,192):
        box=(0,top,im.width,min(im.height,top+192))
        a=np.asarray(im.crop(box)).copy()
        rgb=a[...,:3].copy()
        revised=grade_rgb(rgb,preset,protect_chroma)
        if im.mode=='RGBA':
            revised[a[...,3]==0]=rgb[a[...,3]==0]
        a[...,:3]=revised
        out.paste(Image.fromarray(a),box)
    return out

def grade_png_bytes(data,preset,protect_chroma=False):
    if preset=='preserve':return data
    with Image.open(BytesIO(data)) as im:
        im.load()
        result=grade_image(im,preset,protect_chroma)
        if result.tobytes()==im.tobytes():return data
        meta=PngImagePlugin.PngInfo()
        # Edited pixels must not retain the original C2PA assertion as valid.
        for key,value in im.info.items():
            if isinstance(value,str) and key.lower() not in ('c2pa','jumb'):
                meta.add_text(key,value)
        meta.add_text('exposure_refinement',f'{VERSION}; preset={preset}; original retained in v8 backup')
        kwargs={'pnginfo':meta,'compress_level':6}
        for key in ('icc_profile','dpi','exif'):
            if key in im.info:kwargs[key]=im.info[key]
        buf=BytesIO();result.save(buf,format='PNG',**kwargs)
        return buf.getvalue()

def metrics(im):
    im=im.convert('RGBA');im.thumbnail((512,512),Image.Resampling.NEAREST)
    a=np.asarray(im);v=a[...,3]>16
    if not v.any():return {'visible_pixels':0}
    rgb=a[...,:3][v];y=(rgb.astype(np.float32)/255)@WEIGHTS
    return dict(mean=float(y.mean()),p90=float(np.quantile(y,.9)),p99=float(np.quantile(y,.99)),
                bright_fraction=float((y>.85).mean()),nearwhite_fraction=float(((rgb.min(1)>237)&(rgb.max(1)-rgb.min(1)<21)).mean()),
                visible_pixels=int(v.sum()))
