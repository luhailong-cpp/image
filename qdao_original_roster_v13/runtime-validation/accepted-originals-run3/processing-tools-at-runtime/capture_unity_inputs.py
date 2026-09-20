"""Read-only complete Unity input snapshots for the accepted Original roster runs."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,os
ROOT=Path(__file__).resolve().parents[1]
FOLDERS=('Assets','Packages','ProjectSettings','Library/PackageCache')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(v,msg):
 if not v:raise ValueError(msg)
def links(p,seen=None):
 p=Path(p)
 for node in (p,*p.parents):
  if seen is not None and node in seen:break
  require(not node.is_symlink() and not (hasattr(node,'is_junction') and node.is_junction()),'Linked input path: '+str(node))
  if seen is not None:seen.add(node)
def inventory(project):
 paths=[];seen=set()
 for folder in FOLDERS:
  base=project/folder;require(base.is_dir(),'Missing input folder '+folder);links(base,seen)
  for directory,dirs,files in os.walk(base,followlinks=False):
   for name in dirs:links(Path(directory)/name,seen)
   for name in files:
    p=Path(directory)/name;links(p,seen);require(p.is_file(),'Non-file input '+str(p));paths.append(p)
 return sorted(paths,key=lambda p:p.relative_to(project).as_posix())
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--compare',type=Path);a=parser.parse_args();links(a.project);project=a.project.resolve();output=a.output.resolve();require(project.is_relative_to(Path('E:/work').resolve()),'Project must be under E:/work');require((project/'ProjectSettings/ProjectVersion.txt').is_file(),'Not a Unity project');require(output.is_relative_to((ROOT/'runtime-validation').resolve()) and not output.exists(),'Snapshot output must be new under runtime-validation');require(not (project/'Temp/UnityLockfile').exists(),'Capture input snapshot only while Unity is closed')
 paths=inventory(project);rows=[];stable_stats={}
 for p in paths:
  before=p.stat();require(before.st_nlink==1,'Hard-linked input file: '+str(p));digest=sha(p);after=p.stat();require((before.st_size,before.st_mtime_ns,before.st_nlink)==(after.st_size,after.st_mtime_ns,after.st_nlink),'Input changed during hashing: '+str(p));stable_stats[p]=(after.st_size,after.st_mtime_ns,after.st_nlink);rows.append({'path':p.relative_to(project).as_posix(),'sha256':digest,'bytes':after.st_size})
 require(paths==inventory(project),'Input inventory changed during capture')
 for p,expected_stats in stable_stats.items():
  final=p.stat();require((final.st_size,final.st_mtime_ns,final.st_nlink)==expected_stats,'Previously hashed input changed before capture completed: '+str(p))
 spec=importlib.util.spec_from_file_location('publication_contract',ROOT/'tools/publish_original_roster_v13.py');pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub);by={r['path']:r for r in rows};require(all(p in by for p in pub.CODE_PATHS),'Missing actual reviewed character source')
 result={'created_utc':datetime.now(timezone.utc).isoformat(),'source':str(project),'project':str(project),'mode':'Read-only complete saved Unity input capture; no source copying or reconstruction','included_roots':list(FOLDERS),'shared_writable_links':False,'files':rows,'count':len(rows),'bytes':sum(x['bytes'] for x in rows),'reviewed_source_hashes':{p:by[p]['sha256'] for p in pub.CODE_PATHS},'capture_tool_sha256':sha(Path(__file__)),'unity_runner_sha256':sha(ROOT/'tools/run_unity_tests.ps1')}
 if a.compare:
  prior=json.loads(a.compare.read_text(encoding='utf-8-sig'));require(Path(prior['project']).resolve()==project,'Compared snapshot belongs to another project');old={r['path']:r for r in prior['files']};result['comparison']={'previous_snapshot':str(a.compare.resolve()),'previous_snapshot_sha256':sha(a.compare),'added':[by[k] for k in sorted(by.keys()-old.keys())],'removed':[old[k] for k in sorted(old.keys()-by.keys())],'changed':[{'path':k,'before_sha256':old[k]['sha256'],'after_sha256':by[k]['sha256'],'before_bytes':old[k]['bytes'],'after_bytes':by[k]['bytes']} for k in sorted(old.keys()&by.keys()) if old[k]['sha256']!=by[k]['sha256']]}
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'path':str(output),'sha256':sha(output),'count':len(rows),'bytes':result['bytes'],'comparison_counts':{k:len(result['comparison'][k]) for k in ('added','removed','changed')} if 'comparison' in result else None}))
if __name__=='__main__':main()
