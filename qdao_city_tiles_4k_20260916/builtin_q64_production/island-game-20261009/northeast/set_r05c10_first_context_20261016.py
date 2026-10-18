from native_work import *
p=ZONE/'prompts/r05_c10_p01_04.inputs.json';d=read(p);q=ZONE/'guides/r05c10-original-context-20261016.png';d[3]={'file':q.as_posix(),'sha256':sha(q),'role':'original layout context ONLY; NOT native art'};write(p,d)

