from repair import *
import numpy as np
gen=Image.open(R/'repair-v2.png').convert('RGB')
strip=gen.crop((627,115,830,1139)); strip.save(R/'candidate-right-native.png')
derived(R/'candidate-right-native.png',[R/'repair-v2.png'],{'method':'exact native crop','sourceBoxLTRB':[627,115,830,1139],'globalRectXYWH':[49152,32768,203,1024],'resampling':None,'status':'not_accepted_residual_edge_mismatch'})
old=np.array(Image.open(R/'target-native.png'))
joined=np.array(Image.open(R/'joined-v3.png'))
report={'createdAt':now(),'status':'unresolved_do_not_integrate_as_passed','formalAccepted':False,'checkedAtNativeScale':True,'checkedFullSharedEdgeGlobalY':[32768,33792],'checkedFullReplacementRightBoundaryGlobalY':[32768,33792],'nativeQA':str(R/'qa-both-edges-v3.png'),'currentPreview':str(R/'joined-v3.png'),'bestUniqueAIRepair':str(R/'repair-v2.png'),'proposedCandidateStrip':str(R/'candidate-right-native.png'),'placement':{'globalRectXYWH':[49152,32768,203,1024],'c13LocalRectXYWH':[0,0,203,1024],'p11RectXYWH':[115,115,203,1024],'generatedSourceCropLTRB':[627,115,830,1139],'hardMask':str(R/'mask-v1.png'),'feather':0,'resampling':None},'baseline':{'file':str(BASE),'sha256':sha(BASE),'matchesHandoff':sha(BASE)==H['baselineCandidates'][-1]['sha256'],'unchangedInJoinedPreview':bool(np.array_equal(old[:,:627],joined[:,:627]))},'farRightContextUnchanged':bool(np.array_equal(old[:,830:],joined[:,830:])),'fixed':['Duplicate thin wooden post removed by built-in AI redraw.','Adjacent foundation/step turn reconstructed with one broad doorway post.'],'remaining':['Upper wooden rail has approximately12px height mismatch at immutable x627 edge: old edge gradient y170, generated y182 in1254 crop.','Stone bevel at y603/606 remains approx3px mismatch.','Stone lower turn y738/740 approx2px mismatch and y886/883 approx-3px mismatch.','Subtle luminance and painted-detail discontinuity at hard x627 edge and right replacement boundary.','Bottom boundary of replacement at tile y1024 must be reviewed against next patch; this candidate is not accepted.'],'rejectedRegistration':{'record':str(R/'registration-v2.json'),'reason':'Large variable displacement -13.78..16px bends upper rail, exceeds bounded6px intent; do not integrate.','parametersAndFieldRetained':True},'nextAction':'Targeted AI redraw using an explicit gap/mask may be needed; do not enlarge registration or blur to hide geometry.'}
write(R/'repair-status.json',report)
cleanup=[]
for name in ['joined-v1.png','qa-both-edges-v1.png','registered-v1.png','joined-v2.png','qa-both-edges-v2.png']:
    p=R/name
    if p.exists():
        cleanup.append({'file':str(p),'sha256':sha(p),'reason':'rejected or superseded derived inspection image; text provenance retained'})
        # Validate exact target is confined to owned folder before deleting.
        assert p.resolve().parent==R.resolve()
        p.unlink()
write(R/'cleanup.json',{'createdAt':now(),'deletedImages':cleanup,'retained':'Best AI candidate, native target inputs needed by current in-progress provenance, current joined preview, current QA, binary mask, numerical correction field and all text records.'})
