"""Render selected native S frames with the shared read-only QA script."""
from pathlib import Path
source = (Path(__file__).parent / 'inspect_direction.py').read_text(encoding='utf-8')
source = source.replace("work = DELIVERY / 'work' / args.direction", "work = DELIVERY / 'work' / args.direction / 'variants' / 'native'")
exec(compile(source, str(Path(__file__)), 'exec'))
