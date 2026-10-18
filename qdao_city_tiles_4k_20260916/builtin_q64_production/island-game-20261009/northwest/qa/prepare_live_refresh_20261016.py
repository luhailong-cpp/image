from pathlib import Path
Z=Path(__file__).resolve().parents[1]
p=Z/'refresh_live_progress_20261016.py'
s=(Z/'refresh_live_progress_20261013.py').read_text(encoding='utf8')
s=s.replace("active_root='r07_c03'", "active_root='r03_c01'")
s=s.replace("Complete r07c03 roof/door/plaster native repair QA, r05c02 cauldron repair, r07c04 missing cores, and r05/r06 cross railing closure; then advance retained coordinates along verified edges.", "Complete r07c04 v6 changed-native checks and r06c02 remaining cores; continue r03c01 coastline. r07c03 one eave offset deferred after two ineffective attempts. Cross r05/r06 geometry17 passed, paving material and r06/r07 outer boundary pending.")
s=s.replace("Current owner-pinned candidates recorded; r05c02/r06c04/r07c03 internal repairs and connected outer boundaries remain pending.", "Current owner-pinned candidates recorded; r05c02 v5 internal33 independently passed. r07c03 eave offset, r06c04 paving material, and connected outer boundaries remain pending. r07c04 and r06c02 advance per explicit owner pins.")
assert not p.exists()
p.write_text(s,encoding='utf8')
print(p)
