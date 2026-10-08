from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'prepare_r07_c16.py').read_text(encoding='utf-8').replace('r07_c16','r07_c15').replace('r08_c16','r08_c15').replace('61440','57344')
s=s.replace('extended=Image.fromarray(np.pad(rgb,((0,0),(0,4),(0,0)),mode=\'edge\'))','extended=Image.fromarray(rgb)')
s=s.replace("for direction,identity in [('south','r08_c15'),('west','r07_c15')]:","for direction,identity in [('south','r08_c15'),('east','r07_c16'),('west','r07_c14')]:")
start=s.index('    border=');end=s.index('    neighbors={}',start)
s=s[:start]+"    border={'mapBounds':[0,0,65536,65536],'requestedGlobalBox':global_box,'extendsBeyondMap':False,'referenceOnly':True,'finalCorePixelsNotPadded':True,'finalArtUpscaled':False}\n"+s[end:]
p=R/'prepare_r07_c15.py';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(R/'production_r07_c16.py').read_text(encoding='utf-8').replace('r07_c16','r07_c15')
start=s.index('    if column==4:record');end=s.index('    p.savej',start);s=s[:start]+s[end:]
start=s.index('    prompt=',s.index('def prepare_structure():'));end=s.index("    save_prompt('local-structure'",start)
s=s[:start]+"    prompt='Edit IMAGE 1 only. Preserve the exact camera, framing, every existing pictured object and silhouette. Clarify the existing forms in the rounded clean hand-painted style of IMAGE 2, without moving anything or inventing objects. Keep water calm and low contrast. No text, UI, border or resize. One opaque native1254 square. Structural reference only.'\n"+s[end:]
s=s.replace("    if column==4:prompt+=' The outermost right 115 pixels are out-of-map continuation context and will be excluded from the final core.'\n",'')
p=R/'production_r07_c15.py';assert not p.exists();p.write_text(s,encoding='utf-8')
print('r07c15 tools prepared')
