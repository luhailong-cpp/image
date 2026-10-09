from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent));import production as p
O=R/'repairs/internal';p.ROOT=O
name=sys.argv[2];call=p.read(O/'prompts'/f'{name}.call.json');dest=p.ingest(sys.argv[1],name,O/'prompts'/f'{name}.prompt.txt',call['referenced_image_paths'],'native_joint_repair');rec=p.read(str(dest)+'.generation.json');rec['submittedParameters'].update(call);rec['evidence']['toolOutputHintFile']=str(O/'evidence'/f'{name}.tool-result.json');p.write(str(dest)+'.generation.json',rec);print(dest)

