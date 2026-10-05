import json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat()
before={f['slot']:f for f in read(P/'before-manifest.json')['frames']}
reason='原13支撑靴白鞋头向屏幕右侧横钩；v2只调整靴前半部及鞋底后侧透视，白鞋头收为远侧窄边，沿NE进深；保留自然抬跟、前掌接触、膝踝和主体位置。'
for n,v,accepted,note in [('13',1,False,'虽略收窄，仍保留侧向L形鞋尖，拒用。'),('13',2,True,reason),('15',1,False,'鞋尖横钩未有实质改善，拒用；根任务已将NE15重试唯一交给full_run_north。')]:
 native=ROOT/f'generation/limbs-20261004/feet-northeast/NE-{n}-v{v}.png'
 side=Path(str(native)+'.generation.json');r=read(side)
 for ref in r['references']:
  p=Path(ref['path']);ref['sha256']=sha(p)
 r['editInput']={'file':before[f'run/NE/{n}']['file'],'sha256':before[f'run/NE/{n}']['sha256'],'historicalManifest':'provenance/limbs-20261004/before-manifest.json','historicalManifestSha256':sha(P/'before-manifest.json'),'generationRecord':before[f'run/NE/{n}']['derivedFrom']['generationRecord']}
 r['visualStatus']='static_sequence_reviewed' if accepted else 'rejected_insufficient_axis_correction'
 r['staticReview']={'reviewedAt':stamp,'accepted':accepted,'notes':note,'registeredCanvas':True,'clientDynamicAccepted':False}
 write(side,r)
 job=P/f'feet-NE-{n}-v{v}.job.json';j=read(job);j['references']=r['references'];j['editInput']=r['editInput'];write(job,j)
source='generation/limbs-20261004/feet-northeast/NE-13-v2.png'
write(P/'feet-selection.json',{'run/NE/13':{'source':source,'reason':reason,'staticReviewed':True}})
report={'reviewedAt':stamp,'scope':'旧槽run/NE/13；NE14转交axis_south，NE15首稿拒用后转交full_run_north','status':'candidate_ready_for_root_export','selectedReplacements':1,'selected':{'run/NE/13':source},'originalRuntimeUntouched':True,'sequenceOriginChanged':False,
 'actuallyViewed':['runtime/run/NE/05.png','runtime/run/NE/12.png','runtime/run/NE/13.png','runtime/run/NE/14.png','runtime/run/NE/15.png','runtime/run/NE/16.png','generation/limbs-20261004/feet-northeast/NE-13-v1.png','generation/limbs-20261004/feet-northeast/NE-13-v2.png','generation/limbs-20261004/feet-northeast/NE-15-v1.png','provenance/limbs-20261004/feet-NE13-comparison.jpg'],
 'selectedReview':{'slot':'run/NE/13','sha256':sha(ROOT/source),'nativeCanvas':[1254,1254],'mode':'RGBA','plannedRuntime':[1024,1024],'offset':[0,0],'cropFitOrWholeBodyShift':False,'reason':reason,'actualChange':'后蹬鞋白色鞋头向右的横向突出减小，变成接近后侧的窄边；棕色外底由明显L形收成较窄的连续脚掌。','registration':read(P/'feet-registration.json')['v2'],'supportDepth':'原靴最低点925，新928，差3原画像素；保留抬跟和前掌接触，没有把靴子整体平移贴线。','identityAndHands':'头冠/背包/卷轴、右炉左瓶位置保持，上身alpha IoU约0.989；没有新手、新瓶或道具交换。','limits':'少量手绘轮廓变化存在；是静态序列局部候选审阅，尚待根任务与另两张NE14/15新版共同连续预览。'},
 'rejections':[{'source':'generation/limbs-20261004/feet-northeast/NE-13-v1.png','reason':'侧向横钩仍明显，修正不足。'},{'source':'generation/limbs-20261004/feet-northeast/NE-15-v1.png','reason':'侧向横钩几乎不变；不纳入选表，另由north重试。'}],
 'unsubmittedDraftPrompts':['provenance/limbs-20261004/feet-NE-14-v1.prompt.txt','provenance/limbs-20261004/feet-NE-15-v2.prompt.txt'],
 'provenance':'三张实际输出均保存独立prompt/job/receipt及.png.generation.json。内置image_gen；配置目标由快照保存，工具未披露实际模型/质量，实际均null。未提交提示词没有输出/receipt，不冒充实际生成。',
 'clientValidated':False,'dynamicAccepted':False,'unresolvedMaterialItemsForSelectedNE13':[],
 'rootHandoff':'脚稿已落盘，只有NE13 v2可合并。合并后可依用户政策删除本子任务3张native PNG及1张比较JPG；保留全部文字记录。'}
write(P/'feet-review.json',report)
print(json.dumps({'selection':1,'slot':'run/NE/13','sha256':report['selectedReview']['sha256'],'images':3,'qaImages':1}))
