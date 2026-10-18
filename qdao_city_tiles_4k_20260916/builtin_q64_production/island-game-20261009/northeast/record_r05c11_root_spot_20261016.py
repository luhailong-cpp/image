from native_work import *
name='r05_c11-localfinish-v3-20261016';tile=ZONE/'tiles'/f'{name}.png'
paths=[ZONE/'qa'/f'{name}-changed'/f'{x}-100pct.png' for x in ['vertical-3-segment-1','core-1-4','external-top-4']]
out=ZONE/'qa'/f'{name}-root-independent-spotreview-20261016.json';assert not out.exists()
write(out,{'candidatePath':tile.as_posix(),'candidateSha256':sha(tile),'reviewedAtUtc':now(),'reviewer':'root','scope':'3 changed/known-pending crop checks, not full49 repeated','internalSpotReview':'passed','externalTopSegment4':'still_pending_small_gold_rib_step','formalAccepted':False,'crops':[{'file':p.as_posix(),'sha256':sha(p),'status':'pending_known_gold_rib_detail' if 'external-top' in p.name else 'passed_direct100pct'} for p in paths],'notes':['Internal paving focus transition no longer forms a straight seam; matching slab geometry and foliage preserved.','Upper lantern golden ribs retain slight lateral/thickness steps; worker correctly did not mark this boundary passed.']})
print(out.as_posix())

