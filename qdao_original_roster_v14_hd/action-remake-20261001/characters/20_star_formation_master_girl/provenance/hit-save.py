"""Save unchanged host hit images and exact call evidence in this character only."""
import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    assert path.resolve().is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def selection():
    frames=[]
    for number in range(1,7):
        version=2 if (ROOT/f'generation/hit/E/{number:02d}-v2.png').exists() else 1
        image=ROOT/f'generation/hit/E/{number:02d}-v{version}.png'
        sidecar=image.with_name(image.name+'.generation.json')
        if image.exists() and sidecar.exists():
            meta=json.loads(sidecar.read_text(encoding='utf-8-sig'))
            assert meta['sha256']==sha(image)
            frames.append({'action':'hit','direction':'E','frame':number,'source':image.relative_to(ROOT).as_posix(),'generationRecord':sidecar.relative_to(ROOT).as_posix(),'sourceSha256':sha(image),'status':'candidate','visualReview':'static_checked_candidate','dynamicReview':'not_verified'})
    write(ROOT/'hit-selection.json',{'schema':1,'character':ROOT.name,'exportTransform':{'size':[922,922],'offset':[51,40],'pivot':[512,922]},'scope':'hit/E only; parent merges explicitly into global selection','expectedFrames':6,'availableFrames':len(frames),'dynamicReview':'not_verified','frames':frames})

parser=argparse.ArgumentParser()
parser.add_argument('--frame',type=int,required=True)
parser.add_argument('--version',type=int,default=1,choices=(1,2))
parser.add_argument('--receipt',required=True)
parser.add_argument('--review',default='')
args=parser.parse_args()
assert args.frame in (1,2,4,5,6)
receipt_path=(ROOT/args.receipt).resolve()
assert receipt_path.is_relative_to(ROOT/'provenance')
receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig'))
config=json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig'))
receipt['recordedAt']=datetime.now(ZoneInfo('America/New_York')).isoformat()
receipt['configSnapshot']={k:config[k] for k in ['model','quality','builtin_product','verified_on','sources']}
write(receipt_path,receipt)
if receipt['status']!='succeeded':
    selection()
    print(json.dumps({'status':'failed','error':receipt.get('rawError'),'record':str(receipt_path)},ensure_ascii=False))
    raise SystemExit(0)
source=Path(receipt['hostOutput'])
dest=ROOT/f'generation/hit/E/{args.frame:02d}-v{args.version}.png'
assert not dest.exists(), 'Refusing to overwrite existing hit image'
dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,dest)
with Image.open(dest) as im:
    im.load()
    assert im.format=='PNG' and im.mode=='RGBA' and min(im.size)>=1024
    width,height=im.size
    assert width==height
    alpha=im.getchannel('A')
    alpha_extrema=alpha.getextrema()
    bounds=alpha.point(lambda x:255 if x>=128 else 0).getbbox()
refs=receipt['submittedParameters']['referenced_image_paths']
roles=['受击E03主身份、相机、比例与画布基准','E向原idle身份、待机与持物','主要已确认画法与材质样板']
if len(refs)==4:
    roles=['本槽待修正图片，仅改变指定持臂及盘位']+roles
record={'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'generatedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'generatedAtMeaning':'本地接收并保存时间；工具未披露服务器生成时刻','width':width,'height':height,'format':'PNG','mode':'RGBA','tool':'image_gen__imagegen','route':'builtin','slot':{'action':'hit','direction':'E','frame':args.frame},'configSnapshot':receipt['configSnapshot'],'submittedParameters':receipt['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具无model/quality选择器且返回未披露；配置目标与提示词不是实际版本依据。','prompt':f'prompts/hit-E-{args.frame:02d}-v{args.version}.txt','references':[{'path':p,'role':role,'sha256':sha(Path(p))} for p,role in zip(refs,roles)],'evidence':{'receipt':receipt_path.relative_to(ROOT).as_posix(),'hostOutput':str(source),'returnedKeys':receipt['returnedKeys']},'review':{'status':'candidate','staticFindings':args.review,'openIssues':['本段以E03约y93%地面为同段构图基准，跨run锚点及本段连续性仍待动态检查。'],'dynamicAcceptance':False,'clientIntegration':'not_integrated'},'technicalValidation':{'alphaExtrema':list(alpha_extrema),'alpha128BoundsForInspectionOnly':list(bounds),'nativePixelsUnmodified':True,'sourceCopySha256Matches':sha(source)==sha(dest),'note':'alpha边界仅用于诊断，未按bbox裁切、缩放或贴地。'}}
record['promptSha256']=sha(ROOT/record['prompt'])
write(dest.with_name(dest.name+'.generation.json'),record)
selection()
print(json.dumps({'image':str(dest),'native':[width,height],'sha256':sha(dest),'alpha128Bounds':bounds},ensure_ascii=False,indent=2))
