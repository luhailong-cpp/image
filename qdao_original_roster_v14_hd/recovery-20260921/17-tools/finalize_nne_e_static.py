from pathlib import Path
import base64, hashlib, json
import numpy as np
from PIL import Image
from common import HERE, GEN, now, sha

out = HERE / 'nne-e-static-review-v2'
rows = json.loads((out / 'validated-selection-rows.json').read_text(encoding='utf8'))
log = Path(r'C:/Users/Administrator/.codex/sessions/2026/09/21/rollout-2026-09-21T12-00-01-01a0c4b2-1ac3-7380-9bc1-dd41a5fbe468.jsonl')
north = {r['source_record']['source']['sha256']:r for r in rows if r['path'].startswith('walk/N/') or r['path']=='idle/N.png'}
evidence = []
for line in log.open(encoding='utf8'):
    event = json.loads(line)
    item = event.get('payload', {}).get('item', {})
    if item.get('kind') != 'image_gen.generation': continue
    digest = hashlib.sha256(base64.b64decode(item.get('result',''))).hexdigest()
    if digest not in north: continue
    row = north[digest]
    archive = GEN / row['selected_revision']
    request = json.loads((archive/'request.json').read_text(encoding='utf8'))
    archived = request['actual_request']['prompt']
    returned = item.get('revisedPrompt')
    assert returned == archived or returned == archived.rstrip('\n')
    supplement = {
        'schema':1, 'recordedAt':now(), 'slot':row['path'], 'source_sha256':digest,
        'session_log':str(log), 'event_ordinal':event.get('ordinal'), 'event_timestamp':event['timestamp'],
        'event_result_bytes_equal_archived_raw':True,
        'host_event_metadata':{k:v for k,v in item.items() if k!='result'},
        'archived_request_prompt_sha256':hashlib.sha256(archived.encode('utf8')).hexdigest(),
        'host_returned_revised_prompt_sha256':hashlib.sha256(returned.encode('utf8')).hexdigest(),
        'archived_prompt_exactly_matches_host_returned_prompt':returned==archived,
        'difference':'none' if returned==archived else 'Archive contains one extra trailing LF; host returned revisedPrompt does not.',
        'actual_submission_limit':'Historical functions call used an in-memory prompt expression. This supplement preserves exact host-returned revisedPrompt and raw completion evidence; it does not relabel that returned field as a directly captured resolved request argument.',
        'original_records_modified':False, 'actual_model':None,'actual_quality':None,
    }
    target=archive/'session-evidence-nne-final.json'
    assert not target.exists(), target
    target.write_text(json.dumps(supplement,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    evidence.append({'slot':row['path'],'supplement':str(target),'sha256':sha(target),'exact_prompt_match':returned==archived})

bykey={r['path']:r for r in rows}
gifs=[]; numerical={}
for direction in ('N','NE','E'):
    walk=[bykey[f'walk/{direction}/{n:02d}.png'] for n in range(1,17)]
    heights=[r['subject_height_native_px'] for r in walk]
    scales=[r['body_scale'] for r in walk]
    numerical[direction]={
        'walk_count':16,'idle_count':1,'walk_height_min_max':[min(heights),max(heights)],
        'body_scale_cv':float(np.std(scales)/np.mean(scales)),
        'idle_walk_height_drift':abs(bykey[f'idle/{direction}.png']['subject_height_native_px']/float(np.mean(heights))-1),
        'top_y_by_frame':[943-h for h in heights],
    }
    for mode,color in [('dark',(30,38,46)),('light',(240,238,228))]:
        frames=[]
        for row in walk:
            im=Image.open(row['source']).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
            bg=Image.new('RGB',(512,512),color);bg.paste(im,(0,0),im);frames.append(bg)
        gif=out/f'{direction}-30ms-{mode}.gif'
        frames[0].save(gif,save_all=True,append_images=frames[1:],duration=[30]*16,loop=0,optimize=False,disposal=2)
        with Image.open(gif) as check:
            durations=[]
            for n in range(check.n_frames):check.seek(n);durations.append(check.info['duration'])
            assert check.n_frames==16 and durations==[30]*16
        gifs.append({'path':str(gif),'sha256':sha(gif),'frames':16,'durations_ms':durations,'cycle_ms':480})

report={
    'character_id':'17_ghost_script_calligrapher_boy','scope':['N','NE','E'],'recordedAt':now(),
    'selection_file':str(out/'selections.json'),'selection_sha256':sha(out/'selections.json'),
    'walk_count':48,'independent_idle_count':3,'unique_native_source_count':51,
    'native_size':[1254,1254],'final_size':[1024,1024],'final_format':'RGBA PNG',
    'all_exact_anchors':[512,942],'no_duplicate_source_cells':True,'no_exact_pixel_duplicates_or_mirrors':True,
    'static_visual_review':{'performed':True,'backgrounds':['dark RGB 30,38,46','light RGB 240,238,228'],
        'normal_cell_size':[512,512],'enlarged_cell_size':[1024,1024],
        'coverage':'All 51 selected images viewed on both backgrounds in normal and enlarged contact views; seams 15,16,01,02 viewed on both backgrounds.',
        'result':'Static candidates accepted for dynamic review; no visible crop, isolated solid background remnants, incorrect prop hand, or identity break found.',
        'directions':{
            'N':'08-v2 and 10-v2 recovered from old completed generation events, then imported. Opposite contacts at 01/09, support/swing exchange at 05/13; 14-v2 retained. Seam maintains right-forward contact progression.',
            'NE':'06-v2,09-v3,13-v3 retained. Opposite-leg contact and passing poses visible. Top-of-hair differences around 02/04 and 12→13 remain dynamic review targets, not silently declared smooth.',
            'E':'10-v4 independently generated to restore the rear near-side/right boot below and larger than forward far-side/left boot. 13-v1 reviewed enlarged: raised passing foot with opposite support, no definite high kick; retained. Dynamic 09→10→11 and 12→13→14 still require playback judgment.'}},
    'numerical_by_direction':numerical,'gif_timing_checks':gifs,
    'source_evidence_supplements':evidence,
    'historical_prompt_note':'14 original selected N sources were archived with one additional trailing LF relative to the exact host-returned revisedPrompt. Original files and hashes remain unchanged; supplements preserve exact returned prompt and completed result evidence. N14-v2 exact matches. N08-v2/N10-v2 separately recovered exact request/returned prompt matches.',
    'new_generation_calls_this_subtask':1,'recovered_existing_completed_images':2,'paid_api_calls':0,
    'actual_model':None,'actual_quality':None,'host_managed_model_quality_unconfirmed':True,
    'dynamic_browser_review':False,'formal_animation_approval':False,'client_integration':False,
    'pending_root_checks':['30 ms playback, dark/light, normal/enlarged','NE 02/04 and 12→13 vertical bob','E 09→10→11 depth and E13 passing','all direction seam playback']
}
(out/'static-qa-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'selected':len(rows),'source_supplements':len(evidence),'gifs':len(gifs),'numerical':numerical},ensure_ascii=False,indent=2))
