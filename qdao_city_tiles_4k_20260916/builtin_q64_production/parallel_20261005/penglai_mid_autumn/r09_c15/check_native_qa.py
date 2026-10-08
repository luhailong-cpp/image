"""Post-assembly QA preparation only. Does not create or modify a candidate.

Prepared while source migration is pending; invoke only after root releases it.
Default checks existing standard QA in memory. --write-details emits unrotated
west details and an unreviewed index, never any seam-acceptance record.
"""
from pathlib import Path
import argparse, hashlib, json, sys
from datetime import datetime, timezone
import numpy as np
from PIL import Image

T=Path(__file__).resolve().parent
ROOT=T.parent
sys.path.insert(0,str(ROOT))
from native_assemble import full_strip

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def anchor(p):return {'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--expected-candidate-sha256',required=True)
    ap.add_argument('--expected-west-sha256',required=True)
    ap.add_argument('--source-migration-record',type=Path,required=True)
    ap.add_argument('--write-details',action='store_true')
    a=ap.parse_args()
    migration=a.source_migration_record.resolve()
    assert migration.is_relative_to(ROOT.resolve()) and migration.is_file()
    read(migration)  # Require an actual persisted JSON migration record.
    plan=read(T/'plan.json')
    candidate=T/'output/r09_c15-candidate.png'
    assembly=T/'output/native-assembly.json'
    assert candidate.is_file() and assembly.is_file(), 'Parent must release source migration and complete assembly first.'
    assert sha(candidate)==a.expected_candidate_sha256.lower()
    west=Path(plan['westCandidate'])
    assert sha(west)==plan['westCandidateSha256']==a.expected_west_sha256.lower()
    assert sha(west)!='26ef781afe2fe0d6d8352f4a6f57e88780b93a7ed26cb41411efbc35d44432dc', 'Old whole-source hash: migration still pending.'
    asm=read(assembly)
    assert asm['sha256']==sha(candidate) and asm['neighbors']['west']['sha256']==sha(west)
    assert asm['plan']['sha256']==sha(T/'plan.json')
    assert set(asm['neighbors'])=={'west'}, 'This prepared QA schedule is for the approved west-only tile.'
    new=Image.open(candidate).convert('RGB');old=Image.open(west).convert('RGB')
    assert new.size==old.size==(4096,4096)
    before={str(p):sha(p) for p in [candidate,west,assembly,T/'plan.json']}
    expected={}
    for axis in ('x','y'):
        for pos in (1024,2048,3072):
            expected[f'internal-{axis}{pos}-full']=full_strip(new,axis,pos)[0]
            expected[f'internal-{axis}{pos}-return-256-full']=full_strip(new,axis,pos+256)[0]
    for y in (1024,2048,3072):
        for x in (1024,2048,3072):
            expected[f'junction-{x}-{y}']=new.crop((x-160,y-160,x+160,y+160))
    band=Image.new('RGB',(320,4096))
    band.paste(old.crop((3936,0,4096,4096)),(0,0));band.paste(new.crop((0,0,160,4096)),(160,0))
    sheet=Image.new('RGB',(1024,1280))
    for i in range(4):sheet.paste(band.crop((0,i*1024,320,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90),(0,i*320))
    expected['west-shared-full']=sheet
    expected['west-return-256-full']=full_strip(new,'x',256)[0]
    expected['north-return-256-full']=full_strip(new,'y',256)[0]
    for side,box in [('east',(3776,0,4096,4096)),('south',(0,3776,4096,4096))]:
        band=new.crop(box);sheet=Image.new('RGB',(1024,1280))
        for i in range(4):
            part=band.crop((0,i*1024,320,(i+1)*1024)) if side=='east' else band.crop((i*1024,0,(i+1)*1024,320))
            if side=='east':part=part.transpose(Image.Transpose.ROTATE_90)
            sheet.paste(part,(0,i*320))
        expected[side+'-no-neighbor-unverified']=sheet
    assert len(expected)==26
    standard=[]
    for name,im in expected.items():
        p=T/'qa/native-candidate'/(name+'.png');metadata=read(str(p)+'.generation.json')
        assert metadata['sha256']==sha(p)
        assert np.array_equal(np.asarray(im),np.asarray(Image.open(p).convert('RGB'))),name
        standard.append({**anchor(p),'pixels':list(im.size),'nativeScale':1,
            'actuallyViewed':False,'verdict':'pending_visual_QA','verifiedAgainstCurrentCandidatePixels':True,
            'operation':metadata['operation']})
    details=[]
    if a.write_details:
        out=T/'qa/external-details'
        index=T/'qa/native-review-index.json'
        assert not out.exists() and not index.exists(), 'Refuse to overwrite QA.'
        out.mkdir(parents=True)
        # All four segments show entire west edge at 1:1, without rotation.
        # Use an explicit-recipe name: generic west-segment names mean 256px per side.
        scopes=[(f'west-native-context-{i+1}',i*1024,(i+1)*1024) for i in range(4)]
        scopes += [('west-p31-paving-detail',2760,3272),('west-p41-paving-detail',3072,4096)]
        for name,y0,y1 in scopes:
            im=Image.new('RGB',(832,y1-y0))
            im.paste(old.crop((3776,y0,4096,y1)),(0,0))
            im.paste(new.crop((0,y0,512,y1)),(320,0))
            p=out/(name+'.png');im.save(p)
            rec={**anchor(p),'pixels':list(im.size),'nativeScale':1,'actuallyViewed':False,
                 'verdict':'pending_visual_QA','sourceUpscaling':False,'rotationCCW90':False,
                 'joinX':320,'westCropLTRB':[3776,y0,4096,y1],'candidateCropLTRB':[0,y0,512,y1],
                 'reproduction':{'canvasPixels':[832,y1-y0],'pieces':[
                     {'source':'west','cropLTRB':[3776,y0,4096,y1],'pasteXY':[0,0]},
                     {'source':'current','cropLTRB':[0,y0,512,y1],'pasteXY':[320,0]}]},
                 'sources':[anchor(west),anchor(candidate)]}
            write(Path(str(p)+'.generation.json'),rec);details.append(rec)
        write(index,{'createdAt':datetime.now(timezone.utc).isoformat(),'candidate':anchor(candidate),
            'west':anchor(west),'sourceMigrationRecord':anchor(migration),'nativeAssembly':anchor(assembly),
            'standardQA':standard,'unrotatedWestDetails':details,'sourcePixelScale':1,
            'inspectionSchedule':'View all26 standard originals plus all4 unrotated west segments and2 concern details. Internal x/y strips are four1024-long sections stacked; x strips are CCW90. The seam within each320px section is at160. North/east/south neighbors are absent and must remain unverified.',
            'formalAccepted':False,'scopedLocalSeamsPassed':False,'candidatePixelsChanged':False})
    assert all(sha(p)==h for p,h in before.items()), 'Protected input changed during QA operation.'
    print(json.dumps({'standardPixelChecks':len(standard),'detailsWritten':len(details),
        'candidatePixelsChanged':False,'visualQAClaimed':False,'candidateSha256':sha(candidate)}))

if __name__=='__main__':main()
