from pathlib import Path
p=Path(r'E:\work\image\qdao_chibi_roster_v12\review\verify_review_pages.cjs');t=p.read_text(encoding='utf-8')
t=t.replace('let browser;','let browser,page;').replace('const page=await browser.newPage','page=await browser.newPage')
t=t.replace("  await page.locator('[data-direction=\"'+dr+'\"]').click();", "  report.progress={role:name,direction:dr};\n  await page.locator('[data-direction=\"'+dr+'\"]').click();")
t=t.replace("report.failure=String(e);throw e;", "report.failure=String(e);if(page)report.pageState=await page.evaluate(()=>({url:location.href,character:document.getElementById('character')?.value,ready:typeof ready==='undefined'?null:ready,playing:typeof playing==='undefined'?null:playing,direction:typeof direction==='undefined'?null:direction,requestVersion:typeof requestVersion==='undefined'?null:requestVersion,loading:document.getElementById('loading')?.textContent,loadError:document.getElementById('load-error')?.textContent,imageSources:typeof imageCache==='undefined'?[]:[...imageCache.keys()].slice(-16)})).catch(()=>null);throw e;")
p.write_text(t,encoding='utf-8')
print('Added precise failing-role and browser-state diagnostics to QA')
