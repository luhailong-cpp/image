from prepare_structure import *
ident=sys.argv[1]; note=sys.argv[2];assert ident in [f'p{r}{c}' for r in [2,3,4] for c in range(1,5)]
p=F/'native'/f'{ident}.png';req=read(F/'native'/f'{ident}.request.json');g=read(str(p)+'.generation.json')
assert Image.open(p).size==(1254,1254) and sha(p)==g['sha256']
assert g['actualModel'] is None and g['actualQuality'] is None
record=dict(at=now(),reviewer='/root/r09c14_row4_resume',file=str(p),sha256=sha(p),actuallyViewed=True,outputViewedVia='native image_gen result at1254x1254',inputsActuallyViewed=[ref(F/'native'/f'{ident}-edit-target.png'),ref(F/'guides'/f'{ident}.png'),ref(STYLE)],inputViewDetail='original',observations=note,compositionPreserved=True,fullSeamReviewPending=True,formalAccepted=False,rootReview=False,contextSourceRegions=req['contextRegions'])
write(F/'native'/f'{ident}.visual-review.json',record)
print(json.dumps(ref(p),indent=2))
