from pathlib import Path
import json
Z=Path(__file__).resolve().parent;s=Z/'west-current-selection-20261012.json';d=json.loads(s.read_text())
assert not any(x['tileId']=='r07_c02' for x in d['partialTiles'])
d['partialTiles'].append({'tileId':'r07_c02','selectedNativeStems':[],'selectedNative':[],'nativeCount':0,'inflightStems':['r07_c02_s01_01_a01','r07_c02_s01_04_a01'],'status':'0of16_first_wave_inflight','northAnchor':d['currentTile']['candidate'],'rightAnchor':{'path':str((Z/'tiles/r07_c03_candidate-v7_4096.png').as_posix()),'sha256':'ca295176c0b35366814428d79240195b8afa7e679fd6c74b4711f5e82b13fc53'}})
s.write_text(json.dumps(d,indent=2)+'\n')

