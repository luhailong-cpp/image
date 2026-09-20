from pathlib import Path
p=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tianyong_festival')
s=(p/'assemble_triple.py').read_text(encoding='utf-8')
for a,b in [
("triple_r10_c07_c09","quad_r10_c07_c10"),
("root/'r10_c09/assemble_builtin.py'","root/'r10_c10/assemble_builtin.py'"),
("root/'pair_r10_c07_c08/output_v4/extended-context.png'","root/'triple_r10_c07_c09/output_v3/extended-context.png'"),
("root/'r10_c09/output/extended-context.png'","root/'r10_c10/output/extended-context.png'"),
("join_c08_c09","join_c09_c10"),
("(4326,12518,3)","(4326,16614,3)"),
("(115,115,12403,4211)","(115,115,16499,4211)"),
("triple_12288x4096_candidate.png","quad_16384x4096_candidate.png"),
("(7,8,9)","(7,8,9,10)"),
("(1800,600)","(2000,500)"),
("8192-627","12288-627"),("8192+627","12288+627"),
("8192+1024,8192+2048,8192+3072","12288+1024,12288+2048,12288+3072"),
("'nativeBaseSources':48","'nativeBaseSources':64"),
("[12288,4096]","[16384,4096]"),("[12518,4326]","[16614,4326]")
]:s=s.replace(a,b)
(p/'assemble_quad.py').write_text(s,encoding='utf-8')
