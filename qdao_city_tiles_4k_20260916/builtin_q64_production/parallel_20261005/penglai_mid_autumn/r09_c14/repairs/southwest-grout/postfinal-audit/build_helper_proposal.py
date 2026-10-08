"""Write a review-only full source and unified diff; never modify tools helper."""
from pathlib import Path
import difflib,hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
helper=ROOT/'tools/finalize_scoped.py'
original=helper.read_text(encoding='utf-8');addition=(OUT/'source_metadata_proposal.py').read_text(encoding='utf-8')
addition=addition[addition.index('def source_metadata'):]
anchor='def approve(ctx,required,covered,reports):'
assert original.count(anchor)==1
proposed=original.replace(anchor,addition+'\n\n'+anchor)
anchor="    frozen(ctx);frozen_reviews(covered,reports);snapshots=[record for record in [pending_snapshot(mp),pending_snapshot(review_path),pending_snapshot(progress_path)] if record]"
assert proposed.count(anchor)==1
proposed=proposed.replace(anchor,"    source_overrides=source_metadata(ctx,read(mp) if mp.exists() else {})\n"+anchor)
anchor='    write(mp,manifest)\n'
assert proposed.count(anchor)==1
proposed=proposed.replace(anchor,'    manifest.update(source_overrides)\n'+anchor)
compile(proposed,str(helper),'exec')
(OUT/'finalize_scoped.proposed.py').write_text(proposed,encoding='utf-8')
(OUT/'finalize_scoped.proposal.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),proposed.splitlines(True),fromfile='a/tools/finalize_scoped.py',tofile='b/tools/finalize_scoped.py')),encoding='utf-8')
print(json.dumps(dict(proposalPrepared=True,productionHelperModified=False,baseHelperSha256=hashlib.sha256(helper.read_bytes()).hexdigest())))
