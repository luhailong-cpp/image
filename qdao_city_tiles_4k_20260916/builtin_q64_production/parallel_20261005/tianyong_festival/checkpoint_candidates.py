"""Carry current tile ownership forward without dropping coupled neighbors."""
from pathlib import Path
import json,hashlib
def carry(previous,current,out):
    cp={**previous,**current,'version':out.name}
    cp['coupledNeighbors']=previous.get('coupledNeighbors',{})
    cp['baselineSet']=previous.get('baselineSet')
    candidates={x['tile']:x for x in previous.get('candidateSet',[])}
    for tile,ref in cp['coupledNeighbors'].items():candidates[tile]={**ref,'tile':tile}
    candidates['r08_c10']={**cp['fragment'],'tile':'r08_c10','partialFragment':True,'formalAccepted':False}
    candidates['r09_c10']={**cp['bottom'],'tile':'r09_c10','formalAccepted':False}
    cp['candidateSet']=[candidates[k] for k in sorted(candidates)]
    p=out/'candidate-set.json';p.write_text(json.dumps({'candidates':cp['candidateSet'],'formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    cp['candidateSetRecord']={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    return cp
