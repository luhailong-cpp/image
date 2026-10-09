from pathlib import Path
import json
N=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r09_c11')
s=(N/'assemble-joint-repair.py').read_text(encoding='utf-8-sig')
s=s.replace("D=N/'r03_c01-v1'; R=D/'joint-repair-v1'", "D=N/'r04_c01-v1'; R=D/'joint-repair-v2'")
s=s.replace('exec-9ec0d784-674b-4684-98b4-4bbeca7aa066.png','exec-309fed57-818b-43f2-98ac-8201a30cb675.png')
s=s.replace('box=[170,440,660,590]','box=[195,190,580,690]')
s=s.replace("'references':[ref(D/'join-v1/joined.png'),ref(Path(r'D:\\work\\image\\designs\\gameplay-ui\\04-guild.png'))]", "'references':[ref(Path(p)) for p in read(R/'request.json')['payload']['referenced_image_paths']]")
s=s.replace("'upstreamAdditionalModelCalls':1","'upstreamAdditionalModelCalls':2")
(N/'assemble-r04c01-repair.py').write_text(s,encoding='utf-8')
s=(N/'grid-finish.py').read_text(encoding='utf-8-sig').replace("O=D/'join-v1'","O=D/'join-v2'")
(N/'grid-finish-join-v2-standard.py').write_text(s,encoding='utf-8')
R1=N/'r04_c01-v1/joint-repair-v1'
src=Path(r'C:/Users/luyua/.codex/generated_images/01a10bad-0c92-7f93-8a5b-4ae4ec120204/exec-fcf63bd0-788c-4e3a-aab0-321792285ca3.png')
import hashlib, shutil
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
shutil.copy2(src,R1/'native.png')
rec={'file':str(R1/'native.png'),'sha256':sha(R1/'native.png'),'pixels':[1254,1254],'tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'request':str(R1/'request.json'),'receipt':str(R1/'tool-receipt.json'),'source':{'file':str(src),'sha256':sha(src)},'role':'First true AI cleanup; residual branch rejected and corrected by joint-repair-v2','formalAccepted':False}
(R1/'native.png.generation.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
