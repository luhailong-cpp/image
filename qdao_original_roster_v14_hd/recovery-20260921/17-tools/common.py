"""Character 17 local evidence helpers. No image generation or shared mutations."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, re, sys
sys.dont_write_bytecode = True
from PIL import Image

HERE = Path(__file__).resolve().parent
RECOVERY = HERE.parent
PACKAGE = RECOVERY.parent
IMAGE_ROOT = PACKAGE.parent
GEN = RECOVERY / '17-generation'
CHAR = '17_ghost_script_calligrapher_boy'
DIRS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
CONFIG = IMAGE_ROOT / 'config/image-generation.json'
UNVERIFIED = '宿主管理；实际工具返回未披露可核实的型号或质量，配置目标不作为实际结果。'

def require(value, message):
    if not value:
        raise ValueError(message)

def now():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def archive_path(path):
    path = Path(path).resolve()
    require(path.is_relative_to(GEN.resolve()) and path != GEN.resolve(), 'Archive must stay below recovery/17-generation')
    require(re.fullmatch(r'[A-Za-z0-9_-]+', path.name), 'Use a simple unique attempt directory name')
    return path

def slot(kind, direction, frame=None):
    require(kind in ('walk', 'idle') and direction in DIRS, 'Invalid action/direction')
    if kind == 'walk':
        require(isinstance(frame, int) and 1 <= frame <= 16, 'Walk frame must be 1 through 16')
        return f'walk/{direction}/{frame:02d}.png'
    require(frame is None or frame == 0, 'Idle must not reuse a walk frame number')
    return f'idle/{direction}.png'

def image_identity(path):
    with Image.open(path) as image:
        image.load()
        return {'file': str(Path(path).resolve()), 'sha256': sha(path), 'width': image.width,
                'height': image.height, 'format': image.format, 'mode': image.mode}

def request_data(archive):
    request = read(archive / 'request.json')
    if 'actual_request' not in request:
        require(request.get('tool') in ('image_gen.imagegen', 'built-in image_gen'), 'Unrecognized actual request tool')
        require(request.get('prompt') == 'prompt.txt', 'Unsupported original prompt-file mapping')
        references = request.get('referenced_image_paths', [])
        require(references, 'Original request must name actual references')
        before = all(isinstance(r, dict) and r.get('path') and r.get('sha256') for r in references)
        if not before:
            require(all(isinstance(r, str) for r in references), 'Unsupported mixed reference schema')
            binding_file = archive / 'reference-bindings.json'
            require(binding_file.is_file(), 'String references need an explicit after-generation reference-bindings.json')
            binding = read(binding_file)
            require(binding['request_sha256'] == sha(archive / 'request.json') and binding['timing'] == 'after_generation', 'Invalid later reference binding')
            references = binding['references']
        request = {**request, 'original_request_schema': 'prompt_file_and_reference_objects',
            'actual_request': {'prompt': (archive / 'prompt.txt').read_text(encoding='utf-8'),
                               'referenced_image_paths': [r['path'] for r in references],
                               'started_at': request.get('startedAt')},
            'reference_bindings_at_start': references if before else [],
            'reference_bindings_after_generation': [] if before else references}
    if (archive / 'slot.json').is_file():
        binding = read(archive / 'slot.json')
        require(binding.get('request_sha256') == sha(archive / 'request.json'), 'Slot binding belongs to another request')
        for key in ('kind', 'direction', 'frame', 'slot'):
            require(key not in request or request[key] == binding[key], 'Slot binding disagrees with actual request')
            request[key] = binding[key]
    actual = request['actual_request']
    require((archive / 'prompt.txt').read_bytes() == actual['prompt'].encode('utf-8'), 'Prompt bytes differ from prepared actual request')
    require(actual.get('started_at'), 'Missing actual request start timestamp')
    require(request.get('character_id', CHAR) == CHAR, 'Wrong character')
    slot(request['kind'], request['direction'], request.get('frame'))
    for item in request.get('reference_bindings_at_start', []) + request.get('reference_bindings_after_generation', []):
        path = Path(item['path'])
        require(path.is_file() and sha(path) == item['sha256'], 'Reference changed since request preparation: ' + str(path))
    return request
