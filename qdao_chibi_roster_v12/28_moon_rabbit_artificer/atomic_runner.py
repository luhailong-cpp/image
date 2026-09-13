"""Run processing scripts with atomic local PNG/GIF writes to avoid Windows preview locks."""
import io, os, runpy, sys, uuid, subprocess
from pathlib import Path
from PIL import Image
original_save = Image.Image.save

def atomic_save(image, target, format=None, **params):
    if not isinstance(target, (str, os.PathLike)):
        return original_save(image, target, format=format, **params)
    path=Path(target)
    if path.suffix.lower() not in ('.png','.gif'):
        return original_save(image,target,format=format,**params)
    chosen=format or {'.png':'PNG','.gif':'GIF'}[path.suffix.lower()]
    buffer=io.BytesIO()
    original_save(image,buffer,format=chosen,**params)
    temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    temporary.write_bytes(buffer.getvalue())
    os.replace(temporary,path)
Image.Image.save=atomic_save
original_run=subprocess.run
runner_path=str(Path(__file__).resolve())
def atomic_subprocess(command,*args,**kwargs):
    if isinstance(command,(list,tuple)) and command and Path(str(command[0])).stem.lower().startswith('python'):
        command=list(command)
        for index in range(1,len(command)):
            if str(command[index]).lower().endswith('.py') and str(command[index])!=runner_path:
                command.insert(index,runner_path)
                break
    return original_run(command,*args,**kwargs)
subprocess.run=atomic_subprocess
script=sys.argv.pop(1)
sys.path.insert(0,str(Path(script).resolve().parent))
sys.argv[0]=script
runpy.run_path(script,run_name='__main__')
