from pathlib import Path
root=Path(r'E:\work\image\qdao_chibi_roster_v12\review')
p=root/'site/index.html';t=p.read_text(encoding='utf-8')
old="im.onerror=()=>reject(new Error('无法读取：'+url));im.src=url;"
new="im.onerror=()=>{imageCache.delete(url);reject(new Error('无法读取：'+url));};im.src=url;"
assert old in t;t=t.replace(old,new);p.write_text(t,encoding='utf-8')
p=root/'verify_review_pages.cjs';t=p.read_text(encoding='utf-8');old="page.on('pageerror',e=>report.errors.push(e.message));";new=old+"\npage.on('requestfailed',r=>report.errors.push('REQUEST FAILED '+r.url()+' '+JSON.stringify(r.failure())));";assert old in t;t=t.replace(old,new);p.write_text(t,encoding='utf-8')
print('Failed images can be retried by reselecting a direction; QA records network failures')
