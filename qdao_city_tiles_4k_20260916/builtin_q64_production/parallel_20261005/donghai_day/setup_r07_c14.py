from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'prepare_r07_c15.py').read_text(encoding='utf-8')
s=s.replace('r07_c15','r07_c14').replace('r08_c15','r08_c14').replace('57344','53248')
s=s.replace("('east','r07_c16'),('west','r07_c14')","('east','r07_c15'),('west','r07_c13')")
s=s.replace('with clamped right-edge guidance beyond map bounds','at exact global extent')
(R/'prepare_r07_c14.py').write_text(s,encoding='utf-8')
s=(R/'production_r07_c15.py').read_text(encoding='utf-8').replace('r07_c15','r07_c14')
start=s.index('    # Exact adjacent native context');end=s.index('    for rr,cc',start)
s=s[:start]+s[end:]
start=s.index('    prompt=',s.index('def prepare_structure():'));end=s.index("    save_prompt('local-structure'",start)
s=s[:start]+"    prompt='Edit IMAGE 1 only. Structural reference from an existing bright Q-style fishing-village map. Preserve the exact crop, camera and all pictured silhouettes, object footprints and real shadows. Clarify only the existing forms with rounded bright clean hand-painted volumes, matching IMAGE 2 as the primary confirmed style reference. Do not invent or remove objects, change positions, enlarge framing or add texture to empty water. Keep water calm cyan with broad low-contrast shading; preserve real object reflections. No characters, text, UI, border or zoom. One opaque native1254 square. This is structural guidance only, not final HD pixels.'\n"+s[end:]
s=s.replace("    if row==4:checked_neighbor('south')","    if row==4:checked_neighbor('south')\n    if column==4:checked_neighbor('east')")
start=s.index("    prompt='''",s.index('def prepare(row,column):'));end=s.index('    save_prompt(f',start)
s=s[:start]+'''    prompt="""Use case: precise-object-edit. Edit IMAGE 1 only: a native crop of the bright clean rounded fishing-village game map. Repaint the soft reference interior into clear native hand-painted art while preserving its exact camera, crop, every pictured object, silhouette, angle, scale and real shadow. IMAGE 2 is the PRIMARY confirmed style: rounded full forms, warm clean timber, clear large material planes and restrained detail. Any water remains quiet cyan with broad low-contrast shading. Preserve existing contact highlights and reflections; add no microtexture, caustic nets, new waves, grain, cracks or small repeated patterns. No extra objects, decorations, ropes or plank joints. Sharp strips are actual completed neighboring pixels: keep their geometry and color, continue existing objects naturally across their boundary. Strip boundary is not a physical line. Neighbor geometry takes precedence over conflicting soft interior; reconcile the interior to the exact neighboring shapes. Do not leave a pasted collage boundary. One opaque native1254x1254 square, same field of view, no crop, zoom, text, UI, border, character, artificial sharpen or blur filter."""
    if row==4:prompt+=' Bottom115 pixels are the fixed completed south tile; continue every object and boundary upward accurately from this anchor.'
    if column==4:prompt+=' Right115 pixels are the fixed completed east tile; continue every object and boundary leftward accurately from this anchor.'
''' + s[end:]
(R/'production_r07_c14.py').write_text(s,encoding='utf-8')
s=(R/'assembly_r07_c15.py').read_text(encoding='utf-8').replace('r07_c15','r07_c14').replace('r08_c15','r08_c14').replace('57344','53248')
(R/'assembly_r07_c14.py').write_text(s,encoding='utf-8')
print('Prepared r07_c14 isolated tools')
