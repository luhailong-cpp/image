from publish_v9_edges import *
now=datetime.now(timezone.utc).isoformat()
assert not (HERE/'publication.json').exists()
stage=read(HERE/'stage.json')['records'];sources=[r for r in stage if r['path'].startswith('q_daoist_character_pack_4096/')];needs={r['path'] for r in sources};assert len(sources)==19
initial=read(ROOT/'qdao_festival_refinement_20260910/reviews/v9-pets-style-review.json');m=read(V9/'manifest.json');prep_before=read(HERE/'before/qdao_character_diversity_v9/prepared_sync.json')
hero=next(r for r in stage if r['character_id']=='hero1024');canonical=next(r for r in sources if r['path'].endswith('/00_reference_topright_boy_transparent_4096.png'))
pub=[]
for r in sources:
 assert sha(ROOT/r['path'])==r['output_sha256'] and sha(ROOT/r['before_path'])==r['source_sha256'];contract(ROOT/r['before_path'],ROOT/r['path'])
 pub.append({**r,'kind':'v9_source','status':'published','published_utc':now,'visual_review':'qdao_festival_refinement_20260910/v9-edges/visual-approval.json'})
hc=read(ROOT/'qdao_asset_refresh_v6/hero_compat_manifest.json')
for r in hc['assets']:
 f=ROOT/r['path'];assert sha(f)==canonical['output_sha256']
 if r['path'] not in needs:pub.append({'path':r['path'],'kind':'verified_hero_4096_alias','status':'published','source_sha256':canonical['source_sha256'],'output_sha256':sha(f),'before_path':rel(HERE/'before'/r['path']),'canonical':canonical['path'],'visual_review':'qdao_festival_refinement_20260910/v9-edges/visual-approval.json',**contract(HERE/'before'/r['path'],f)})
assert sha(ROOT/hero['path'])==hero['output_sha256'];pub.append({**hero,'kind':'hero_1024_fixed_canvas','status':'published','visual_review':'qdao_festival_refinement_20260910/v9-edges/hero1024-visual-approval.json'})
prepared=read(V9/'prepared_sync.json');oldprep={r['output']:r for r in prep_before['records']};changed=[]
for row in prepared['records']:
 p=ROOT/row['output'];old=HERE/'before'/row['output']
 stats=contract(old,p,allow_hidden=True)
 if sha(old)!=sha(p):
  changed.append({'path':row['output'],'kind':'prepared_1024','status':'published','source':row['source'],'current_4096_source_sha256':row['source_sha256'],'source_sha256':sha(old),'output_sha256':sha(p),'before_path':rel(old),'method':'Full RGBA LANCZOS resample of reviewed current 4096 source; pre/post Alpha exact',**stats})
 else:assert stats['changed_rgb_pixels']==0
assert len(changed)==17
pub.extend(changed)
prepared['current_refinement']={'date_utc':now,'changed':17,'retained':5,'all_alpha_unchanged':True,'report':'qdao_character_diversity_v9/festival_edge_refinement.json'}
dump(V9/'prepared_sync.json',prepared)
op=V9/'build_overview.py';txt=op.read_text(encoding='utf-8');txt=txt.replace('00 与额外主角参考保持原样','00 与额外主角参考造型保留');op.write_text(txt,encoding='utf-8')
subprocess.run([sys.executable,'-B',str(op)],cwd=ROOT,check=True)
# Stop legacy entry points from replacing fixed-canvas refinements or falsifying historical QA.
for p in [V9/'build_manifest.py',ROOT/'qdao_asset_refresh_v6/build_hero_compat.py']:
 txt=p.read_text(encoding='utf-8');needle='def main():\n'
 guard="def main():\n    current = Path(__file__).resolve().parents[1] / 'qdao_character_diversity_v9/festival_edge_refinement.json'\n    if current.exists():\n        import runpy\n        runpy.run_path(str(current.parent.parent / 'qdao_festival_refinement_20260910/v9-edges/verify_current.py'), run_name='__main__')\n        return\n"
 assert needle in txt;txt=txt.replace(needle,guard,1);p.write_text(txt,encoding='utf-8')
report={'status':'published','completed_utc':now,'source_count':19,'prepared_count':17,'hero_aliases_outside_v9':7,'hero_fixed_canvas_1024':1,'changed_png_count':len(pub),'all_alpha_unchanged':True,'all_canvas_and_identity_preserved':True,'actual_client_written':False,'new_art_generation':False,'historical_visual_qa_unchanged_sha256':sha(V9/'visual_qa.json'),'review':'qdao_festival_refinement_20260910/v9-edges/current-visual-review.json','review_sha256':sha(HERE/'current-visual-review.json'),'publication':'qdao_festival_refinement_20260910/v9-edges/publication.json','method':'Local same-image RGB donor fitting at transparent boundary; current canvases and all Alpha bytes preserved. Protected original purple characters/pet fur retained.'}
dump(HERE/'publication.json',{'status':'published','published_utc':now,'count':len(pub),'records':pub,'retained_files':[{'path':r['path'],'sha256':r['sha256']} for r in initial['files'] if r['status']=='retained'],'overview':{'path':rel(V9/'roster_overview.png'),'sha256':sha(V9/'roster_overview.png'),'method':'Existing deterministic roster composition from current 22 source portraits'}})
report['publication_sha256']=sha(HERE/'publication.json');dump(V9/'festival_edge_refinement.json',report)
valid=read(V9/'validation.json');valid['current_validation_utc']=now;valid['visual_review']='passed; current hashes match v9-edges/current-visual-review.json; visual_qa.json remains historical'
valid['festival_edge_refinement']={'report':'qdao_character_diversity_v9/festival_edge_refinement.json','report_sha256':sha(V9/'festival_edge_refinement.json'),'all_current_hashes_match':True,'all_alpha_unchanged':True,'changed_source_count':19,'prepared_count':17}
valid['reviewed_color_candidates']=sum(r['strong_chroma_candidates'] for r in m['assets']);dump(V9/'validation.json',valid)
comp=read(V9/'completion.json')
for row in comp['artifacts']:row['sha256']=sha(V9/row['path'])
comp['refinement_completed_utc']=now;comp['current_refinement']='festival_edge_refinement.json';comp['artifacts'].append({'path':'festival_edge_refinement.json','sha256':sha(V9/'festival_edge_refinement.json')});dump(V9/'completion.json',comp)
follow=read(V9/'followup_completion.json')
for row in follow['artifacts']:
 if row['path'] in ['qdao_character_diversity_v9/prepared_sync.json','qdao_character_diversity_v9/sync_prepared.py']:row['sha256']=sha(ROOT/row['path'])
follow['portrait_refinement_completed_utc']=now;follow['portrait_refinement_record']='qdao_character_diversity_v9/festival_edge_refinement.json';dump(V9/'followup_completion.json',follow)
print(json.dumps({'status':'published','png_count':len(pub),'sources':19,'prepared':17,'other_hero_aliases':7,'hero1024':1,'overview_refreshed':True}),flush=True)
