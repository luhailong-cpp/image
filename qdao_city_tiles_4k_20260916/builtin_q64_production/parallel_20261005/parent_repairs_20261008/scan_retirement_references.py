"""Read-only scan of all parallel sibling text references immediately before cleanup."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
PARALLEL = ROOT.parent
EXTENSIONS = {'.json', '.md', '.py', '.ps1', '.txt', '.js', '.ts', '.tsx', '.jsx', '.html', '.yml', '.yaml', '.toml', '.cs'}

def normalized(text):
    return text.lower().replace('\\\\', '/').replace('\\', '/')

def main():
    proposal = json.loads((ROOT/'cleanup-proposal.json').read_text(encoding='utf-8-sig'))
    patterns = []
    for item in proposal['conditionalRetirement']['items']:
        path = Path(item['file'])
        relative = path.relative_to(ROOT).as_posix().lower()
        patterns.append((item['file'], [normalized(str(path)), 'parent_repairs_20261008/'+relative, relative, item['sha256']]))
    result = subprocess.run(['rg', '--files', '--hidden', str(PARALLEL)], capture_output=True, text=True, encoding='utf-8', check=True)
    scanned = []
    matches = []
    non_runtime = []
    errors = []
    exceptions_path = ROOT/'historical-reference-exceptions.json'
    exceptions = json.loads(exceptions_path.read_text(encoding='utf-8-sig'))['items'] if exceptions_path.exists() else []
    for value in result.stdout.splitlines():
        path = Path(value)
        if ROOT in path.parents or path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            data = path.read_bytes()
            text = normalized(data.decode('utf-8-sig'))
        except Exception as error:
            errors.append({'file': value, 'error': str(error)})
            continue
        file_sha = hashlib.sha256(data).hexdigest()
        scanned.append({'file': value, 'sha256': file_sha, 'bytes': len(data)})
        for target, alternatives in patterns:
            found = [s for s in alternatives if s in text]
            if found:
                match = {'referenceFile': value, 'targetFile': target, 'matchedPatterns': found}
                exception = next((x for x in exceptions if Path(x['file']) == path and x['sha256'] == file_sha
                    and target in x['allowedTargets'] and (not x.get('hashOnly') or all(len(s) == 64 for s in found))), None)
                if exception:
                    non_runtime.append(dict(match, classification=exception['reason'], exceptionBoundToFileSha256=file_sha))
                else:
                    matches.append(match)
    output = {'at': datetime.now(timezone.utc).isoformat(), 'scope': str(PARALLEL), 'scannedFileCount': len(scanned),
        'scannedBytes': sum(x['bytes'] for x in scanned), 'matches': matches, 'nonRuntimeMatches': non_runtime, 'errors': errors,
        'method': 'rg enumerated all sibling text files; normalized absolute, parent-relative, branch-relative paths and target SHA256 matched. Parent-owned directory excluded.',
        'scannedFiles': scanned}
    (ROOT/'external-reference-scan.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'scanned': len(scanned), 'matches': len(matches), 'nonRuntimeMatches': len(non_runtime), 'errors': len(errors)}))
    if errors or matches:
        raise SystemExit(2)

if __name__ == '__main__':
    main()
