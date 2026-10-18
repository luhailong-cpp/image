from native_work import *
import sys,argparse
ident=sys.argv[1];neighbors=sys.argv[2:];assert ident.startswith('r05_c10_')
for suffix in ('.anchored-layout-only.png','.native-neighbors.png'):
 assert not (ZONE/'guides'/f'{ident}{suffix}').exists()
guide(argparse.Namespace(id=ident,neighbor=neighbors,base=None))
p=ZONE/'prompts'/f'{ident}.inputs.json';r=read(p);target=patch(ident)['coreWorldBox'];roles=[]
for n in neighbors:
 b=patch(n)['coreWorldBox'];roles.append('UPPER' if b[1]<target[1] else 'LOWER' if b[1]>target[1] else 'RIGHT' if b[0]>target[0] else 'LEFT')
r[1]['role']='native neighbor'+(' plate left-to-right: ' if len(neighbors)>1 else ' reference: ')+', '.join(roles)
ctx=ZONE/'guides/r05c10-original-context-20261016.png'
r[3]={'file':str(ctx),'sha256':sha(ctx),'role':'enlarged original-layout context only; NOT final native art'}
write(p,r);print(json.dumps({'id':ident,'roles':roles,'references':[x['file'] for x in r]}))

