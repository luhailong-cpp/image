from native_work import *
s=read(ZONE/'selection-r05_c10.json')
issues=[]
for ident,col,neighbors in [('r05_c10_p01_02',1,['r04_c10_p04_02']),('r05_c10_p01_04',3,['r04_c10_p04_04','r05_c11_p01_01_v3'])]:
    for a in neighbors:
        f=ZONE/'qa'/f'{a}__{ident}.json'
        if not f.exists(): f=ZONE/'qa'/f'{ident}__{a}.json'
        q=read(f)
        q.update(status='geometry_pass_material_transition_pending',reviewedAtUtc=now(),reviewer='root',geometryChecks={'pavingContours':'pass; direct 1:1 join'},material='Visible change in surface mottling/tessellation size at the exact core boundary; requires later localized correction. Not a seam pass.')
        write(f,q)
        issues.append({'id':q['seamId'],'status':'pending_material_transition','geometry':'passed','evidence':q['inspectionEvidencePath']})
    g=ZONE/'native'/f'{ident}.png.generation.json';r=read(g);r.update(status='selected_layout_candidate_material_pending',layout='paving and cropped border features follow original layout',internalSeams='remaining neighbors pending',externalSeams='geometry checked; material transition pending');write(g,r)
    s['cores'][0][col]=ident
s.update(pendingIssues=issues,formalAccepted=False,internalStatus='incomplete_material_transition_pending',updatedAtUtc=now());write(ZONE/'selection-r05_c10.json',s)
print(json.dumps({'selected':2,'materialTransitionsPending':len(issues)}))
