exec((__import__('pathlib').Path(__file__).parent/'measure.py').read_text(encoding='utf-8').split('rows={}')[0])
g0=grey(left).astype(float);g1=grey(raw).astype(float);g2=grey(current[2842:4096,:627]).astype(float)
bands=[(1080,1210),(1200,1250)]
profiles={}
for name,g,xs in [('old',g0,[560,580,600,610,620,626]),('raw',g1,[560,580,600,610,620,626,627,630,640]),('merged',g2,[0,1,5,10])]:
    data=[]
    for x in xs:
        out=dict(x=x)
        for j,(lo,hi)in enumerate(bands):
            vals=cv2.GaussianBlur(g[:,max(0,x-1):min(g.shape[1],x+2)].mean(axis=1).astype(np.float32),(1,5),0).ravel()
            gy=np.gradient(vals);center=int(np.argmin(vals[lo:hi]))+lo
            peaks=[]
            for p in range(lo+1,hi-1):
                if abs(gy[p])>=abs(gy[p-1]) and abs(gy[p])>=abs(gy[p+1]) and abs(gy[p])>3:peaks.append((p,round(float(gy[p]),2)))
            out[f'band{j}']=dict(darkestY=center,darkestValue=float(vals[center]),gradientPeaks=peaks)
        data.append(out)
    profiles[name]=data
# Compare only genuine LEFT half cropped feature blocks, integer offsets <=6, choosing the minimum-length within 0.01 of best NCC to avoid aperture ambiguity.
def grad(a):
    g=grey(a).astype(np.float32)
    return cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3),cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
rx,ry=grad(left);sx,sy=grad(raw);fits=[]
for box in [(475,925,610,1035),(475,1065,610,1175),(475,1135,610,1235),(550,1060,620,1240)]:
    x0,y0,x1,y1=box;ra=np.stack([rx[y0:y1,x0:x1],ry[y0:y1,x0:x1]],axis=-1).ravel();ra-=ra.mean();scores=[]
    for dy in range(-6,7):
        for dx in range(-6,7):
            sb=np.stack([sx[y0+dy:y1+dy,x0+dx:x1+dx],sy[y0+dy:y1+dy,x0+dx:x1+dx]],axis=-1).ravel();sb-=sb.mean()
            ncc=float(np.dot(ra,sb)/(np.linalg.norm(ra)*np.linalg.norm(sb)+1e-9));scores.append((ncc,dx,dy))
    scores.sort(reverse=True);stable=sorted([s for s in scores if s[0]>=scores[0][0]-.01],key=lambda s:s[1]*s[1]+s[2]*s[2])[0]
    fits.append(dict(box=list(box),best=scores[0],smallestEquivalentOffset=stable))
# y-varying one-dimensional left-support offset (mean of x450:600) has no contribution from erroneous new context.
result=dict(profileFeatures=profiles,boundedLeftGradientFits=fits,notes=['Offsets are source sampling dx/dy, not physical motion.','Feature gradient NCC near a single diagonal edge is aperture-ambiguous; smallest near-optimal shift is reported.'])
(OUT/'edge-measurement.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
