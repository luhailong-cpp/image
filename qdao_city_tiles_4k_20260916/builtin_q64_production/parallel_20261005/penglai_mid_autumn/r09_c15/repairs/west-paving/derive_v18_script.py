from pathlib import Path
p=Path(__file__).parent;s=(p/'build_v17_endpoint_proposal.py').read_text().replace('v17','v18')
s=s.replace('tone=transportedTone*weight[:,:,None]*owner[:,:,None]','tone=transportedTone*weight[:,:,None]*owner[:,:,None]*smooth((659-xx)/32)[:,:,None]')
s=s.replace("('measuredSlopeProfile',slope)","('measuredSlopeProfile',slope),('toneDepth32',smooth((659-xx)/32))")
s=s.replace('no horizontal row strip copying.','no horizontal row strip copying. High-gradient color endpoint correction has only32px horizontal support.')
(p/'build_v18_endpoint_proposal.py').write_text(s)

