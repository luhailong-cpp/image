exec((__import__('pathlib').Path(__file__).parent/'measure.py').read_text(encoding='utf-8'))
def px(im,y,ws):
 a=im[max(0,y-4):y+5].astype(float).mean((0,2));a=cv2.GaussianBlur(a[None,:],(0,0),1.3)[0];g=np.gradient(a)
 return [int(l+np.argmax(g[l:r]*sgn)) for l,r,sgn in ws]
print('horizontal')
for y in [480,520,540,560,640,820,860,900,920,960]: print(y,px(target,y,[(230,305,-1),(265,325,1),(460,510,-1)]),px(raw,y,[(230,305,-1),(265,325,1),(460,510,-1)]))
