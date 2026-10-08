from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'assembly_r07_c16.py').read_text(encoding='utf-8')
s=s.replace('r07_c16','r09_c16').replace('24576','32768').replace('south','north').replace('South','North')
old='''    common.paste(candidate.crop((0, FINAL - 128, FINAL, FINAL)), (0, 0))
    common.paste(north.crop((0, 0, FINAL, 128)), (0, 128))
    band("north-r07-r08-common-edge-full", common, "horizontal", [0, FINAL - 128, FINAL, FINAL + 128],
         [{"tile": "r09_c16", "rectXYXY": [0, 3968, 4096, 4096]},
          {"tile": "r08_c16", "rectXYXY": [0, 0, 4096, 128]}])'''
new='''    common.paste(north.crop((0, FINAL - 128, FINAL, FINAL)), (0, 0))
    common.paste(candidate.crop((0, 0, FINAL, 128)), (0, 128))
    band("north-r08-r09-common-edge-full", common, "horizontal", [0, -128, FINAL, 128],
         [{"tile": "r08_c16", "rectXYXY": [0, 3968, 4096, 4096]},
          {"tile": "r09_c16", "rectXYXY": [0, 0, 4096, 128]}])'''
assert old in s;s=s.replace(old,new)
s=s.replace('old_overlap = north.crop((0, 0, FINAL, HALO))','old_overlap = north.crop((0, FINAL-HALO, FINAL, FINAL))')
s=s.replace('new_overlap = extended.crop((HALO, HALO + FINAL, HALO + FINAL, EXTENDED))','new_overlap = extended.crop((HALO, 0, HALO + FINAL, HALO))')
s=s.replace('"rectXYXY": [0, 0, 4096, 115], "bandY": 0','"rectXYXY": [0, 3981, 4096, 4096], "bandY": 0')
s=s.replace('"rectXYXY": [115, 4211, 4211, 4326], "bandY": 128','"rectXYXY": [115, 0, 4211, 115], "bandY": 128')
s=s.replace('pixels[-1].astype(np.int16) - old[0].astype(np.int16)','pixels[0].astype(np.int16) - old[-1].astype(np.int16)')
s=s.replace('np.diff(pixels[-128:]','np.diff(pixels[:128]').replace('np.diff(old[:128]','np.diff(old[-128:]')
s=s.replace('old[:HALO].astype(np.int16) - np.asarray(extended)[HALO + FINAL:, HALO:HALO + FINAL]','old[-HALO:].astype(np.int16) - np.asarray(extended)[:HALO, HALO:HALO + FINAL]')
p=R/'assembly_r09_c16.py';assert not p.exists();p.write_text(s,encoding='utf-8')
print(p)
