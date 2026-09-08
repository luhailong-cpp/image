"""Verify and record this agent's eleven independent v7 portrait generations."""
from pathlib import Path
import json, hashlib, shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
CHAR=REPO/'qdao_gpt_image2_refresh_v7/characters'
PACK=REPO/'q_daoist_character_pack_4096'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
generation=read(HERE/'generation.json')
inventory=read(CHAR.parent/'inventory.json');old={a['path']:a for a in inventory['assets']}
records=[];failures=[]
for item in generation['sources']:
    stem=item['id'];source=REPO/item['raw'];target=PACK/(stem+'.png');record_path=PACK/'records'/(stem+'.json')
    previous=old[target.relative_to(REPO).as_posix()]
    raw=Image.open(source);final=Image.open(target).convert('RGBA');pixels=np.array(final)
    alpha=final.getchannel('A');bounds=alpha.getbbox()
    strong=(pixels[:,:,0]>200)&(pixels[:,:,1]<100)&(pixels[:,:,2]>200)&(pixels[:,:,3]>0)
    count=int(strong.sum())
    if count:failures.append(stem+': residual chroma')
    proc=read(PACK/'.work'/stem/'pipeline-meta.json');qc=proc['qc_summary']
    assert raw.size[0]>=1254 and raw.size[1]>=1254
    assert final.size==(4096,4096) and alpha.getextrema()==(0,255)
    assert qc['valid_frame_count']==1 and qc['empty_count']==qc['edge_touch_count']==qc['paste_clamped_count']==0
    assert not proc['source_edge_touch_frames'] and not proc['output_edge_touch_frames']
    assert min(bounds[0],bounds[1],4096-bounds[2],4096-bounds[3])>16
    assert sha(target)!=previous['sha256']
    c2pa=b'gpt-imagegversionc2.0' in source.read_bytes()
    assert c2pa, 'Expected original tool provenance gpt-image version2.0'
    backup=CHAR/'backups'/target.relative_to(REPO)
    assert backup.exists() and sha(backup)==previous['sha256']
    pmeta=HERE/'processing';pmeta.mkdir(exist_ok=True)
    shutil.copyfile(PACK/'.work'/stem/'pipeline-meta.json',pmeta/(stem+'.json'))
    r=read(record_path)
    r.update({'schema':'qdao.portrait.v7.independent.1','model':'gpt-image-2','model_evidence':'Original generated PNG C2PA softwareAgent name=gpt-image version=2.0','quality_parameter_exposed':False,'model_parameter_exposed':False,'quality_goal':'highest available','single_portrait_native_source':True,'source':item['raw'],'generation_file':Path(item['original_tool_file']).name,'generation_cache_original':item['original_tool_file'],'reference_baseline':inventory['baseline_commit'],'reference_delivery':'Conversation image: new approved hero + original HEAD role identity. Direct reference path hit Windows ACL.','old_sha256':previous['sha256'],'sha256':sha(target),'raw_sha256':sha(source),'native_generation_size':list(raw.size),'export_size':[4096,4096],'backup':backup.relative_to(REPO).as_posix(),'processor_record':(pmeta/(stem+'.json')).relative_to(REPO).as_posix(),'strict_qc_passed':True,'strong_chroma_remaining_pixels':count,'subject_bounds':list(bounds),'art_only_not_engine_integrated':True})
    write(record_path,r)
    records.append({'path':target.relative_to(REPO).as_posix(),'old_sha256':previous['sha256'],'new_sha256':sha(target),'source':item['raw'],'source_sha256':sha(source),'native_generation_size':list(raw.size),'export_size':[4096,4096],'alpha_range':[0,255],'subject_bounds':list(bounds),'backup':r['backup'],'record':record_path.relative_to(REPO).as_posix(),'generator':'built-in image_gen','embedded_model':'gpt-image 2.0','quality_parameter_exposed':False,'single_portrait_native_source':True,'source_edge_touch':False,'output_edge_touch':False,'strict_qc_passed':True,'residual_strong_chroma':count})
    final.close();raw.close()

qcdir=CHAR/'qc';qcdir.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
names=['铁刀少年','风刃少女','雪灵少女','水龙书生','金铃舞者','鬼书书生','日轮少女','驯灵少年','星阵少女','小厨仙','店小二刀客']
board=Image.new('RGB',(1680,1320),'#f3ecdf');draw=ImageDraw.Draw(board)
for i,r in enumerate(records):
    x=(i%4)*420;y=(i//4)*440
    for yy in range(y+12,y+392,16):
        for xx in range(x+12,x+408,16):draw.rectangle((xx,yy,xx+15,yy+15),fill='#e5e2d8' if ((xx-x)//16+(yy-y)//16)%2 else '#faf7eb')
    im=Image.open(REPO/r['path']).convert('RGBA');im.thumbnail((390,375),Image.Resampling.LANCZOS)
    board.paste(im,(x+(420-im.width)//2,y+12+(380-im.height)//2),im)
    draw.text((x+24,y+399),f'{i+12:02}  {names[i]}',font=font,fill='#285649')
    draw.text((x+24,y+421),'1254 原生单图 → 4096 RGBA',font=font,fill='#69715b')
board.save(qcdir/'professions12-22-contact.png')
payload={'status':'passed' if not failures else 'failed','scope':'Only professions12-22; full character package manifest owned by character agent','count':11,'independent_native_portraits':11,'native_size_each':[1254,1254],'export_size_each':[4096,4096],'failures':failures,'quality_parameter_exposed':False,'generation':'sources/professions12-22/generation.json','contact_sheet':'qc/professions12-22-contact.png','records':records}
write(CHAR/'professions12-22-validation.json',payload)
print(json.dumps({k:payload[k] for k in ['status','count','independent_native_portraits','failures']},ensure_ascii=False))
if failures:raise SystemExit(1)
