from pathlib import Path
p=Path(r'E:\work\image\qdao_chibi_roster_v12\review\sync_final_preview.py');t=p.read_text(encoding='utf-8').replace("im.thumbnail((330,290)","im.thumbnail((330,250)").replace("top+19),im)","top+12),im)");p.write_text(t,encoding='utf-8')
print('Portrait overview places names below intact source canvases')
