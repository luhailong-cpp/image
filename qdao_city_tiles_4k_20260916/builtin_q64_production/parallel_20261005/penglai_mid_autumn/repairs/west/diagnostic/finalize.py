exec((__import__('pathlib').Path(__file__).parent/'measure.py').read_text(encoding='utf-8').split('rows={}')[0])
trial=arr(OUT/'recommended-trial.png')[:,115:]
def peak(a,x,lo,hi):
    g=grey(a);v=g[:,max(0,x-1):min(g.shape[1],x+2)].mean(axis=1).astype(np.float32)
    gy=np.gradient(cv2.GaussianBlur(v,(1,5),0).ravel());return lo+int(np.argmax(gy[lo:hi]))
r=json.loads((OUT/'recommended-record.json').read_text(encoding='utf-8'))
r['metrics']['roofFaceHighlightRisingEdgeLocalY']=dict(old=peak(left,626,1100,1145),raw=peak(raw,627,1100,1145),current=peak(current[2842:4096,:627],0,1100,1145),trial=peak(trial,0,1100,1145))
r['resampling']='bicubic of existing native source pixels, native dimensions retained; no enlargement and no generative drawing'
r['visualReviewPending']=False
r['visualReview']=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),actuallyViewedFiles=['recommended-native-comparison.png','recommended-trial.png'],scale='1:1',scope='new tile x0..100, y3692..4096; entire404px transition and100px return included in comparison',finding='Major endpoint dark joint stair-step removed; roof face highlight joins with a small change in painted highlight curvature. No missing roof component in this scope. Entire merged city seam and other y positions are not accepted by this trial.',canRecommendAlgorithm=True,productionAccepted=False)
r['integration']='Use recommended-trial pixel region x115..215,y850..1254 to replace current new tile x0..100,y3692..4096 only after verifying inputCurrentSha256. Do not copy trial left115px or any other region. Alternatively reproduce recommended_trial.py formula within merge_west; calculate its support flow on actual old c12 only.'
(OUT/'recommended-record.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(metrics=r['metrics'],visualReview=r['visualReview'],integration=r['integration']),indent=2))
