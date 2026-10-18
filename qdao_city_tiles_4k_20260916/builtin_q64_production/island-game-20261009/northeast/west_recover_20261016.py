from native_work import *
import sys

TILE='r04_c09'

def prepare(ident,neighbors):
    assert ident.startswith(TILE+'_')
    promptpath=ZONE/'prompts'/f'{ident}.prompt.txt'
    assert not promptpath.exists()
    guide(argparse.Namespace(id=ident,neighbor=neighbors,base=None))
    inp=ZONE/'prompts'/f'{ident}.inputs.json'
    refs=read(inp)[:(2 if len(neighbors)==1 else 1)]+current_references()[:1]
    for file,role in [('designs/mail-ui-v1/01-mail-event.png','approved primary Daoist Q hand-painted style, never copy UI or night'),('designs/team-ui-v2/team-ui-v2.png','approved primary Daoist Q hand-painted finish and rounded material style, never copy UI')]:
        p=ROOT/file
        refs.append({'file':p.as_posix(),'sha256':sha(p),'role':role})
    write(inp,refs)
    anchorinfo=read(Path(refs[0]['file']).with_suffix('.png.derivation.json'))['anchors']
    descriptions=[]
    for x in anchorinfo:
        at=x['targetPaste']; crop=x['sourceCrop']
        descriptions.append(f"{Path(x['file']).stem}: fixed anchor pixels at target x{at[0]}..{at[0]+crop[2]-crop[0]}, y{at[1]}..{at[1]+crop[3]-crop[1]}")
    prompt='Use case: sketch-to-render. Produce one opaque native 1254x1254 game map patch '+ident+'. Image 1 is the edit target: blurry pixels are coordinate layout guidance only, sharp overlap bands are fixed native neighbors. Image 2 shows the native neighbor reference(s), in the listed anchor order. Image 3 is full-island layout authority; image 4 is material detail; images 5 and 6 show approved Daoist Q hand-painted style only, do not copy their UI, figures, text or night setting. '+ '; '.join(descriptions)+'. Preserve the sharp overlap bands exactly, continue incoming slab grout contours at their exact endpoints, spacing and direction. Repaint only the unresolved blurry interior as crisp detailed daylight natural pale gray and blue-gray stone paving, rounded gently beveled slabs, restrained irregular cream mineral mottling. Preserve any existing architecture, plants or shadows in the blurry coordinate guide at their exact positions and scale; add none if absent. Maintain identical camera, framing, stone scale and lighting throughout. Match complete stone faces across the band edges with gradual irregular mineral changes, no straight material cutoff or blurry-to-sharp transition. Empty paving remains clear walkable ground. No new motifs, characters, trees, objects, UI, text, border, grid overlay, watermark, crop, zoom or reframing. Full-bleed opaque square1254x1254, native detailed painting.'
    prompt=prompt.replace('Image 2 shows the native neighbor reference(s), in the listed anchor order. Image 3 is full-island layout authority; image 4 is material detail; images 5 and 6', 'Image 2 is full-island layout authority; images 3 and 4')
    if len(neighbors)==1:
        prompt=prompt.replace('Image 2 is full-island layout authority; images 3 and 4','Image 2 is adjacent native scale and surface reference only; do not copy its whole composition. Image 3 is full-island layout authority; images 4 and 5')
    prompt+=' Preserve the same slab lattice scale as the native anchors, typically450-650px long and200-350px wide per slab, about8-12 whole or partial slabs in1254square. Tiny face grain is not separate cobblestones. No giant slabs or tiny paver field.'
    promptpath.write_text(prompt,encoding='utf-8')
    write(ZONE/'receipts'/f'{ident}.preflight.json',{'checkedAtUtc':now(),'rootInstructions':sha(ROOT/'AGENTS.md'),'parallelSplit':sha(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'coordinate':ident,'builtinOnly':True,'paidApiAllowed':False,'actualModel':None,'actualQuality':None,'sourceRefs':refs,'status':'ready'})
    print(json.dumps({'prompt':prompt,'references':[r['file'] for r in refs]},ensure_ascii=False))

def select(ident,note,status='passed_quick_layout_geometry'):
    p=patch(ident); recpath=ZONE/'native'/f'{ident}.png.generation.json'; rec=read(recpath)
    assert (rec['nativeWidth'],rec['nativeHeight'])==(1254,1254)
    r=int(ident.split('_p')[1][:2])-1; c=int(ident.split('_p')[1][3:5])-1
    sel=read(ZONE/f'selection-{TILE}.json'); sel['cores'][r][c]=ident;sel['updatedAtUtc']=now();sel['formalAccepted']=False;sel['selectionIsPartialCandidate']=not all(all(x) for x in sel['cores'])
    if 'pendingIssues' not in sel:sel['pendingIssues']=[]
    if status!='passed_quick_layout_geometry':sel['pendingIssues'].append({'source':ident,'sha256':rec['sha256'],'issue':note,'status':'pending_not_passed'})
    write(ZONE/f'selection-{TILE}.json',sel)
    write(ZONE/'qa'/f'{ident}.quick-review-20261016.json',{'source':rec['file'],'sha256':rec['sha256'],'reviewedAtUtc':now(),'status':status,'note':note,'fullInternalQa':'pending all16','formalAccepted':False})
    print(json.dumps({'selected':ident,'selectedCount':sum(bool(c) for row in sel['cores'] for c in row),'status':status}))

if __name__=='__main__':
    action=sys.argv[1]
    if action=='prepare':prepare(sys.argv[2],sys.argv[3:])
    elif action=='select':select(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else 'passed_quick_layout_geometry')
