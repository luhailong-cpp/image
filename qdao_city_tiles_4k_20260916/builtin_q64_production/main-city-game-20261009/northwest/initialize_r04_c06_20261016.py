from pathlib import Path
import json,hashlib
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest');T=Z/'r04_c06';assert not T.exists();T.mkdir()
src=(Z/'r05_c08/workflow_20261016.py').read_text()
src=src.replace("TILE='r05_c08'","TILE='r04_c06'").replace("NEIGHBORS={'r05_c07':('r05_c07/candidate/r05_c07-candidate-localcut-e280bcf6d4f6.png','75374335df252505edbb301d18c17bca9434b8ac74852bdafa698eaba41f10ec')}","NEIGHBORS={'r05_c06':('r05_c06/candidate/r05_c06-candidate-minimum-error-03d4dd9f7332.png','beb936eca2c223bf30e9d34717d8fd0e2254ee06cc0e1e25e4835a4138f44e39')}").replace("'reviewer':'/root/continue_r07_c07'","'reviewer':'/root'")
(T/'workflow_20261016.py').write_text(src,encoding='utf-8')
(T/'allocation-and-start-20261016.json').write_text(json.dumps({'tile':'r04_c06','worker':'/root','authorization':'Existing user request to continue completing NW work; proceed along stable south final after concentrated near-complete repairs','priorDirectoryExisted':False,'priorNativeSources':0,'priorSelectedCores':0,'actualConflictFound':False,'splitReserved':False,'worldBox':[20480,12288,24576,16384],'nativePatchGeometry':[1254,1254],'coreCrop':[115,115,1139,1139],'southFinal':{'file':str(Z/'r05_c06/candidate/r05_c06-candidate-minimum-error-03d4dd9f7332.png'),'sha256':'beb936eca2c223bf30e9d34717d8fd0e2254ee06cc0e1e25e4835a4138f44e39','actuallyViewed':True,'internalQA':'passed33'},'layoutActuallyViewed':True,'guidePolicy':'exact same-world actual final/selected core anchors only; never unreviewed halo','eastNeighborInProgress':'r04_c07 owned by /root/resume_r08_audit_20261016; coordinate before right column generation','actualModel':None,'formalAccepted':False},indent=2),encoding='utf-8')
print(str(T))

