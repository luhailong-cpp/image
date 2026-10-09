import helper as h
from PIL import Image
import numpy as np
R=h.ROOT;p=h.p;B=R.parent;state=p.read(R/'evidence/boundary-state.json');old=state['north'];f=B/'r10_c15/repairs/external/proposals/r10_c14-west-proposal-v1.png'
assert p.sha(f)=='c2e3729e36725b13e530c074afbd17d639188d199b9a56d6f6be7144c78aa58e'
oldim=Image.open(old['source']).convert('RGB');im=Image.open(f).convert('RGB');assert np.array_equal(np.asarray(oldim)[3981:,:3469],np.asarray(im)[3981:,:3469])
anchor=R/'references/north-115-native-v2.png';im.crop((0,3981,4096,4096)).save(anchor);p.derived(anchor,[f],{'method':'native integer crop','boxLTRB':[0,3981,4096,4096]})
canvas=Image.open(R/'references/layout-canvas-only.png').convert('RGB');canvas.paste(Image.open(anchor),(115,0));c=R/'references/layout-canvas-north-v2-only.png';canvas.save(c);p.derived(c,[R/'references/layout-canvas-only.png',anchor],{'method':'guide-only native115 anchor update, no final art'})
guide=R/'guides/p14-north-v2.png';canvas.crop((3072,0,4326,1254)).save(guide);p.derived(guide,[c],{'method':'integer guide crop; never final pixels','boxLTRB':[3072,0,4326,1254]})
state['north']={'source':str(f),'sha256':p.sha(f),'anchor':str(anchor),'anchorSha256':p.sha(anchor),'stable':True,'confirmation':'fabric_repairs froze west proposal bottom115; onlyx3681..4095 modified; p11..p13 north context unchanged','prior':old};state.setdefault('guideOverrides',{})['p14']=str(guide);p.write(R/'evidence/boundary-state.json',state)
print('North frozen for p14, previous p11..13 anchors unchanged')
