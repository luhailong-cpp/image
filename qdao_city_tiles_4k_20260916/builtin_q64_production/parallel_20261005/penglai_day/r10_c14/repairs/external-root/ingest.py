from pathlib import Path
import sys
R=Path(__file__).resolve().parent;B=R.parents[2];sys.path.insert(0,str(B));import production as p
p.ROOT=R
records=p.read(R/'evidence'/sys.argv[1])
for x in records:
    f=p.ingest(x['source'],x['name'],x['prompt'],x['call']['referenced_image_paths'],'native_joint_repair')
    rec=p.read(str(f)+'.generation.json');rec['evidence']['output_hint']=x['output_hint'];rec['evidence']['toolOutputSha256']=p.sha(x['source']);p.write(str(f)+'.generation.json',rec)
    print(x['name'],p.sha(f))
