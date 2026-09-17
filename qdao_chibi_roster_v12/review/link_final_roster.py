from pathlib import Path
p=Path(r'E:\work\image\qdao_chibi_roster_v12\review\site\index.html');t=p.read_text(encoding='utf-8');old='<a href="portrait-comparison.jpg" target="_blank" rel="noopener">查看八人肖像总览</a>';new='<a href="roster-final.jpg" target="_blank" rel="noopener">查看八人新版总览</a>\n<a href="portrait-comparison.jpg" target="_blank" rel="noopener">查看新旧肖像对照</a>';assert old in t;t=t.replace(old,new);p.write_text(t,encoding='utf-8')
print('Added final-roster overview link alongside comparison')
