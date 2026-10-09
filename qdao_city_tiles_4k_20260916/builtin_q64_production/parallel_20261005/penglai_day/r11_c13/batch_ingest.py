import helper as h
import sys
for x in h.p.read(h.ROOT/'evidence'/sys.argv[1]):
    existing=h.ROOT/'native'/f"{x['name']}.png"
    if existing.exists():
        assert h.p.sha(existing)==h.p.sha(x['source'])
        assert h.p.read(str(existing)+'.generation.json')['sha256']==h.p.sha(existing)
    else:
        h.ingest(x['source'],x['name'],x.get('role','native_detail'))
    h.p.write(h.ROOT/'evidence'/f"{x['name']}.actual-tool-result.json",x)

