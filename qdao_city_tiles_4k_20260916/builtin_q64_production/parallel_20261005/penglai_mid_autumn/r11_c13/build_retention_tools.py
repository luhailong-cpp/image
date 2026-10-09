from pathlib import Path
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_mid_autumn');source=R/'r09_c15';target=R/'r11_c13'
s=(source/'prepare_retention.py').read_text().replace('r09_c15','r11_c13')
s=s.replace('818a33e706b2db98c0404701f8e3f7cbf21bf7f1f9000905a22ee59c2b5ea2ef','1aa087f96cf986582881560436fb3fba780cbcbe13f3b29a133e4eb9c0ece180')
s=s.replace("night=Path(read(T/'plan.json')['nightStructure']['file'])","night=Path(read(T/'plan.json')['nightStructure'])")
s=s.replace("structure-water-fixed","structure-canopy-corrected")
s=s.replace("qa/north-no-neighbor-unverified.png","qa/west-no-neighbor-unverified.png").replace("Current north boundary inspection; absent neighbor","Current west boundary inspection; absent neighbor")
s=s.replace("Current unrotated actual-W context or repaired paving detail;33 covered view items use these pixels.","Current unrotated actual-north context; passed final view records use these exact pixels.")
start=s.index("for name in ['proposed-joint-v19.png'")
end=s.index("assembly=read",start)
s=s[:start]+s[end:]
start=s.index("# Keep the final effective fields")
end=s.index("for key,uses in extbinary.items()",start)
s=s[:start]+"""keep(T/'references/day-structure-snapshot.png','current_design','Current same-frame shared daytime layout design snapshot paired with the approved night design; preserve this unique current design.')
keep(T/'references/north-native320.png','current_required_source','Current exact frozen320px north support from finalized r10_c13. Keep this local source and preserve the external canonical north file untouched.')
keep(T/'references/canopy-planning-selection-mask.png','current_design_mask','Actual canopy selection mask used in the current approved night design; retained with design TEXT.')
"""+s[end:]
s=s.replace("currentSharedDayDesignOutsideScope=read(T/'plan.json')['sharedDayStructure']","currentDayDesignSnapshot=read(T/'plan.json')['sharedDayStructureSource']")
s=s.replace("Current standard native QA derived from818a33 final","Current standard native QA derived from1aa087 final")
s=s.replace("immutable original assembly plus approved local repair provenance","immutable original assembly and actual-neighbor provenance")
s=s.replace("old rejected sky design","superseded design")
s=s.replace("Current applied-v19 QA and effective fields retained.","Current final QA and effective fields retained.")
s=s.replace("Current4096 game candidate with27 required native QA passed, immutable original assembly and actual-neighbor provenance.","Current4096 game candidate with27 required native QA passed; protect final as source for future r11_c14 west context.")
assert not (target/'prepare_retention.py').exists()
(target/'prepare_retention.py').write_text(s,encoding='utf-8')
script=(source/'execute-retention.ps1').read_text().replace('r09_c15','r11_c13')
assert not (target/'execute-retention.ps1').exists()
(target/'execute-retention.ps1').write_text(script,encoding='utf-8')

