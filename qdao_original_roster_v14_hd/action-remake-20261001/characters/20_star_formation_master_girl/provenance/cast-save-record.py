from pathlib import Path
import json,sys,subprocess,hashlib
from PIL import Image
B=Path(__file__).resolve().parents[1]
idx,source,status,note=sys.argv[1:5]
stem='cast-E-'+idx+'-v1'
refs=json.loads((B/'provenance/cast-session.json').read_text(encoding='utf-8'))['refs']
dest='generation/cast/E/'+idx+'-v1.png'
subprocess.run([sys.executable,str(B/'tools/save_generation.py'),source,dest,'prompts/'+stem+'.txt',json.dumps(refs), '--status',status,'--note',note],check=True)
recpath=B/(dest+'.generation.json')
rec=json.loads(recpath.read_text(encoding='utf-8'))
rec['references']=[{'path':r,'role':role,'sha256':hashlib.sha256(Path(r).read_bytes()).hexdigest()} for r,role in zip(refs,['施法第10帧：比例相机身份根点与释放端姿态','E待机：回收端姿态与持物参考','主要已确认画法风格参考'])]
rec['promptSha256']=hashlib.sha256((B/rec['prompt']).read_bytes()).hexdigest()
im=Image.open(B/dest)
rec['pixelValidation']={'alphaExtrema':im.getchannel('A').getextrema(),'alphaBBox':im.getchannel('A').getbbox(),'nativeSize':list(im.size),'transformation':'原生PNG原样复制，无裁切或缩放','globalAnchorAcceptance':False}
receipt={'resultKeys':['image_url','output_hint'],'output_path':source,'actualModel':None,'actualQuality':None,'note':'内置回执显示原图；未披露实际版本或质量'}
receiptpath='provenance/'+stem+'-receipt.json'
(B/receiptpath).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rec['evidence']['receipt']=receiptpath
recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selpath=B/'cast-selection.json'
sel=json.loads(selpath.read_text(encoding='utf-8')) if selpath.exists() else {'action':'cast','direction':'E','dynamicAcceptance':False,'frames':{}}
sel['frames'][idx]={'source':dest,'generationRecord':dest+'.generation.json','review':rec['review'],'sha256':rec['sha256']}
selpath.write_text(json.dumps(sel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

