from native_work import *
from PIL import Image
import argparse
tid='r05_c10';sp=ZONE/f'selection-{tid}.json';assert not sp.exists()
write(sp,{'tileId':tid,'cores':[[None]*4 for _ in range(4)],'overlays':[],'formalAccepted':False,'pendingIssues':[],'updatedAtUtc':now()})
id='r05_c10_p01_04';guide(argparse.Namespace(id=id,neighbor=['r04_c10_p04_04','r05_c11_p01_01_v3'],base=None))
p=ZONE/'prompts'/f'{id}.inputs.json';r=read(p);r[1]['role']='native neighbor plate left=UPPER r04_c10_p04_04; right=RIGHT r05_c11_p01_01_v3';write(p,r)
source=Path(current_references()[0]['file']);ctx=ZONE/'guides/r05c10-original-context-20261016.png';assert not ctx.exists()
Image.open(source).crop((788,345,907,458)).resize((595,565),Image.Resampling.NEAREST).save(ctx)
write(ctx.with_suffix('.png.derivation.json'),{'source':str(source),'sha256':sha(source),'crop':[788,345,907,458],'displayResize':[595,565],'purpose':'original-layout-only context; never native art','finalArt':False})
print(json.dumps({'id':id,'context':str(ctx),'refs':r}))

