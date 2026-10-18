from native_work import *
ident='r03_c09_p02_02'
s=read(ZONE/'selection-r03_c09.json');s['cores'][1][1]=ident
s.setdefault('pendingIssues',[]).append('r03_c09_p02_02 right join to p02_03: straight material density change and a few cut leaves; initial candidate retained, v2 repair moved grout and is rejected. Left/downward native anchors remain usable for independent production.')
s['updatedAtUtc']=now();write(ZONE/'selection-r03_c09.json',s)
p=ZONE/'native'/f'{ident}.png.generation.json';r=read(p);r.update(status='selected_native_candidate_right_material_seam_pending',internalSeams='upper passed; right failed material continuity; full49 pending');write(p,r)
p=ZONE/'native/r03_c09_p02_02_v2.png.generation.json';r=read(p);r.update(status='rejected_repair_moved_right_grout_and_foliage',internalSeams='upper retained; right grout kink worse than initial');write(p,r)
p=ZONE/'qa/r03_c09_p02_02_v2__r03_c09_p02_03.json';r=read(p);r.update(status='failed_geometry_continuity',reviewedAtUtc=now(),reviewer='root',observed='Right core join grout kink at y300 and shifted leaf shapes; first local full-core repair unsuccessful.');write(p,r)
print(json.dumps({'selected':ident,'pendingRight':True,'rejected':'r03_c09_p02_02_v2'}))

