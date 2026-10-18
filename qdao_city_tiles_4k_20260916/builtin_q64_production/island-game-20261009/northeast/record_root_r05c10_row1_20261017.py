from native_work import *
s=read(ZONE/'selection-r05_c10.json')
reviews=[('r04_c10_p04_01','r05_c10_p01_01','passed_cross_tile_core_segment_only','Lantern red trim and gray slab grout continue across the top; material remains coherent.'),('r05_c10_p01_01','r05_c10_p01_02','pending_local_curb_and_surface_transition','Paving endpoints align. Lower cream curb underside changes thickness near the core boundary; surface texture differs. Pending localized correction.'),('r04_c10_p04_03','r05_c10_p01_03','geometry_pass_material_transition_pending','Grout endpoints align, but upper paving has visibly finer mottling than generated center.'),('r05_c10_p01_02','r05_c10_p01_03','geometry_pass_material_transition_pending','Grout joins align. Surface paint grain changes at the seam.'),('r05_c10_p01_03','r05_c10_p01_04','geometry_pass_material_transition_pending','Slab structure continues. Larger pale mottling on left meets smaller outlined grain on right abruptly.')]
for a,b,status,note in reviews:
 p=ZONE/'qa'/f'{a}__{b}.json';q=read(p);q.update(status=status,reviewer='root',reviewedAtUtc=now(),reviewNotes=note,inspection='direct exact 1:1 concatenated native core strips');write(p,q)
 if not status.startswith('passed'):s['pendingIssues'].append({'id':q['seamId'],'status':status,'note':note,'evidence':q['inspectionEvidencePath']})
for ident,col in [('r05_c10_p01_01',0),('r05_c10_p01_03',2)]:
 p=ZONE/'native'/f'{ident}.png.generation.json';q=read(p);q.update(status='selected_layout_candidate_local_seams_pending',layout='native crop follows original lantern/garden or paving occupancy',internalSeams='see exact join reviews; local transitions pending',externalSeams='available upper boundary reviewed');write(p,q);s['cores'][0][col]=ident
s.update(updatedAtUtc=now(),formalAccepted=False);write(ZONE/'selection-r05_c10.json',s)
f=ZONE/'selection-r03_c09.json';q=read(f);msg='Whole-tile layout mismatch: generated extra small ball posts/short wall segments around the upper-left lantern garden and an ornamental pillar in the lower garden; original tall tree/foliage mass and sparse boundary posts are not faithfully retained. Layout repair required; internal49 QA alone cannot pass tile.'
if msg not in q['pendingIssues']:q['pendingIssues'].append(msg)
q.update(internalReview='failed_layout_authority_seams_pending',layoutReview='failed',formalAccepted=False,updatedAtUtc=now());write(f,q)
f=ZONE/'tiles/r03_c09-native-v1-20261016.png.derivation.json';q=read(f);q.update(status='complete_native_coverage_layout_repair_required',layoutReview='failed',internalReview='pending',formalAccepted=False);write(f,q)
print(json.dumps({'r05c10Selected':4,'r03c09Layout':'failed_pending_repair'}))
