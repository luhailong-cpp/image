from pathlib import Path
T=Path(__file__).resolve().parent;old=T.parent/'r11_c10'
for n in ['internal_qa.py','quilt_internal.py','repair_task.py','compose_patch.py']:
 s=(old/n).read_text(encoding='utf8').replace('r11_c10','r11_c11')
 if n=='quilt_internal.py':
  s=s.replace("records.append({'source'", "h.p.derived(mp,[src],{'method':'binary min-error native source ownership mask','originTileXY':[x-115,y-115],'fieldFile':str(fp),'fieldSha256':h.p.sha(fp)})\n  records.append({'source'")
  s+="\nh.p.derived(O/'preview.png',[out],{'method':'review-only downscale'})\n"
 (T/n).write_text(s,encoding='utf8')

