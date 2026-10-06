exec((__import__('pathlib').Path(__file__).parent/'measure.py').read_text(encoding='utf-8').split('rows={}')[0])
prod_tone=np.load(ROOT/'output/r09_c13/west4.colorCorrection.npy')
patch=raw[:,512:1254]
yy,xx=np.mgrid[:1254,:742].astype(np.float32)
def smoothstep(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def saveimg(path,a):Image.fromarray(np.uint8(np.clip(np.rint(a),0,255))).save(path)
basecrop=current[2842:4096,:627]
trials=[]
for name,x0,x1 in [('support590-615',590,615),('support570-610',570,610)]:
    anchor=np.median(lf[:,x0:x1],axis=1)
    anchor=cv2.GaussianBlur(anchor,(1,11),0)
    # Limit each sampled axis to12px; source native geometry only.
    anchor=np.clip(anchor,-12,12)
    field=np.repeat(anchor[:,None,:],742,axis=1)
    wx=1-smoothstep((xx-115)/100)
    wy=smoothstep((yy-850)/84)
    weight=wx*wy
    flow=prod+(field-prod)*weight[:,:,None]
    flow=np.clip(flow,-12,12)
    aligned=cv2.remap(patch,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    # Native left-only color residual: the old image is the sole reference.
    support_raw=cv2.remap(raw,np.repeat(np.arange(627,dtype=np.float32)[None,:],1254,axis=0)+lf[:,:,0],np.repeat(np.arange(1254,dtype=np.float32)[:,None],627,axis=1)+lf[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    residual=cv2.GaussianBlur(left.astype(np.float32)-support_raw.astype(np.float32),(0,0),8)
    tc=np.median(residual[:,x0:x1,:],axis=1);tc=cv2.GaussianBlur(tc,(1,17),0);tc=np.clip(tc,-12,12)
    tone=prod_tone+(np.repeat(tc[:,None,:],742,axis=1)-prod_tone)*weight[:,:,None]
    rendered=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
    # exact return: alpha zero outside new first100px and above local y850.
    alpha=(xx>=115).astype(np.float32)*wx*wy
    alpha=np.where(xx<195,alpha,np.minimum(alpha,1-smoothstep((xx-195)/20)))
    mask=np.uint8(np.rint(alpha*255))
    ctx=np.concatenate([left[:,-115:],basecrop],axis=1)
    mix=((ctx.astype(np.uint32)*(255-mask[:,:,None])+rendered.astype(np.uint32)*mask[:,:,None]+127)//255).astype(np.uint8)
    assert np.array_equal(mix[:,:115],ctx[:,:115]);assert np.array_equal(mix[:,215:],ctx[:,215:])
    p=OUT/f'{name}-trial.png';saveimg(p,mix)
    saveimg(OUT/f'{name}-mask.png',mask)
    np.save(OUT/f'{name}-flow.npy',flow);np.save(OUT/f'{name}-tone.npy',tone)
    endpoint=np.concatenate([old[3776:4096,3936:4096],mix[934:1254,115:615]],axis=1)
    saveimg(OUT/f'{name}-endpoint.png',endpoint)
    saveimg(OUT/f'{name}-join-native.png',np.concatenate([left[934:,427:],mix[934:,115:315]],axis=1))
    trials.append(dict(name=name,oldSupportColumns=[x0,x1],newTileChangedRectXYWH=[0,3692,100,404],maxAllowedPerAxis=12,actualMaxFlowXY=np.abs(flow).max(axis=(0,1)).tolist(),actualMaxVector=float(np.linalg.norm(flow,axis=2).max()),toneMaxRGB=np.abs(tone).max(axis=(0,1)).tolist(),oldNeighborUnchanged=True,newTileX100OnwardUnchanged=True,flowFile=str(OUT/f'{name}-flow.npy'),flowSha256=sha(OUT/f'{name}-flow.npy'),toneFile=str(OUT/f'{name}-tone.npy'),toneSha256=sha(OUT/f'{name}-tone.npy'),maskFile=str(OUT/f'{name}-mask.png'),maskSha256=sha(OUT/f'{name}-mask.png'),trialFile=str(p),trialSha256=sha(p),resampling='cv2.INTER_CUBIC native dimensions retained; no source enlargement',isProduction=False))
(OUT/'trial-records.json').write_text(json.dumps(dict(createdAt=datetime.now(timezone.utc).isoformat(),trials=trials,inputRawSha256=sha(rawfile),inputCurrentSha256=sha(currentfile),sourceOldSha256=sha(oldfile)),indent=2)+'\n',encoding='utf-8')
print(json.dumps(trials,indent=2))
