from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'prepare_r07_c16.py').read_text(encoding='utf-8')
s=s.replace('r07_c16','r09_c16').replace('r07_c15','r09_c15').replace('24576','32768').replace('south','north').replace('South','North').replace('nativeBottomRowRequires','nativeTopRowRequires').replace('native top row allowed','native bottom row allowed')
s=s.replace('immediately north of r08_c16','immediately south of r08_c16')
p=R/'prepare_r09_c16.py';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(R/'production_r07_c16.py').read_text(encoding='utf-8')
s=s.replace('r07_c16','r09_c16').replace('south','north').replace('bottom row','top row').replace('row==4:checked_neighbor','row==1:checked_neighbor')
start=s.index('    prompt=',s.index('def prepare_structure():'));end=s.index("    save_prompt('local-structure'",start)
s=s[:start]+"    prompt='Edit IMAGE 1 only. Preserve the exact camera, framing, calm blue water and every existing pictured silhouette. Render pictured objects cleanly in the confirmed rounded hand-painted style of IMAGE 2. Keep the open water quiet with broad soft low contrast blue and cyan shading; add no ripples, lattice, foam or objects. No text, no UI, no borders. One opaque native1254 image. This is a local layout structure reference only.'\n"+s[end:]
p=R/'production_r09_c16.py';assert not p.exists();p.write_text(s,encoding='utf-8')
print('prepared r09 wrappers')
