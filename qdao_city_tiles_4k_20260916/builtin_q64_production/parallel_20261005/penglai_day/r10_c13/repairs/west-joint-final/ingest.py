from ai_helper import *
files={0:'exec-50c0dfe4-d115-49c4-bb07-d52702389ec3.png',1024:'exec-a066fd72-3c6e-4fc5-b33f-6b7ae154db12.png',2048:'exec-e380c320-44cd-47e1-93c4-978636065dc3.png',2842:'exec-73ff6238-35c9-4cdb-a866-8b81e6d5061b.png'}
for y,p in files.items():
 d=ingest('joint-'+str(y)+'-ai-v1',Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')/p)
 r=json.loads(Path(str(d)+'.generation.json').read_text(encoding='utf8'));r['visualInspection']={'native1254Reviewed':True,'finding':'center shared-edge tone and geometry repaired; exact mask return pending','status':'accepted_for_mask_integration'};Path(str(d)+'.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print('4 native AI sources saved with call evidence')

