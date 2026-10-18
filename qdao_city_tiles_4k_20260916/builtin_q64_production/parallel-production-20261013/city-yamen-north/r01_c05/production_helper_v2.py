"""r01_c05 local request/QA utilities. No image API/network calls."""
import importlib.util
import json
from pathlib import Path
from PIL import Image

BATCH = Path(__file__).resolve().parent.parent
s = importlib.util.spec_from_file_location("pipeline", BATCH / "batch_pipeline_v4.py")
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
TILE = "r01_c05"

def exact_request(prepared_file, description):
    q=m.read(prepared_file)
    assert q["tile"] == TILE
    q["prompt"]=("Use case: stylized-concept. Native 1254x1254 map continuation, central core [115,115,1139,1139]. "
        "Edit image1 as the exact local composition/scale target. " + description +
        " Preserve all sharp existing native overlap strips at their exact positions, leaf/stone scale, contour, texture and lighting; continue their forms smoothly. "
        "Newly paint clear fine Daoist chibi hand-painted detail into only the blurred layout areas. The blur is an enlarged layout guide, not finished artwork. "
        "Images2-3 supply brushwork/material style only, never UI, text or characters. Keep this close crop; do not fit a complete object/building or city into it. "
        "Add no object absent from guide. Soft daylight, rounded detailed painted forms, no photographic texture, plastic shine, noise or unpainted blur. "
        "No border, labels, grid or watermark. Output only the image.")
    if q["coordinates"]["haloOutsideArtCanvas"]:
        q["prompt"] += " Top115 rows are disposable off-canvas guide padding, not a striped texture or black boundary; paint natural continuation there. Keep all valid pixels at the same coordinates."
    q["referenced_image_paths"]=[q["guide"]["file"],str(m.ROOT/"designs/mail-ui-v1/01-mail-event.png"),str(m.ROOT/"designs/team-ui-v2/team-ui-v2.png")]
    q["createdAtUTC"]=m.now();q["preparationRequest"]=str(prepared_file)
    path=m.next_path(BATCH/"requests"/TILE,q["patch"]+"-exact")
    m.write_new(path,q)
    return {"request":str(path),"prompt":q["prompt"],"references":q["referenced_image_paths"]}

def splices(patch, source):
    p=m.spec(TILE,patch); x0,y0,x1,y1=p["coreWorldBox"]
    current={f"{t}/{k}":v for t in sorted(m.TILES) for k,v in m.selected(t).items()};outputs=[]
    with Image.open(source) as art:
        for other in current.values():
            if other["patch"]==patch:continue
            n=other["coordinates"]["coreWorldBox"]
            direction=None
            if n==[x0-1024,y0,x0,y1]:direction="west"
            elif n==[x1,y0,x1+1024,y1]:direction="east"
            elif n==[x0,y0-1024,x1,y0]:direction="north"
            elif n==[x0,y1,x1,y1+1024]:direction="south"
            if not direction:continue
            assert m.sha(other["file"])==other["sha256"]
            with Image.open(other["file"]) as adjacent:
                if direction=="west":sz=(320,1024);imgs=[adjacent,art];crops=[(979,115,1139,1139),(115,115,275,1139)];dest=[(0,0),(160,0)]
                elif direction=="east":sz=(320,1024);imgs=[art,adjacent];crops=[(979,115,1139,1139),(115,115,275,1139)];dest=[(0,0),(160,0)]
                elif direction=="north":sz=(1024,320);imgs=[adjacent,art];crops=[(115,979,1139,1139),(115,115,1139,275)];dest=[(0,0),(0,160)]
                else:sz=(1024,320);imgs=[art,adjacent];crops=[(115,979,1139,1139),(115,115,1139,275)];dest=[(0,0),(0,160)]
                out=m.next_path(BATCH/TILE/"qa",Path(source).stem+"-"+direction+"-native100",".png")
                im=Image.new("RGB",sz)
                for img,crop,xy in zip(imgs,crops,dest):im.paste(img.crop(crop),xy)
                im.save(out)
                outputs.append({"direction":direction,"file":str(out),"sha256":m.sha(out),"pixels":list(sz),"neighbor":other["file"],"neighborSHA256":other["sha256"],"cropLTRB":[list(c) for c in crops],"pasteXY":[list(d) for d in dest],"nativePixelScale":1})
    record=m.next_path(BATCH/TILE/"qa",Path(source).stem+"-splice-record")
    m.write_new(record,{"source":str(source),"sha256":m.sha(source),"method":"Exact core-edge crops, no resizing or blending","outputs":outputs})
    return {"record":str(record),"outputs":outputs}

def quick_select(patch,source,notes,evidence):
    review=m.next_path(BATCH/TILE/"qa",Path(source).stem+"-actual-quick-review")
    m.write_new(review,{"createdAtUTC":m.now(),"source":str(source),"sha256":m.sha(source),"quickVisualPassed":True,"actualViewNotes":notes,"actualEvidence":evidence,"formalAccepted":False,"wholeTileQA":"pending"})
    result=m.select_source(TILE,patch,source,True)
    return {"review":str(review),"selection":result}

if __name__=="__main__":
    import sys
    if sys.argv[1]=="request":result=exact_request(*sys.argv[2:])
    elif sys.argv[1]=="splices":result=splices(*sys.argv[2:])
    else:raise RuntimeError("Unsupported action")
    print(json.dumps(result,ensure_ascii=False))


def north_core_request(prepared_file, prompt, layout_context):
    """Guide-only north115 clipping; same-row native overlaps stay exact."""
    q=m.read(prepared_file)
    assert q['tile']==TILE
    world=q['coordinates']['worldBoxWithHalo']
    with Image.open(q['guide']['layout']) as im:
        w,h=im.size
        g=im.convert('RGB').transform((1254,1254),Image.Transform.EXTENT,[world[0]*w/65536,world[1]*h/65536,world[2]*w/65536,world[3]*h/65536],Image.Resampling.BICUBIC)
    actual=[]
    for item in q['guide']['nativeContextPastes']:
        ref=item['source'];crop=list(item['sourceCropLTRB']);dest=list(item['guidePasteXY'])
        if ref['worldBox'][1]<world[1]:
            crop[3]=min(crop[3],crop[1]+max(0,115-dest[1]))
        if crop[3]<=crop[1]:continue
        assert m.sha(ref['file'])==ref['sha256']
        with Image.open(ref['file']) as im:g.paste(im.convert('RGB').crop(crop),tuple(dest))
        actual.append({'source':ref,'sourceCropLTRB':crop,'guidePasteXY':dest,'resampled':False})
    p=m.next_path(BATCH/'requests'/TILE,q['patch']+'-north-core-guide','.png');g.save(p)
    q['guide']['originalPreparedGuide']=q['guide']['file'];q['guide']['file']=str(p);q['guide']['sha256']=m.sha(p)
    q['guide']['nativeContextPastes']=actual;q['guide']['northLockRows']=[0,115]
    q['guide']['preparationNote']='Guide only: approved enlarged layout plus exact same-world selected contexts; north limited to valid core115, excluding its southern halo. Source images unchanged.'
    q['createdAtUTC']=m.now();q['preparationRequest']=str(prepared_file);q['prompt']=prompt
    q['referenced_image_paths']=[str(p),str(layout_context),str(m.ROOT/'designs/mail-ui-v1/01-mail-event.png'),str(m.ROOT/'designs/team-ui-v2/team-ui-v2.png')]
    req=m.next_path(BATCH/'requests'/TILE,q['patch']+'-north-core-exact');m.write_new(req,q)
    return {'request':str(req),'prompt':prompt,'references':q['referenced_image_paths']}
