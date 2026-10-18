from worker import *
d=B/'r12_c14'/'repairs'/'lower-timber-20261016-v01';src=Path('C:/Users/luyua/.codex/generated_images/01a1346c-f256-7660-bdc2-dd45a971f68b/exec-e17ceecc-949b-4e7a-9b98-9eb812fd2b32.png');dst=d/'native-v02.png'
assert not dst.exists();shutil.copy2(src,dst)
write(d/'native-v02.json',{'path':str(dst),'originalOutput':str(src),'sha256':sha(dst),'dimensions':list(Image.open(dst).size),'tool':'image_gen.imagegen','actualModel':None,'modelEvidence':'not returned','status':'saved_pending_integration_review','resized':False,'review':'Second repair eliminates join in source but changes lower-right board fill beyond requested rectangle; cannot assume perimeter matches.'})
print(str(dst))
