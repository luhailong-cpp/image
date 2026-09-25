"""Bind a newly dispatched actual call to an unchanged prepared request."""
import argparse, json
from common import *

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    archive = archive_path(args.archive)
    require(not (archive / 'raw.png').exists() and not (archive / 'tool-result.json').exists(), 'An actual result already exists')
    request = request_data(archive)
    actual = request['actual_request']
    parameters = {'prompt': actual['prompt'], 'referenced_image_paths': actual['referenced_image_paths']}
    record = {'submitted_at': now(), 'prepared_request_sha256': sha(archive / 'request.json'),
              'actual_parameters': parameters, 'tool': 'image_gen.imagegen',
              'reference_bindings_at_submission': [{'path': p, 'sha256': sha(p)} for p in actual['referenced_image_paths']],
              'note': 'Fresh dispatch record; prepared request remains byte-exact. Successful result is recorded separately.'}
    save_new(archive / 'submission.json', record)
    print(json.dumps({'archive': str(archive), **parameters}, ensure_ascii=False))

if __name__ == '__main__':
    main()
