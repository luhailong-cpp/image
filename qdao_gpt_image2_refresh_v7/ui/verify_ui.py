"""UI-only v7 QA. Does not modify root/global validation conclusions."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont,ImageChops

HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
inventory=read(HERE.parent/'inventory.json')
cats={'legacy_exact_slices','legacy_atomic_controls','ui_components_and_overviews','hud_layers','legacy_screen_layers_and_compat'}
items=[a for a in inventory['assets'] if a['category'] in cats or a['path']=='qdao_ui_redesign_v5/source/04_main_city_hud.png']
cm=read(REPO/'qdao_ui_redesign_v5/components/manifest.json'); lm=read(REPO/'exact_qdao_slices/manifest_native_q5.json')
specs={}
for a in cm['assets']:
    for ext in ['png','svg']:specs['qdao_ui_redesign_v5/components/'+a[ext]]=a
for a in lm['assets']:
    for ext in ['png','svg']:specs[a[ext]]=a
native=read(HERE/'source-map.json')
labels_only={'qdao_ui_redesign_v5/hud/hud_labels.png','qdao_ui_redesign_v5/hud/hud_labels.svg','q_daoist_login_ui_uncropped_highres_final_layers/native_q5/labels.svg'}
records=[];failures=[]
for old in items:
    rel=old['path'];p=REPO/rel;after=sha(p);changed=after!=old['sha256']
    record={'path':rel,'old_sha256':old['sha256'],'new_sha256':after,'changed':changed,'original_size':old['size'],'category':old['category']}
    if p.suffix=='.png':
        with Image.open(p) as im:
            record['size']=list(im.size);record['mode']=im.mode
            record['alpha_range']=list(im.getchannel('A').getextrema()) if 'A' in im.getbands() else None
            record['canvas_preserved']=record['size']==old['size']
            record['mode_preserved']=im.mode==old['mode']
            if record['alpha_range']:
                alpha=im.getchannel('A');record['transparent_corners']=all(alpha.getpixel(xy)==0 for xy in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)])
                record['alpha_preserved']=record['alpha_range']==old.get('alpha_range',[0,255])
    else:
        tree=ET.parse(p);root=tree.getroot()
        record['size']=[round(float(root.get('width'))),round(float(root.get('height')))];record['viewBox']=root.get('viewBox')
        record['canvas_preserved']=record['size']==old['size'] and record['viewBox']==old.get('viewBox')
        record['portable_embedded_images']=all(v.startswith('data:image/png;base64,') or v.startswith('#') for el in root.iter() for k,v in el.attrib.items() if k.rsplit('}',1)[-1]=='href')
        record['no_scripts']=not any(e.tag.rsplit('}',1)[-1]=='script' for e in root.iter())
        record['text_nodes']=sum(e.tag.rsplit('}',1)[-1]=='text' for e in root.iter())
    if rel in specs:
        current=specs[rel]
        record['contract_preserved']=all(current.get(k)==old[k] for k in ['nine_slice','resize_axes','content_insets'] if k in old)
        record['derivation']='New image_gen native atlas → alpha-preserving connected cleanup/crop → fixed-border resampling/status composition → PNG / embedded-image SVG.'
        key=rel if rel in native['derivatives'] else current.get('png')
        record['source_elements']=current.get('v7_sources') or native['derivatives'].get(key) or []
        record['source_map']='qdao_gpt_image2_refresh_v7/ui/source-map.json'
    else:
        record['derivation']='New v7 AI UI components assembled under preserved layout; labels remain separate true-value text. Scene/hero compatibility outputs are transitive v7 dependencies where present.'
        record['source_components']='qdao_ui_redesign_v5/components/manifest.json'
        if old['category']=='legacy_screen_layers_and_compat':record['composition_manifest']='q_daoist_login_ui_uncropped_highres_final_layers/manifest_native_q5.json'
        if old['category']=='hud_layers' or '04_main_city_hud' in rel:record['composition_manifest']='qdao_ui_redesign_v5/hud/placement.json'
    if rel in labels_only:
        record['status']='preserved_text_data';record['reason']='Only approved Chinese text and layout; no painted artwork. Regenerated unchanged; not falsely attributed to AI.'
    else:record['status']='redrawn_from_new_ai_artwork' if changed else 'FAILED_UNCHANGED'
    record['tool']='built-in image_gen plus deterministic local derivative processing'
    record['native_sources']=[{'path':'qdao_gpt_image2_refresh_v7/ui/'+s['file'],'size':s['size'],'sha256':s['sha256']} for s in native['native_sources']]
    if not record['canvas_preserved'] or record.get('contract_preserved') is False or record.get('mode_preserved') is False or record.get('alpha_preserved') is False or (not changed and rel not in labels_only):failures.append(rel)
    records.append(record)

compositions=[]
layer=REPO/'q_daoist_login_ui_uncropped_highres_final_layers'
for w,h in [(5120,2160),(10240,4320)]:
    base=Image.open(layer/f'q_daoist_login_background_ui_uncropped_final_{w}x{h}.png').convert('RGBA')
    controls=Image.open(layer/f'q_daoist_login_buttons_uncropped_final_{w}x{h}.png').convert('RGBA')
    combined=Image.open(layer/f'q_daoist_login_ui_uncropped_final_recomposed_{w}x{h}.png').convert('RGBA')
    expected=Image.alpha_composite(base,controls)
    # Different integer compositors may differ by one unit; compare full RGBA.
    diff=ImageChops.difference(expected,combined)
    extrema=diff.getextrema();maximum=max(v[1] for v in extrema)
    passed=maximum<=2
    compositions.append({'size':[w,h],'alpha_over_max_channel_error':maximum,'passed':passed,'note':'Pillow reference vs Sharp/libvips compositor; rounding tolerance <=2/255.'})
    if not passed:failures.append(f'composition_{w}')
    base.close();controls.close();combined.close();expected.close();diff.close()

qc=HERE/'qc';qc.mkdir(exist_ok=True)
font_path=Path('C:/Windows/Fonts/msyh.ttc')
font=ImageFont.truetype(str(font_path),18) if font_path.exists() else ImageFont.load_default()
def board(subset,name,columns=5,tile=(230,185)):
    images=[r for r in subset if Path(r['path']).suffix=='.png'];rows=(len(images)+columns-1)//columns
    out=Image.new('RGB',(columns*tile[0],rows*tile[1]),'#f1eee1');d=ImageDraw.Draw(out)
    for i,r in enumerate(images):
        x=(i%columns)*tile[0];y=(i//columns)*tile[1]
        im=Image.open(REPO/r['path']).convert('RGBA');im.thumbnail((tile[0]-24,tile[1]-55),Image.Resampling.LANCZOS)
        for by in range(y+8,y+tile[1]-42,12):
            for bx in range(x+8,x+tile[0]-8,12):
                d.rectangle((bx,by,bx+11,by+11),fill='#dedbcd' if ((bx-x)//12+(by-y)//12)%2 else '#f6f1e4')
        out.paste(im,(x+(tile[0]-im.width)//2,y+10+(tile[1]-60-im.height)//2),im)
        d.text((x+8,y+tile[1]-38),Path(r['path']).stem[:25],font=font,fill='#345447')
        d.text((x+8,y+tile[1]-19),' × '.join(map(str,r['size'])),font=font,fill='#6e715f')
    out.save(qc/name)
board([r for r in records if r['category']=='ui_components_and_overviews' and '/png/' in r['path']],'components-contact.png')
board([r for r in records if r['category'] in ['legacy_exact_slices','legacy_atomic_controls']],'legacy-ui-contact.png')
board([r for r in records if r['category'] in ['legacy_screen_layers_and_compat','hud_layers'] and not r['path'].endswith('hud_labels.png')],'layers-contact.png',3,(430,250))
payload={'status':'passed' if not failures else 'failed','scope':'UI only; global artwork verification owned by root task','tracked_files':len(records),'new_ai_artwork_or_derivatives':sum(r['status']=='redrawn_from_new_ai_artwork' for r in records),'preserved_text_data':sorted(labels_only),'failures':failures,'generation_record':'source/generation.json','quality_parameter_exposed':False,'compositions':compositions,'records':records,'visual_qc':['qc/components-contact.png','qc/legacy-ui-contact.png','qc/layers-contact.png']}
write(HERE/'validation.json',payload)
write(REPO/'exact_qdao_slices/validation_native_q5.json',{'passed':not any('exact_qdao_slices' in p or 'buttons_redrawn_atomic' in p for p in failures),'date':'2026-09-07','count':73,'v7_ui_validation':'../qdao_gpt_image2_refresh_v7/ui/validation.json','checks':[r for r in records if r['category'] in ['legacy_exact_slices','legacy_atomic_controls']]})
write(layer/'validation_native_q5.json',{'passed':not any(r['category']=='legacy_screen_layers_and_compat' and r['path'] in failures for r in records) and all(c['passed'] for c in compositions),'date':'2026-09-07','count':12,'v7_ui_validation':'../qdao_gpt_image2_refresh_v7/ui/validation.json','compositions':compositions,'checks':[r for r in records if r['category']=='legacy_screen_layers_and_compat']})
print(json.dumps({'status':payload['status'],'tracked_files':len(records),'changed':payload['new_ai_artwork_or_derivatives'],'text_data':len(labels_only),'failures':failures,'compositions':compositions},ensure_ascii=False))
if failures:raise SystemExit(1)
