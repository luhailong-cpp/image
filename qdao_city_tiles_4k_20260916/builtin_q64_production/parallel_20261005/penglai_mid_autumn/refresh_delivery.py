from production import *

def main():
    h=read(ROOT/'handoff.json');plan=read(h['plan']['file'])
    entries={b['tile']:dict(file=b['file'],sha256=b['sha256'],kind='inherited_4K_candidate',status='inherited_4K_candidate_available',completePixelCoverage=True,formalAccepted=False,qaReusedByHash=h['latestQA']) for b in h['baselineCandidates']}
    current=[('r09_c13',ROOT/'output/r09_c13/manifest.json')]+[(mp.parent.parent.name,mp) for mp in sorted(ROOT.glob('r[0-9][0-9]_c[0-9][0-9]/output/manifest.json'))];scoped=[];new_entries=[]
    for ident,mp in current:
        if not mp.exists():continue
        m=read(mp);p=Path(m['file']);im=Image.open(p);assert im.size==(4096,4096);assert sha(p)==m['sha256']
        entries[ident]=dict(file=str(p),sha256=sha(p),kind='new_native_detail_4K_candidate',completePixelCoverage=True,formalAccepted=False,manifest=str(mp),status=m['status'])
        new_entries.append(ident)
        if m.get('scopedLocalSeamsPassed'):scoped.append(ident)
    tiles=[]
    for t in plan['tiles']:
        ident=t['id'];row=dict(id=ident,row=t['row'],column=t['column'],globalPixelRectXYWH=t['finalPixelRect'],worldRect=t['worldRect'],completePixelCoverage=False,formalAccepted=False,status='missing')
        row.update(entries.get(ident,{}));tiles.append(row)
    direct={};hist=[]
    for rp in ROOT.rglob('*.generation.json'):
        g=read(rp)
        if g.get('tool')!='image_gen.imagegen':continue
        evidence=g.get('evidence',{});key=evidence.get('sourceOutputSha256') or g.get('sha256')
        if key:direct.setdefault(key,dict(sha256=key,record=str(rp)))
        if g.get('fileNoLongerContainsTheseBytes'):hist.append(str(rp))
    summary=dict(updatedAt=now(),appearance=h['appearance'],wholeCityPixels=[65536,65536],tilePixels=[4096,4096],targetTiles=256,completePixelCandidates=len(entries),missingTiles=256-len(entries),formallyAcceptedTiles=0,wholeCityComplete=False,runtimePublished=False,clientVerified=False,navigationVerified=False,successfulUniqueAIGenerations=len(direct),builtinActualModel=None,builtinActualQuality=None,unverifiedReason='Host-managed builtin did not expose model or quality metadata.',tiles=tiles)
    write(ROOT/'delivery-index.json',summary)
    p=read(ROOT/'progress.json');active_id=p.get('currentTile','r10_c13');active=ROOT/active_id
    native_count=len(list((active/'native').glob('p[1-4][1-4].png.generation.json')))
    # The first32 products live in historical row directories; subsequent tiles use native/.
    detail_products=32+sum(len(list((f/'native').glob('p[1-4][1-4].png.generation.json'))) for f in ROOT.glob('r[0-9][0-9]_c[0-9][0-9]') if f.name!='r10_c12')
    active_stage='native_detail_generation' if native_count else 'shared_structure_preparation'
    if active_id in new_entries:active_stage='scoped_QA_passed' if active_id in scoped else 'complete_pixels_under_scoped_QA'
    p.pop('layoutGenerations',None);p.update(updatedAt=now(),newFullPixelCandidates=len(entries)-3,totalFullPixelCandidates=len(entries),missingTiles=256-len(entries),newAIGenerations=len(direct),formalAccepted=0,wholeCityComplete=False,runtimePublished=False,clientVerified=False,currentTiles=new_entries,deliveryIndex=str(ROOT/'delivery-index.json'),qaDefectsRemaining=len(scoped)<len(new_entries),qaPassedNewTiles=len(scoped),scopedQAPassedNewTiles=scoped,fullSeamInspectionCompleted=scoped,newNativeDetailPatches=detail_products,nativeDetailPatchProducts=detail_products,activeTileNativePatches=native_count,activeTileStage=active_stage);write(ROOT/'progress.json',p)
    w=read(ROOT/'current-work.json');w.update(updatedAt=now(),tile=active_id,stage=active_stage,activeWork={**{k:('available_internal_and_neighbor_seams_passed' if k in scoped else 'remaining_local_seam_repair') for k in new_entries},active_id:active_stage},currentCandidate=entries.get(active_id,entries[new_entries[-1]])['file'],next=f'Generate {active_id} using shared geometry and actual available native neighboring context, then inspect all available seams and junctions.');write(ROOT/'current-work.json',w)
    # Preview only: real tile coordinates in the bounding region, absent tiles left blank.
    minrow=min(int(k[1:3]) for k in entries);maxrow=max(int(k[1:3]) for k in entries);mincol=min(int(k[5:7]) for k in entries);maxcol=max(int(k[5:7]) for k in entries)
    preview=Image.new('RGB',((maxcol-mincol+1)*512,(maxrow-minrow+1)*512),'#202a32')
    for ident,e in entries.items():
        r=int(ident[1:3]);c=int(ident[5:7]);im=Image.open(e['file']).convert('RGB');preview.paste(im.resize((512,512),Image.Resampling.LANCZOS),((c-mincol)*512,(r-minrow)*512))
    out=ROOT/'current-preview.png';preview.save(out);deriv(out,[e['file'] for e in entries.values()],dict(kind='current_coverage_preview_only',tileCoordinates=True,sourceUpscaling=False,scale=0.125,blank='missing tiles, not game art'))
    print(__import__('json').dumps(dict(fullPixelCandidates=len(entries),missing=256-len(entries),formalAccepted=0,successfulUniqueAIGenerations=len(direct))))
if __name__=='__main__':main()
