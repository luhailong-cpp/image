from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,hashlib,json,datetime,shutil,os

REPO=Path('E:/work/image')
ROOT=REPO/'qdao_original_roster_v13'
PACK=REPO/'q_daoist_character_pack_4096'
COMMIT='9adcf9291e4a867601868889a5965f3cd48630ba'
BASE=ROOT/'baseline'/'q_daoist_character_pack_4096'
PREFIX='q_daoist_character_pack_4096/'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args])
def safe(p,root):
    p=Path(os.path.abspath(p))
    for x in (p,*p.parents):
        if x.is_symlink() or (hasattr(x,'is_junction') and x.is_junction()):raise RuntimeError('Refusing linked path '+str(x))
    if not p.resolve().is_relative_to(root.resolve()):raise RuntimeError('Out of scope '+str(p))
    return p

def main():
    safe(PACK,REPO);safe(ROOT,REPO)
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    history=safe(ROOT/'history'/'before-restore'/stamp,ROOT)
    backup=history/'q_daoist_character_pack_4096'
    originals=sorted(p for p in PACK.rglob('*') if p.is_file())
    before=[]
    for p in originals:
        safe(p,PACK);rel=p.relative_to(PACK);digest=sha(p);dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,dst)
        if sha(dst)!=digest or sha(p)!=digest:raise RuntimeError('Backup source changed while copying '+str(p))
        before.append({'path':rel.as_posix(),'sha256':digest,'bytes':p.stat().st_size,'backup':str(dst)})
    write(history/'inventory.json',{'created_utc':start,'source':str(PACK),'files':before,'file_count':len(before),'status':'backed_up_and_verified'})
    print(json.dumps({'step':'backup_complete','files':len(before),'backup':str(backup)},ensure_ascii=False),flush=True)
    tree=git('ls-tree','-r','-z',COMMIT,'--',PREFIX.rstrip('/')).split(b'\0')
    records=[]
    BASE.mkdir(parents=True,exist_ok=True)
    for entry in tree:
        if not entry:continue
        info,name=entry.split(b'\t',1);mode,kind,oid=info.decode().split();repo_path=name.decode('utf-8')
        if kind!='blob' or mode not in ('100644','100755'):raise RuntimeError('Unsupported tree entry '+repo_path)
        if not repo_path.startswith(PREFIX):raise RuntimeError('Unexpected git path')
        relative=repo_path[len(PREFIX):];out=safe(BASE/relative,BASE)
        data=git('cat-file','blob',oid)
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if blob!=oid:raise RuntimeError('Git blob verification failed '+relative)
        digest=hashlib.sha256(data).hexdigest()
        out.parent.mkdir(parents=True,exist_ok=True)
        if out.exists() and sha(out)!=digest:raise RuntimeError('Existing frozen baseline differs; preserving it '+str(out))
        if not out.exists():out.write_bytes(data)
        if sha(out)!=digest:raise RuntimeError('Baseline extraction SHA mismatch')
        records.append({'path':relative,'git_path':repo_path,'git_blob':oid,'git_commit':COMMIT,'sha256':digest,'bytes':len(data),'baseline_path':str(out)})
    print(json.dumps({'step':'baseline_extracted','files':len(records),'reference00':str(BASE/'00_reference_topright_boy_transparent_4096.png'),'reference01':str(BASE/'01_ice_sword_girl_transparent_4096.png')},ensure_ascii=False),flush=True)
    committed=json.loads((BASE/'manifest.json').read_text(encoding='utf-8-sig'))
    assets=committed['assets'];rows=[]
    for asset in assets:
        p=BASE/asset['path']
        with Image.open(p) as im:
            rgba=im.convert('RGBA');pixelsha=hashlib.sha256(rgba.tobytes()).hexdigest();size=list(im.size);mode=im.mode
        rows.append({'file':asset['path'],'name':asset['name'],'source_id':asset['id'],'character_id':asset['id'].removesuffix('_transparent_4096'),'baseline_path':str(p),'restored_path':str(PACK/asset['path']),'source_commit':COMMIT,'sha256':sha(p),'git_manifest_sha256':asset['sha256'],'matches_git_manifest':sha(p)==asset['sha256'],'rgba_pixel_sha256':pixelsha,'size':size,'mode':mode})
    canonical=[r for r in rows if len(r['file'])>3 and r['file'][:2].isdigit()]
    if len(canonical)!=23 or {r['file'][:2] for r in canonical}!={f'{n:02}' for n in range(23)}:raise RuntimeError('Expected exactly00..22 canonical roles')
    hero=next(r for r in canonical if r['file'].startswith('00_'))
    aliases=[]
    for r in rows:
        if r in canonical:continue
        match=next((c for c in canonical if c['rgba_pixel_sha256']==r['rgba_pixel_sha256']),None)
        if not match:raise RuntimeError('Extra reference is distinct and must not silently become an alias')
        aliases.append({**r,'alias_of':match['character_id'],'same_file_sha256':r['sha256']==match['sha256'],'same_rgba_pixels':True})
    # All source bytes are frozen and backups verified before any original-path write.
    restored=[]
    old={r['path']:r for r in before}
    for row in records:
        target=safe(PACK/row['path'],PACK);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(BASE/row['path'],target)
        if sha(target)!=row['sha256']:raise RuntimeError('Restored SHA mismatch '+row['path'])
        restored.append({**row,'restored_path':str(target),'previous_sha256':old.get(row['path'],{}).get('sha256'),'changed':old.get(row['path'],{}).get('sha256')!=row['sha256']})
    selected={r['path'] for r in records}
    retained=[r for r in before if r['path'] not in selected]
    if not all((PACK/r['path']).is_file() and sha(PACK/r['path'])==r['sha256'] for r in retained):raise RuntimeError('A nonselected current file changed')
    inventory={'schema':'qdao-original-roster-v13/inventory-v1','created_utc':start,'source_commit':COMMIT,'source_package':'q_daoist_character_pack_4096','baseline_directory':str(BASE),'restored_directory':str(PACK),'unique_character_count':23,'physical_portrait_file_count':24,'characters':canonical,'aliases':aliases,'git_manifest_sha256':sha(BASE/'manifest.json'),'all_pngs_match_commit_manifest':all(r['matches_git_manifest'] for r in rows),'animation_status':'not_complete; newly authored animation work lives in candidate/<character_id>/; restoring static portraits does not create walk or idle frames','output_spec':{'walk_frames_per_direction':16,'directions':['N','NE','E','SE','S','SW','W','NW'],'frame_duration_ms':30,'cycle_duration_ms':480}}
    write(ROOT/'inventory.json',inventory)
    write(ROOT/'baseline'/'git-extraction-manifest.json',{'source_commit':COMMIT,'package':PREFIX.rstrip('/'),'created_utc':start,'file_count':len(records),'files':records,'git_blob_bytes_verified':True})
    restoration={'status':'restored_static_pack','source_commit':COMMIT,'created_utc':start,'backup_directory':str(backup),'backup_inventory':str(history/'inventory.json'),'restored_count':len(restored),'restored_files':restored,'untouched_current_only_count':len(retained),'untouched_current_only_files':retained,'png_count':24,'unique_characters':23,'animation_completed':False,'game_resources_modified':False,'git_checkout_reset_or_clean_used':False}
    write(ROOT/'restoration.json',restoration)
    write(history/'restoration-receipt.json',restoration)
    # Presentation-only contact sheet: uniform resampling of complete 4096 square canvases.
    fontpath='C:/Windows/Fonts/msyh.ttc'
    font=ImageFont.truetype(fontpath,20);small=ImageFont.truetype(fontpath,15);title=ImageFont.truetype(fontpath,30)
    columns=6;cw=252;ch=298;top=125;margin=25;width=columns*cw+margin*2;height=4*ch+top+20
    board=Image.new('RGB',(width,height),(24,37,39));draw=ImageDraw.Draw(board)
    draw.text((margin,20),'指定原版角色 · 23 人静态基线',(237,228,194),font=title)
    draw.text((margin,65),'来源：9adcf9291e4a867601868889a5965f3cd48630ba · 2026-09-06 · 原图完整画布等比展示',(177,201,197),font=small)
    draw.text((margin,91),'00 为金发带道童，01–22 为职业角色；额外道童文件与 00 像素相同，仅记作别名。尚未完成 16 帧动画。',(177,201,197),font=small)
    for i,row in enumerate(sorted(canonical,key=lambda r:r['file'])):
        col=i%columns;line=i//columns;x=margin+col*cw;y=top+line*ch
        draw.rounded_rectangle((x,y,x+cw-10,y+ch-10),radius=7,fill=(44,59,59),outline=(66,87,83))
        with Image.open(row['baseline_path']) as im:
            thumb=im.convert('RGBA').resize((228,228),Image.Resampling.LANCZOS)
            board.paste(thumb,(x+7,y+8),thumb)
        draw.text((x+12,y+241),row['file'][:2]+'  '+row['name'],(239,224,186),font=font)
        draw.text((x+12,y+269),row['sha256'][:16],(168,190,184),font=small)
    overview=ROOT/'old-style-overview.jpg';board.save(overview,quality=94)
    inventory['overview']={'path':str(overview),'sha256':sha(overview),'method':'full4096 square canvas uniform LANCZOS layout only; no synthesized or altered poses'}
    write(ROOT/'inventory.json',inventory)
    readme='''# 指定原版角色恢复与 16 帧动画工作区\n\n本次按用户明确指定的提交 `'''+COMMIT+'''` 恢复 `q_daoist_character_pack_4096`。原目录全部当前文件已先备份，再仅覆盖该提交中的角色包文件；没有回滚整个 Git 仓库、删除新增文件或改写客户端资源。\n\n- 冻结原包：`baseline/q_daoist_character_pack_4096/`，保留指定提交的全部原字节。\n- 已恢复原路径：`E:/work/image/q_daoist_character_pack_4096/`。原 README 与原工具也按提交恢复。\n- 恢复前完整备份：`'''+str(backup)+'''`。\n- [逐文件恢复记录](restoration.json)记录原 SHA、恢复后 SHA 和保留未动的新文件。\n- [基线清单](baseline/git-extraction-manifest.json)记录每个 Git blob 与 SHA-256。\n- [23 人角色清单](inventory.json)列出 00–22 的准确源路径、SHA 和正式 ID。24 个 PNG 中两张道童参考逐像素相同，额外文件只记作 00 的 alias。\n- [原版总览](old-style-overview.jpg)只对完整原图等比排版，未重新设计人物。\n\n新动画独立写入 `candidate/<character_id>/`；参考图、生成过程与记录位于本工作区 `references/`、`generation/` 和各候选目录。目标为八方向、每向 16 帧、30ms/帧、480ms 周期。静态原图恢复已完成，不能据此声称新行走、独立站立或游戏接入完成；这些由主任务继续逐角色制作并验证。\n'''
    readme_path=ROOT/'README.md'
    if readme_path.exists():
        previous=history/'previous-new-root-README.md';shutil.copy2(readme_path,previous)
        readme+='\n恢复之前本新工作区的 README 已保存在 `'+str(previous)+'`。\n'
    readme_path.write_text(readme,encoding='utf-8')
    print(json.dumps({'status':'restored_static_pack','source_commit':COMMIT,'backup':str(backup),'restored_files':len(restored),'unique_characters':23,'portrait_aliases':len(aliases),'all_pngs_match_commit_manifest':inventory['all_pngs_match_commit_manifest'],'inventory':str(ROOT/'inventory.json'),'overview':str(overview),'reference00':hero['baseline_path'],'reference01':next(r['baseline_path'] for r in canonical if r['file'].startswith('01_')),'animation_completed':False},ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
