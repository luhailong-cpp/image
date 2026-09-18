from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
root=Path(r'E:/work/image/qdao_city_tiles_4k_20260916');p=root/'builtin_q64_production/tianyong_festival/L_r09_c07_r10_c07_c10'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
review={'schemaVersion':1,'reviewedAtUtc':now,'status':'local_native_detail_and_join_review_complete_external_neighbors_and_runtime_pending','formalAcceptance':False,'reviewed':{'newTileNativeGenerations':16,'crossTileBoundaryXSegments':[0,1024,2048,2842],'newTileInternalFullSeamBands':['vertical1024','vertical2048','vertical3072','horizontal1024','horizontal2048','horizontal3072'],'bandPixelScale':1,'junctionBelowCrop':'qa/junction_below_100pct.jpg','v2RepairedContexts':['tree_boundary_context.jpg','floor_boundary_context.jpg','upper_stone_joints_context.jpg'],'v3RepairedContext':'short_joint_context.jpg'},'findings':['Initially clipped foliage wedge repaired with native redraw.','Abruptly terminated paving joint and jagged curved band repaired and rechecked after composition.','Upper narrow border missing segment and incomplete top grout repaired using two successive native redraws and rechecked.','Cross-column junction in row10 reviewed at original pixel scale.','All six complete internal seam bands of the new tile inspected.'],'remaining':['Outer neighboring rows/columns incomplete.','Closest-camera, foreground separation, navigation and runtime acceptance pending.','Minor hand-painted texture, highlight and joint-width variations remain for camera-scale review.'],'parentVisualReview':str(p.parent/'quad_r10_c07_c10/qa_v2/visual-review.json'),'sourceArtUpscaled':False,'limitedSubpixelRegistrationUsed':True,'assemblySha256':sha(p/'assembly_v3.json'),'runtimePublished':False}
(p/'qa_v3/visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
base=p.relative_to(root).as_posix()+'/'
candidates=[]
for row,col in [(9,7),(10,7),(10,8),(10,9),(10,10)]:
 tile=f'r{row:02}_c{col:02}';f=p/'output_v3'/f'{tile}.png'
 candidates.append({'appearance':'tianyong_festival','displayName':'天墉城节庆','tile':tile,'file':base+'output_v3/'+tile+'.png','sha256':sha(f),'assembly':base+'assembly_v3.json','qa':base+'qa_v3/visual-review.json','finalPixelRectXYWH':[(col-1)*4096,(row-1)*4096,4096,4096],'worldRect':{'x':50+(col-1)*18.75,'z':300-row*18.75,'width':18.75,'height':18.75}})
repairs=[base+'repairs/v2/native/'+n+'.record.json' for n in ('tree_boundary','floor_boundary','upper_stone_joints')]+[base+'repairs/v3/native/short_joint.record.json']
(p/'ledger-update.json').write_text(json.dumps({'createdAtUtc':now,'candidates':candidates,'repairRecords':repairs,'newCoordinateCount':1,'updatedCoordinates':4,'newBaseNativeCount':16,'newRepairNativeCount':4,'formalAcceptance':False,'runtimePublished':False},ensure_ascii=False,indent=2),encoding='utf-8')
planfile=p.parent/'r09_c07/plan.json';plan=json.loads(planfile.read_text());plan['status']='locally_reviewed_candidate_with_neighbor_join_external_and_runtime_pending';plan['selectedCandidate']=str(p/'output_v3/r09_c07.png');plan['selectedAssembly']=str(p/'assembly_v3.json');planfile.write_text(json.dumps(plan,indent=2),encoding='utf-8')
print('Five unique Tianyong coordinates ready; one new coordinate and four updated')
