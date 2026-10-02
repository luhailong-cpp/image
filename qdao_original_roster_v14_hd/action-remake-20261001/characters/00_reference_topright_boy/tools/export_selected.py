"""Export reviewed candidates with one fixed whole-canvas transform per direction.
No artwork, pose interpolation, mirroring, framewise fitting, or foot alignment.
"""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parents[2]/'combat-20260929'/'characters'/'00_reference_topright_boy'
RUN=ROOT.parents[2]/'run-correction-20260930'/'characters'/'00_reference_topright_boy'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    selections=[]
    for seq in read(ROOT/'review/combat-reviewed.json')['sequences']:
        for f in seq['frames']:
            selections.append({'action':seq['action'],'direction':seq['direction'],'frame':f['slot'],'source':f['sourcePath'],'record':f['generationRecordPath'],'status':f['decision'],'observation':f['observation']})
    for f in read(ROOT/'review/cast-selection.json')['frames']:
        if not f.get('source'):continue
        records=[e['path'] for e in f.get('sourceEvidence',[]) if e['kind']=='generation_record']
        selections.append({'action':'cast','direction':f['direction'],'frame':f['frame'],'source':f['source'],'record':records[0] if records else None,'status':f['status'],'observation':f['continuityConclusion'],'evidence':f.get('sourceEvidence',[])})
    p=RUN/'generation/E/01-v4.png'
    selections.append({'action':'run','direction':'E','frame':1,'source':str(p),'record':str(p)+'.generation.json','status':'candidate_static_reviewed_dynamic_pending','observation':'右腿前伸接地、近侧右臂后摆、远侧左手持葫芦；待完整循环及全局比例验收。'})
    for n in [4,9]:
        p=ROOT/f'generation/run/E/{n:02d}-v{2 if n==9 else 1}.png'
        if p.exists():selections.append({'action':'run','direction':'E','frame':n,'source':str(p),'record':str(p)+'.generation.json','status':'candidate_static_reviewed_dynamic_pending','observation':'本轮新生成独立原生姿态；待完整循环、比例及脚部相位验收。'})
    index={'schemaVersion':1,'character':'00_reference_topright_boy','status':'candidate_exports_not_runtime_approved','rootAnchor':[512,942],'frames':{}}
    manifest=[]
    for f in selections:
        src=Path(f['source']); meta=read(f['record']) if f.get('record') else {}
        with Image.open(src) as im:
            if im.mode!='RGBA' or im.size!=(1254,1254):raise ValueError(f'Unsupported native input {src}: {im.size} {im.mode}')
            # Preserve generated alpha; downsample whole canvas identically for all frames.
            tile=im.resize((901,901),Image.Resampling.LANCZOS)
        offset=(41,118) if f['direction']=='W' else (61,106)
        canvas=Image.new('RGBA',(1024,1024),(0,0,0,0));canvas.alpha_composite(tile,offset)
        key=f"{f['action']}/{f['direction']}/{f['frame']:02d}.png";dst=ROOT/'frames'/key;dst.parent.mkdir(parents=True,exist_ok=True);canvas.save(dst)
        source_evidence=f.get('record') or str(ROOT/'review/cast-selection.json')
        row={'file':'frames/'+key,'sha256':sha(dst),'width':1024,'height':1024,'mode':'RGBA','nativeSourceSize':[1254,1254],'derivedAt':datetime.now(timezone(timedelta(hours=-4))).isoformat(),'timezone':'America/New_York','route':'derived','tool':'Pillow whole canvas fixed transform','configSnapshot':meta.get('configSnapshot'),'actualModel':meta.get('actualModel'),'actualQuality':meta.get('actualQuality'),'unverifiedReason':meta.get('unverifiedReason','历史回执未披露实际model/quality，保留未知，不以本轮配置补写。'),'derivedFrom':{'file':str(src),'sha256':sha(src),'generationRecord':f.get('record'),'evidence':f.get('evidence',[])},'operation':{'kind':'uniform_whole_canvas_downsample_fixed_direction_offset','nativeCanvas':[1254,1254],'scaledCanvas':[901,901],'offset':list(offset),'alpha':'preserved','rootAnchor':[512,942],'framewiseFit':False,'mirrored':False,'interpolatedPose':False},'frameDurationMs':{'run':30,'hit':40,'attack':30,'cast':45}[f['action']],'visualStatus':f['status'],'observation':f['observation'],'sequenceVisualApproved':False,'clientIntegrated':False}
        write(Path(str(dst)+'.generation.json'),row)
        index['frames'][key]={'source_path':str(src),'source_kind':'single_frame','source_sha256':sha(src),'native_frame_size':[1254,1254],'evidence_path':source_evidence,'export_sha256':row['sha256'],'visual_status':f['status']}
        manifest.append(row)
    write(ROOT/'sources.json',index);write(ROOT/'manifest.json',{'status':'incomplete_candidate_exports','target':196,'candidateExports':len(manifest),'finalVisualApproved':0,'clientIntegrated':False,'frames':manifest})
    print(json.dumps({'exports':len(manifest),'missing':196-len(manifest),'visualApproved':0}))
if __name__=='__main__':main()
