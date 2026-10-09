from pathlib import Path
T=Path(__file__).resolve().parent;B=T.parent
s=(B/'r11_c10/helper.py').read_text(encoding='utf8')
s=s.replace('r11_c10','r11_c11').replace('GX,GY=36864,40960','GX,GY=40960,40960')
s=s.replace("[('north',(115,0))]","[('north',(115,0)),('west',(0,115)),('northwest',(0,0))]")
s=s.replace("p.derived(dest,[src,state['north']['anchor']],","p.derived(dest,[src]+[state[k]['anchor'] for k in ['north','west','northwest']],")
s=s.replace("[('north',r==1)]","[('north',r==1),('west',c==1)]")
s=s.replace("(0,lo,1139,hi)","(2957,lo,4096,hi)")
s=s.replace("'left115px corresponds to target right115px'","'right115px corresponds to target left115px'")
(T/'helper.py').write_text(s,encoding='utf8')

