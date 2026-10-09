from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'repair_r09_c16_color.py').read_text()
s=s.replace('r09_c16','r10_c16').replace("'color-match-v2'","'internal-color-match'").replace('ff169961a00d04558464d4436397938b02ac4e53fd492f7a74122b49eda53095','76171e89da5aa391e359c9c6095f3a09bf46912a8f876f0f4a059d6459b608e7')
start=s.index('    # Do not freeze a visible tonal cut');end=s.index('    diff=merged.astype',start)
s=s[:start]+'''    # Internal scope only: preserve all halo and core y<700 exactly.
    change[:815]=0
    fade=np.linspace(0,1,101,dtype=np.float32)
    fade=fade*fade*(3-2*fade)
    change[815:916]=np.rint(change[815:916].astype(np.float32)*fade[:,None,None]).astype(np.int16)
    change[4211:]=0;change[:,:115]=0;change[:,4211:]=0
    merged=np.clip(baseline.astype(np.int16)+change,0,255).astype(np.uint8)
    union=np.zeros(baseline.shape[:2],dtype=bool)
    for position in (1024,2048,3072):
        union[:,position:position+230]=True
        union[position:position+230,:]=True
    union[:815]=False;union[4211:]=False;union[:,:115]=False;union[:,4211:]=False
    a.require(np.array_equal(merged[~union],baseline[~union]),'Pixels changed outside allowed internal overlap union')
    a.require(np.array_equal(merged[:815],baseline[:815]),'Protected top700 core and north halo changed')
'''+s[end:]
start=s.index("      'northHaloUnchanged'");end=s.index("      'imageResampling'",start)
s=s[:start]+'''      'northHaloUnchanged':True,'northCore700ExactlyPreserved':True,'allHaloExactlyPreserved':True,'outsideAllowedInternalOverlapUnchanged':True,
      'northBoundaryCorrection':None,'minimumCoreY':700,'topFadeCoreRows':[700,800],
'''+s[end:]
(p/'repair_r10_c16_internal_color.py').write_text(s,encoding='utf-8')
