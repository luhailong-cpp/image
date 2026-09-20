from pathlib import Path
p=Path(r'E:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\tianyong_festival\quad_r10_c07_c10')
s=(p.parent/'triple_r10_c07_c09/apply_repairs_v3.py').read_text()
s=s.replace("out=p/'output_v3';qa=p/'qa_v3'","out=p/'output_v2';qa=p/'qa_v2'").replace("source=p/'output_v2/extended-context.png'","source=p/'output/extended-context.png'").replace("r=p/'repairs/v3'","r=p/'repairs/v2'")
start=s.index('placements=');end=s.index('\ntouched=',start)
s=s[:start]+"placements={'boundary_lower':{'box':(11661,2048,12915,3302),'roi':(350,630,1030,1254)},'stairs_boundary':{'box':(11661,2842,12915,4096),'roi':(330,0,1040,1254)}}"+s[end:]
for a,b in [("(115,115,12403,4211)","(115,115,16499,4211)"),("triple_12288x4096_candidate.png","quad_16384x4096_candidate.png"),("(7,8,9)","(7,8,9,10)"),("(1800,600)","(2000,500)"),("[12288,4096]","[16384,4096]"),("assembly_v3.json","assembly_v2.json")]:s=s.replace(a,b)
(p/'apply_repairs_v2.py').write_text(s,encoding='utf-8')
