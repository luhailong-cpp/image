from pathlib import Path
import json,sys
char=Path(sys.argv[1])
a=json.loads((char/'sources/assembly.json').read_text(encoding='utf8'))
m=json.loads((char/'manifest.json').read_text(encoding='utf8'))
m['directional_original_sources']=a['sources']
m['source_resolution_note']='The 2048x2048 sheets are deterministic assembled layouts. Actual built-in ImageGen source native sizes are recorded per direction below. Output 512x512 frames are resampled exports, not a claim of 512 native art detail.'
m['layout_provenance']='sources/assembly.json'
m['direction_reclassification']='sources/SE-reclassification.txt' if (char/'sources/SE-reclassification.txt').exists() else None
for kind in ['cardinal','diagonal']:
 m['sources'][kind]['source']='deterministic layout assembled from built-in image_gen 2x2 directional sheets'
 m['sources'][kind]['original_sources']='sources/assembly.json'
 m['sources'][kind]['assembled_canvas_size']=m['sources'][kind].pop('native_size')
 m['sources'][kind].pop('native_cell_size',None)
m['processing_note']='Each independently generated direction uses one common isotropic scale for all four poses to match the shared body height, then the common processor uses one global scale and per-frame foot translation. No per-frame independent scaling, mirroring, rotation, repeated or synthesized animation.'
(char/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
p=char/'processing/scale-profile.json';s=json.loads(p.read_text(encoding='utf8'))
s['directional_source_normalization']=a['sources']
s['strategy']='one isotropic scale shared across all four frames of each independently generated direction, then one global scale and per-frame foot translation'
s['native_sheet_sizes']={d:r['native_size'] for d,r in a['sources'].items()}
p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf8')
print('manifest provenance supplemented',char.name)

