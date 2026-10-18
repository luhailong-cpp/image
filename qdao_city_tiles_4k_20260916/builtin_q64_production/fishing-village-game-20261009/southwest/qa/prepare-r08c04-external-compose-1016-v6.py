from pathlib import Path
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');p=z/'qa/compose-r08c04-external-1016-v5.py';s=p.read_text()
s=s.replace("pre='external-r08c04-1016-v5'","pre='external-r08c04-1016-v6'")
s=s.replace("('d',[0,100,740,1254]),('e',[250,330,740,850]),('f',[100,100,740,740])","('d',[0,100,1200,1254]),('e',[250,330,1100,850]),('f',[100,100,1180,1100])")
s=s.replace(" yy,xx=np.mgrid[:1254,:1254];mask[(xx+box[0]>=4096)|(yy+box[1]>=4096)]=0"," # Shared native repair is applied to every affected core.")
s=s.replace(" l,t=box[:2];w=min(1254,4096-l);h=min(1254,4096-t);sel=mask[:h,:w].astype(bool);tiles['r08_c04'][t:t+h,l:l+w][sel]=new[:h,:w][sel]",''' for tile,(tx,ty) in coords.items():
  l=max(box[0],tx);t=max(box[1],ty);r=min(box[2],tx+4096);b=min(box[3],ty+4096)
  if l<r and t<b:
   sel=mask[t-box[1]:b-box[1],l-box[0]:r-box[0]].astype(bool)
   tiles[tile][t-ty:b-ty,l-tx:r-tx][sel]=new[t-box[1]:b-box[1],l-box[0]:r-box[0]][sel]''')
s=s.replace("'onlyNewTileCoreSelected':True","'sharedNativeRepair':True")
s=s.replace("'onlyNewTileCoreChanged':True","'sharedNativeRepairAcrossAffectedCores':True")
s=s.replace("for tile,a in contexts.items():trace['tiles'].append({'tile':tile,'context':png(tile+'-context-native',a),'candidate':png(tile+'-candidate-4096',tiles[tile]),'coreChanged':tile=='r08_c04'})",'''for tile,a in contexts.items():
 original=next((np.array(Image.open(t['candidate']['path']).convert('RGB')) for t in bt['tiles'] if t['tile']==tile),None)
 if original is None:original=np.array(Image.open(se).convert('RGB'))[115:4211,115:4211]
 diff=np.any(tiles[tile]!=original,axis=2);ys,xs=np.where(diff);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
 if tile in ['r08_c05','r09_c05']:assert np.array_equal(tiles[tile][:,-230:],original[:,-230:]),'c06 shared edge rollback'
 trace['tiles'].append({'tile':tile,'context':png(tile+'-context-native',a),'candidate':png(tile+'-candidate-4096',tiles[tile]),'coreChanged':bool(len(xs)),'changedPixelCount':int(len(xs)),'actualPixelChangeBbox':bbox,'c06SideLast230Unchanged':True if tile in ['r08_c05','r09_c05'] else None})''')
out=z/'qa/compose-r08c04-external-1016-v6.py';assert not out.exists();out.write_text(s)

