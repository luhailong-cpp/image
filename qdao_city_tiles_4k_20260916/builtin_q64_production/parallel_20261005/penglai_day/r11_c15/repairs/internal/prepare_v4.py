from pathlib import Path
import sys,json
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O));import ai_helper as h
G=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
h.ingest('hull-mid-keep-joint',G/'exec-8a6beadf-86af-4cd4-b7eb-ea74e4783aea.png')
h.ingest('hull-low',G/'exec-0bc91e0b-1054-4ac7-8fcc-93f9d6d25656.png')
s=(O/'integrate_v3.py').read_text(encoding='utf8').replace('v3','v4')
s=s.replace("'hull-mid':{'v':[[440,510],[770,850]],'h':[[690,780],[1000,1090]]}","'hull-mid':{'v':[[440,510],[770,850]]}")
s=s.replace("'boom-left':{'v':[[530,640],[870,980]]}","'boom-left':{'v':[[530,640],[870,980]]},'hull-low':{'h':[[450,530],[720,800]]}")
s=s.replace("for s in spec:","spec=[z for z in spec if z['name']!='sail-midright']+[z for z in spec if z['name']=='sail-midright']+[{'name':'hull-low','origin':[750,2445]}]\nfor s in spec:")
s=s.replace("gen=O/(n+'-generated.png')","gen=O/(('hull-mid-keep-joint' if n=='hull-mid' else n)+'-generated.png')")
s=s.replace(" if n=='hull-mid':m[(X>516)&(X<593)&(Y>253)&(Y<468)]=False","")
s=s.replace(" if n=='sail-upper-right':m &= (X>220)&(X<985)"," if n=='sail-upper-right':\n  m &= (X>220)&(X<985)\n  m |= (X>280)&(X<470) # whole mast segment, continued by next generated segment")
s=s.replace(" if n=='sail-midright':m &= (X>470)&(X<930)"," if n=='sail-midright':\n  m &= (X>470)&(X<930)\n  mast=(X>280)&(X<480)&(Y<1085)&(Y>=cut(cost.T,60,150)[None,:])\n  boom=(X<910)&(Y>940+.075*X)&(Y<1095+.05*X)&(X>=cut(cost,20,80)[:,None])\n  m |= mast|boom")
s=s.replace(" if n=='boom-left':m &= Y<720", " if n=='boom-left':\n  m &= Y<720\n  boom=(X>180)&(Y>435+.108*(X-200))&(Y<580+.108*(X-200))\n  m |= boom")
s=s.replace("'9 native local AI seam repairs", "'10 native local AI seam repairs")
(O/'integrate_v4.py').write_text(s,encoding='utf8')
