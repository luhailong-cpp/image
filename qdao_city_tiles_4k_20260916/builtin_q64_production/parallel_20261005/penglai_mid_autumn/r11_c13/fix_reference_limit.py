from prepare_structure import *
call=read(F/'night-structure.call.json');req=read(F/'night-structure.request.json')
assert len(call['referenced_image_paths'])==6
write(E/'night-structure-rejected-six-reference-call.json',call)
write(E/'night-structure-rejected-six-reference-request.json',req)
write(E/'night-structure-reference-limit-failure.json',dict(at=now(),tool='image_gen.imagegen',error='referenced_image_paths must contain at most 5 paths',generationStarted=False,outputReturned=False,correctiveAction='Remove redundant original coarse night color reference; actual native night context remains attached.'))
old='Image5 is the original whole-map NIGHT context for lighting only. Image6 is the PRIMARY APPROVED art style only:'
assert old in call['prompt'];call['prompt']=call['prompt'].replace(old,'Image5 is the PRIMARY APPROVED art style only:')
del call['referenced_image_paths'][4];del req['references'][4]
Path(req['prompt']).write_text(call['prompt'],encoding='utf-8')
req.update(startedAt=now(),promptSha256=sha(req['prompt']),submittedParameters=dict(model=None,quality=None,**call),priorRejectedRequest=str(E/'night-structure-rejected-six-reference-request.json'))
write(F/'night-structure.call.json',call);write(F/'night-structure.request.json',req)
print('Corrected to five actual attached references')
