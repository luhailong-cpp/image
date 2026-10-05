"""Prepare guide-only context from current handoff; never export guide pixels as art."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REPO=Path('D:/work/image')
TILE=ROOT/'r08_c09'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,j): Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    h=read(ROOT/'handoff.json')
    authorization=read(ROOT/'continuation-authorization.json') if (ROOT/'continuation-authorization.json').exists() else {}
    if not h['readyForProduction'] and not authorization.get('continueFromVerifiedWest'):
        raise SystemExit('handoff not ready; no dependent guides written')
    for item in [h['plan'],h['layout'],*h['baselineCandidates']]:
        assert Path(item['file']).is_file(),item['file']
        assert sha(item['file'])==item['sha256'],item['file']
    west=next(t for t in h['baselineCandidates'] if t['tile']=='r08_c08')
    for sub in ['guides','regional','native','prompts','jobs','qa']:
        (TILE/sub).mkdir(parents=True,exist_ok=True)
    assert not (TILE/'regional/target-layout-only.png').exists()
    full=Image.open(h['layout']['file']).convert('RGB')
    extent=[v*1254/65536 for v in [32653,28557,36979,32883]]
    guide=full.transform((4326,4326),Image.Transform.EXTENT,extent,Image.Resampling.BICUBIC)
    previous=REPO/'qdao_city_tiles_4k_20260916/builtin_q64_production/lanxian_day/r08_c09/native/r01_c01.png'
    assert sha(previous)=='52dd3413b2fa93e930b1c7d8126ea86a2a46eab38aa93b7aebc9b5b151e9917c'
    guide.paste(Image.open(previous).convert('RGB'),(0,0))
    w=Image.open(west['file']).convert('RGB')
    assert w.size==(4096,4096)
    guide.paste(w.crop((3981,0,4096,4096)),(0,115))
    # Missing top/bottom exterior context is edge padding in a guide, not source art.
    guide.paste(w.crop((3981,0,4096,1)).resize((115,115),Image.Resampling.NEAREST),(0,0))
    guide.paste(w.crop((3981,4095,4096,4096)).resize((115,115),Image.Resampling.NEAREST),(0,4211))
    target=TILE/'regional/target-layout-only.png'
    guide.resize((1254,1254),Image.Resampling.LANCZOS).save(target)
    wp=TILE/'regional/west-c08-context-preview.png'
    w.resize((1254,1254),Image.Resampling.LANCZOS).save(wp)
    overview=ROOT/'current-preview.png'
    canvas=Image.new('RGB',(2048,1024),(40,50,50))
    canvas.paste(w.resize((1024,1024),Image.Resampling.LANCZOS),(0,0))
    canvas.paste(guide.crop((115,115,4211,4211)).resize((1024,1024),Image.Resampling.LANCZOS),(1024,0))
    canvas.save(overview)
    now=datetime.now(timezone.utc).isoformat()
    refs=[{'path':str(target),'role':'Target framing and provisional geometry, layout only; first small upper-left square is surviving native detail; thin left strip from selected west neighbor'}, {'path':str(wp),'role':'Selected west neighbor at preview scale; curve tangents, materials, daylight'}, {'path':str(REPO/'designs/gameplay-ui/04-guild.png'),'role':'User-confirmed primary painting/material style, no UI copied'}]
    meta={'schemaVersion':1,'createdAtUtc':now,'guideOnly':True,'finalArt':False,'tile':'r08_c09','handoffSha256':sha(ROOT/'handoff.json'),'west':west,'derivedFrom':[h['layout'],{'file':str(previous),'sha256':sha(previous)},west],'operation':'Layout extent transformed to4326 only for guide; surviving native1254 at0,0; west exact115px at0,115; padded unavailable exterior guide ends; previews downsampled. No guide pixels may enter final art.','extentIn1254Layout':extent,'guideCanvasPixels':[4326,4326],'exportedRegionalGuidePixels':[1254,1254],'references':refs,'currentPreview':{'file':str(overview),'sha256':sha(overview),'role':'left current candidate; right guide-only not generated art'},'nativePatchReuse':'conditional upon native boundary inspection; not counted complete'}
    write(TILE/'regional/context.json',meta)
    p=read(ROOT/'current-work.json');p.update(updatedAtUtc=now,readyForProduction=h['readyForProduction'],productionAuthorized=True,status='active_native_production',currentPhase='regional_structure_recovery',nextAction='Generate missing regional structural guide through builtin imagegen, then native detail patches with shared context.',baselineCurrent=h['baselineCurrent'],preview=str(overview));p.pop('blockingCondition',None);write(ROOT/'current-work.json',p)
    print(json.dumps({'references':refs,'westSha256':west['sha256']}))

if __name__=='__main__':main()
