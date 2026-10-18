from native_work import *
import sys
p=ZONE/'prompts'/f'{sys.argv[1]}.inputs.json';d=read(p);assert len(d)==5
d=[d[0],d[1],d[2],{'file':(ZONE/'guides/r03c09-context-layout-only-20261016.png').as_posix(),'sha256':sha(ZONE/'guides/r03c09-context-layout-only-20261016.png'),'role':'enlarged original-layout context ONLY; no native art pixels'},d[4]]
write(p,d)

