from pathlib import Path
from PIL import Image
import hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[2]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
entries=json.loads((ROOT/'provenance/run/selection-S.json').read_text(encoding='utf-8'))+json.loads((ROOT/'provenance/run/selection-NE-SW.json').read_text(encoding='utf-8'))
notes=json.loads((ROOT/'provenance/run/S-NE-SW-foot-review-notes.json').read_text(encoding='utf-8'))
phases={
'S':['right_contact','right_load_compression','right_support_left_passing','right_push_off_candidate','left_leading_short_flight','left_extension_precontact','left_precontact','left_initial_contact','left_contact','left_load_compression','left_support_right_passing','left_push_off_candidate','right_leading_short_flight','right_extension_precontact','right_precontact','right_initial_contact'],
'NE':['right_contact','right_load_compression','right_support_left_passing','right_push_off_candidate','short_flight','left_extension_flight','left_precontact','left_initial_contact','left_contact','left_load_compression','left_support_right_passing','left_push_off_candidate','opposite_short_flight','continued_flight','right_precontact','right_initial_contact'],
'SW':['right_contact','right_load_compression','right_support_left_passing','right_push_off_candidate','left_leading_flight','left_extension_flight','left_precontact','left_initial_contact','left_contact','left_load_compression','left_support_right_passing','left_push_off_candidate','right_leading_short_flight','right_extension_flight','right_precontact','right_initial_contact']
}
out=[]
for e in entries:
 p=ROOT/e['file']; rp=ROOT/e['generationRecord']; r=json.loads(rp.read_text(encoding='utf-8-sig'))
 sh=hashlib.sha256(p.read_bytes()).hexdigest()
 with Image.open(p) as im:
  im.load(); size=list(im.size); mode=im.mode; alpha=list(im.getchannel('A').getextrema())
 assert size==[1254,1254] and mode=='RGBA' and alpha==[0,255],e
 assert sh==r['sha256'],e
 d=e['direction']; f=e['frame']; foot=notes[d][f-1]
 review={
 'reviewedAt':now,'method':'every selected native PNG actually viewed individually via generatedImage/view_image',
 'reviewedSha256':sh,'selectedSlot':{'action':'run','direction':d,'frame':f},
 'status':'single_frame_usable_for_fixed_root_sequence_review',
 'singleFrameReviewComplete':True,'singleFramePoseUsable':True,
 'identityAndStylePreserved':True,'twoArmsTwoLegs':True,'leftHandUpperQinRightHandLowerStrings':True,
 'footHeadingConclusion':'no_remaining_clear_outward_toe_defect',
 'footHeadingNotes':foot,'observedPhase':phases[d][f-1],
 'poseNotes':e['notes'],'mustCorrectBeforeSequenceReview':[],
 'staticSequenceAccepted':False,'dynamicAccepted':False,
 'finalReport':'provenance/run/S-NE-SW-static-review-20261003.json'
 }
 r['visualReview']=review
 r['status']='candidate_for_fixed_root_sequence_review'
 rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 out.append({**e,'sha256':sh,'nativeSize':size,'mode':mode,'alphaExtrema':alpha,'observedPhase':phases[d][f-1],'footHeadingNotes':foot,'singleFramePoseUsable':True,'mustCorrectBeforeSequenceReview':[],'dynamicAccepted':False})
assert len(out)==48 and len({x['sha256'] for x in out})==48
for d in ['S','NE','SW']:
 assert sorted(x['frame'] for x in out if x['direction']==d)==list(range(1,17))
report={
 'schemaVersion':1,'reviewedAt':now,'scope':'run S/NE/SW selected 48 native frames; single-frame static/anatomy/foot-heading review only',
 'selectedFrameCount':48,'uniqueSha256Count':48,'allNativeSize':[1254,1254],'allRGBA':True,'allGenerationHashesMatch':True,
 'allSelectedPixelsActuallyViewed':True,'singleFrameStaticReviewComplete':True,
 'mustCorrectBeforeSequenceReview':[],
 'footDirectionConclusion':'当前48张未见仍必须修正的明确脚掌横向外撇。S01/S02原生压平支撑前掌；NE01-v3/NE02-v2澄清后跟鞋头读法；其余方向正确图保留。',
 'SCommonNativeAnchorSuggestion':{'x':627,'groundY':1215,'method':'目测骨盆投影与多张左右接触带，不用逐帧最低脚；统一缩放和整段常数根。','acceptedByRootForPreview':True},
 'constraints':{'singleCommonScale':True,'noPerFrameBboxFit':True,'noPerFrameFootSnap':True,'noMirroredOrCopiedFill':True,'phaseLabelsFromActualPose':True},
 'registrationAndDynamicWatchlist':[
 {'direction':'S','frames':[4,12],'issue':'低位前掌发力可作为蹬离过渡，但静态抬跟证据较弱；固定根试播看是否形成蹬离。'},
 {'direction':'S','frames':[5,6,7,13,14,15],'issue':'06/14已接近预接触、13短腾空余隙小；实际相位应按画面调整，不能按原prompt自动标腾空峰值。'},
 {'direction':'S','frames':[16,1,2,3],'issue':'01/02已改平掌；用统一根核对循环初触到压缩承重，不逐帧贴脚。'},
 {'direction':'NE','frames':[4,12],'issue':'前掌蹬离与抬跟读法需整段固定根核实，不能靠整帧位移制造接地。'},
 {'direction':'NE','frames':[13,14,15],'issue':'14实图为持续腾空，需检查13→14→15落下连续性；鞋头朝向无须重画。'},
 {'direction':'SW','frames':[4,5,6,7,8],'issue':'异侧链已修正；05→06→07左前腿下降/初触时机需要固定根试播。'}
 ],
 'staticSequenceAccepted':False,'dynamicAccepted':False,'runtimeExportAccepted':False,
 'modelEvidence':{'configuredTarget':'gpt-image-2.5-sunburst','configuredQuality':'max','actualModel':None,'actualQuality':None,'reason':'宿主管理工具未提供模型/质量选择器或实际返回值。'},
 'selectedFiles':out
}
rp=ROOT/'provenance/run/S-NE-SW-static-review-20261003.json'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for stem,reason in {
 'NE01-v2':'靴朝向改善，但非靴区域重绘导致比例/落脚高度变化；未选，改用严格局部编辑v3。',
 'S01-v1':'初触前掌翘起露整块花纹底，与16平掌到01循环出现反向翘掌；改用v2。',
 'S02-v1':'压缩承重仍前掌翘起大面积露底；改用前掌压平v2。',
 'S10-v1':'要求压低却头更高且鞋底下探近1240，改用v2。'
}.items():
 (ROOT/'provenance/run'/f'{stem}.review.json').write_text(json.dumps({'reviewedAt':now,'decision':'rejected_not_selected','reason':reason,'actualPixelsViewed':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(rp),'frames':48,'unique':48,'mustCorrectBeforeSequenceReview':[],'dynamicAccepted':False},ensure_ascii=False))

