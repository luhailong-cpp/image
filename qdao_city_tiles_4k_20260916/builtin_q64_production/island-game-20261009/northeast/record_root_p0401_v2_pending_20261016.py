from native_work import *
p=ZONE/'qa/r03_c09_p03_01_v2__r03_c09_p04_01_v2.json';q=read(p);q.update(status='passed_internal_only',reviewedAtUtc=now(),reviewer='root',observed='Original left recessed wall molding offset repaired; stone geometry now continuous at upper actual join.');write(p,q)
p=ZONE/'qa/r03_c09_p04_01_v2__r03_c09_p04_02.json';q=read(p);q.update(status='pending_internal_anchor_line_only',reviewedAtUtc=now(),reviewer='root',observed='Actual core join aligns; sourcex1024 y915..1139 inside left patch cuts foliage. Existing v1 lower corner may restore this without undoing fixed upper wall.');write(p,q)
p=ZONE/'selection-r03_c09.json';s=read(p);s['cores'][3][0]='r03_c09_p04_01_v2';s['updatedAtUtc']=now();s['internalReview']='complete_native_coverage_pending_local_repairs_and49QA'
s['pendingIssues'].append('r03_c09_p04_01_v2 upper stone molding repaired, but internal right anchor border sourcex1024,y915..1139 cuts foliage; v1 lower-corner crop under review.')
write(p,s)
p=ZONE/'native/r03_c09_p04_01_v2.png.generation.json';q=read(p);q.update(status='selected_native_candidate_internal_foliage_anchor_line_pending',internalSeams='upper actual join passed; right actual core join coherent, inner anchor foliage line pending');write(p,q)
p=ZONE/'qa/root-p0401-upper-crop-20261016/inspection.json';q=read(p);q.update(status='rejected_lower_molding_offsets',bottom='failed_direct100pct: horizontal crop introduces several shifted vertical moulding lines',reviewer='root',reviewedAtUtc=now());write(p,q)
print(json.dumps({'selected':16,'quality':'local_repairs_pending'}))

