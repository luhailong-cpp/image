from pathlib import Path
import json,sys,subprocess
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent));import archive_generation as a
job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
print(json.dumps(a.finalize(job['batch'],job['original'],job['tool_result'])))
subprocess.run([sys.executable,'-B',str(HERE.parent/'import_frame.py'),'--archive',str(HERE.parent.parent/'06-generation'/job['batch']),'--batch-id',job['batch'],'--direction',job.get('direction','NW'),'--frame',str(job['frame']),'--staging-root',str(HERE)],check=True)
