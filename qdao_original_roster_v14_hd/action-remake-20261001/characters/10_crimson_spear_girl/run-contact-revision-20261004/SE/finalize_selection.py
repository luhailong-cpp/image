from pathlib import Path
import json,datetime
w=Path(__file__).parent
p=w/'selection.json'
s=json.loads(p.read_text(encoding='utf-8-sig'))
s['slots']['run/SE/07']='run-contact-revision-20261004/SE/07-v10/native.png'
s['slots']['run/SE/08']='run-contact-revision-20261004/SE/08-v5/native.png'
s['status']='drawing-reviewed-ready-for-integrated-playback'
s['actualApproval']=False
s['drawingReviewPassed']=True
s['pending']='Parent final integrated normal-speed playback and wraparound review'
s['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
p=w/'contact-audit.json'
a=json.loads(p.read_text(encoding='utf-8-sig'))
a['status']='drawing-reviewed-ready-for-integrated-playback'
a['reviewedAt']=s['updatedAt']
a['visualObservations'][1].pop('concern',None)
a['visualObservations'][1]['transitionReview']='04-to05 retained as legitimate whole-body crouch and weapon rotation, not registered: head width remains comparable, pelvis and head lower together, spear angle changes. No single similarity transform can replace this actual pose.'
a['visualObservations'][3]['approxContactX']=[465,465]
a['visualObservations'][3]['contact']='Same low center support boot stays on forefoot; high screen-left free boot remains airborne. Frame08 raises the free knee and shows more sole as a distinct independent pose.'
a['visualObservations'][3].pop('concern',None)
a['visualObservations'][3]['transitionReview']='06-to07 support advances only about 35 pixels toward rear on 1024 canvas instead of previous 135-pixel jump. Original high-left folded free-leg ownership retained; neither ankle rolls outward.08 no longer shows old wide split before09.'
a['technicalNotes']=[
 'Contact coordinates are visual estimates in1024 and differ from prompt targets; prompt numbers are not validation.',
 'Selected07-v10 and08-v5 are independent1254 RGBA generations. Their composition matches original runtime05 including headtop and spear tip; no registration or pose interpolation was needed.',
 'Rejected07-v7/08-v3 for excessive06-to07 stride and08-to09 split.07-v8/registered and07-v9 intermediate attempts were rejected for anatomy/support-leg ambiguity; they are not selected.',
 'SE04 uses06-v4 native; old04 moves05, old05 moves06, old12 moves11, old13 moves15. Stage all unique old sources before runtime mutation.',
 'Selected frames visually retain two legs/boots, two gripping hands and the complete spear.',
 'SE16-v2 rejected upper-body rightward drift;16-v3 selected.',
 '04-to05 keeps real downstroke/crouch motion and spear rotation. Do not flatten this into an identical upper-body pose by registration.'
]
a['resolvedIssues']=['06-to07 excessive spatial jump','07/08 support-leg identity','08 wide split before09','04-to05 confirmed crouch rather than simple global scale drift']
a['notYetPassed']=['Normal-speed integrated loop and wraparound review by parent after formal export']
p.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
print('SE selection and contact audit finalized; runtime and SW untouched')
