from pathlib import Path
import shutil

ROOT = Path('C:/Users/luyua/.codex/skills/.system/imagegen')
BACKUP = Path('E:/work/image/.work/image25-migration/system-imagegen')
MODEL = 'gpt-image-2.5-sunburst'
changed = []

def update(rel, transform):
    path = ROOT / rel
    raw = path.read_bytes()
    old = raw.decode('utf-8')
    newline = '\r\n' if '\r\n' in old else '\n'
    new = transform(old.replace('\r\n', '\n')).replace('\n', newline)
    if new == old:
        return
    dest = BACKUP / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(path, dest)
    path.write_bytes(new.encode('utf-8'))
    changed.append(rel)

def swap(s, old, new):
    if old not in s:
        raise ValueError(f'Missing expected text: {old[:100]}')
    return s.replace(old, new)

def common(s):
    return s.replace('gpt-image-2', MODEL).replace(
        ', or after the user explicitly confirms that a transparent-output request should use the `gpt-image-1.5` true-transparency fallback path',
        ', or explicitly confirms the API fallback')

def skill(s):
    s = common(s)
    s = swap(s, '- Use the built-in `image_gen` tool by default for normal image generation and editing requests.', '- Use the built-in `image_gen` tool by default for normal image generation and editing requests. Target GPT Image 2.5 Sunburst (`gpt-image-2.5-sunburst`) at the highest available quality. If the tool exposes model and quality parameters, set `model=gpt-image-2.5-sunburst` and `quality=max`; otherwise use the actual tool schema and do not claim either parameter was forced.')
    s = swap(s, '- CLI `'+MODEL+'` does not support `background=transparent`; ask before using `gpt-image-1.5` unless the user explicitly requested that model.', '- CLI `'+MODEL+'` supports `background=transparent` with PNG or WebP output.')
    s = swap(s, '- `'+MODEL+'` always uses high fidelity for image inputs; do not set `input_fidelity` with this model.', '- CLI edits may set `input_fidelity=high` or `low` when input preservation control is needed; omit it by default. Do not inherit older-model restrictions for this parameter.')
    s = swap(s, '- `'+MODEL+'` supports `quality` values `low`, `medium`, `high`, and `auto`.', '- `'+MODEL+'` supports `quality` values `low`, `medium`, `high`, `xhigh`, `max`, and `auto`. The CLI default is `max` to honor the highest-quality preference.')
    s = swap(s, '- Use `quality low` for fast drafts, thumbnails, and quick iterations. Use `medium`, `high`, or `auto` for final assets, dense text, diagrams, identity-sensitive edits, or high-resolution outputs.', '- Use `quality=max` for final assets. Use `quality=low` when the user requests fast drafts, thumbnails, or quick iterations; honor another explicit quality choice.')
    return s

def cli(s):
    s = common(s).replace('- Quality: `medium`', '- Quality: `max`')
    s = swap(s, '- Use `--quality low` for fast drafts, thumbnails, and quick iterations.', '- Use `--quality low` when fast drafts, thumbnails, or quick iterations are requested.')
    s = swap(s, '- Use `--quality medium`, `--quality high`, or `--quality auto` for final assets, dense text, diagrams, identity-sensitive edits, and high-resolution outputs.', '- Use `--quality max` for final assets and highest-quality requests; honor a different explicit quality choice.')
    s = swap(s, '- Do not pass `--input-fidelity` with `'+MODEL+'`; this model always uses high fidelity for image inputs.', '- For edits, `--input-fidelity high|low` is optional and omitted by default; use `high` when explicitly controlling input preservation.')
    s = swap(s, '- Do not use `--background transparent` with CLI `'+MODEL+'`; ask before using `gpt-image-1.5` unless the user explicitly requested that model.', '- Use `--background transparent --output-format png` (or `webp`) for native transparent output with `'+MODEL+'`.')
    s = s.replace('--quality high', '--quality max')
    s = swap(s, 'True transparent fallback request:\n\nAsk for confirmation before using this command unless the user explicitly requested `gpt-image-1.5`.', 'Native transparent output after CLI/API mode is authorized:')
    s = s.replace('--model gpt-image-1.5', '--model '+MODEL)
    s = swap(s, 'Explain that CLI `'+MODEL+'` does not support `background=transparent`, so transparent CLI output requires the confirmed `gpt-image-1.5` fallback.', 'Native transparency is supported by the default model; preserve the output alpha channel.')
    s = swap(s, '`low|medium|high|auto`', '`low|medium|high|xhigh|max|auto` for GPT Image 2.5')
    s = swap(s, '- `--input-fidelity` is **edit-only** and validated as `low|high`; it is not supported for `'+MODEL+'`', '- `--input-fidelity` is **edit-only** and validated as `low|high`; omit it by default. The explicit legacy models `gpt-image-2` and `gpt-image-1-mini` do not accept it.')
    s = swap(s, '- True transparent CLI outputs require `output_format` to be `png` or `webp` and are not supported by `'+MODEL+'`.', '- True transparent CLI outputs are supported by `'+MODEL+'` and require `output_format` to be `png` or `webp`.')
    s = swap(s, 'older GPT Image models support `1024x1024`, `1536x1024`, `1024x1536`, or `auto`.', 'the legacy `gpt-image-2` compatibility branch also supports flexible sizes, while GPT Image 1-family models support `1024x1024`, `1536x1024`, `1024x1536`, or `auto`.')
    return s

def api(s):
    return '''# Image API quick reference

Read this file only for explicitly authorized CLI/API fallback work. The built-in `image_gen` tool remains the default and does not require `OPENAI_API_KEY`. API parameters below are not automatically available on the built-in tool.

## Defaults and supported controls

- Model: GPT Image 2.5 Sunburst (`gpt-image-2.5-sunburst`).
- Quality: `max` for the user's highest-quality preference. Supported values are `low`, `medium`, `high`, `xhigh`, `max`, and `auto`. Use `low` for explicitly requested fast drafts; honor other explicit choices.
- Size: `auto`, or `WIDTHxHEIGHT` with both dimensions divisible by 16, neither edge above 3840 pixels, an aspect ratio between 1:3 and 3:1, and 655,360–8,294,400 total pixels. Output above 2560×1440 pixels is experimental.
- Common sizes: `1024x1024`, `1536x1024`, `1024x1536`, `2048x2048`, `2048x1152`, `3840x2160`, `2160x3840`.
- Background: `transparent`, `opaque`, or `auto`. Native transparency requires PNG or WebP; preserve its alpha channel.
- Output: `png` (default), `jpeg`, or `webp`; `output_compression` is 0–100 for JPEG/WebP.
- `n`: 1–10 images; `moderation`: `auto` or `low`.

## Endpoints and editing

Use `POST /v1/images/generations` (`client.images.generate`) for generation and `POST /v1/images/edits` (`client.images.edit`) for changes to existing images. Results contain `data[].b64_json`; the bundled CLI writes decoded files.

Edits accept up to 16 PNG, WebP, or JPEG inputs, each under 50 MB. An optional PNG mask must have the same dimensions as the first input and be under 4 MB. Transparent mask areas identify the edit region; boundaries remain prompt-guided.

`input_fidelity` accepts `high` or `low` on supported edit models, including the default GPT Image 2.5 model. The CLI omits it unless requested. Use `high` when explicitly controlling preservation of reference details. Do not copy the old GPT Image 2 always-high restriction onto GPT Image 2.5.

## Explicit legacy compatibility

Older models are available only when explicitly chosen; they are never automatic fallbacks. Their supported quality settings stop at `high` (plus `auto`), so callers must select a compatible quality instead of inheriting the `max` default.

- `gpt-image-2` and its `2026-04-21` snapshot support the same flexible size bounds. Omit `input_fidelity`; these models always use high input fidelity. This CLI retains its previous rejection of transparent output for that legacy branch.
- `gpt-image-1`, `gpt-image-1.5`, and `gpt-image-1-mini` use `1024x1024`, `1536x1024`, `1024x1536`, or `auto`. The first two accept `input_fidelity=low|high`; `gpt-image-1-mini` does not.

If a requested option fails, report the error. Do not silently lower model or quality, remove required transparency, or change the authorized execution path.

## Sources

Verified 2026-09-16: [GPT Image 2.5 Sunburst](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst), [image generation guide](https://developers.openai.com/api/docs/guides/image-generation), and [image edit API reference](https://developers.openai.com/api/reference/python/resources/images/methods/edit).
'''

def prompts(s):
    s = common(s)
    s = s.replace('use `medium` or `high` quality for small text', 'use `max` quality for small text')
    s = s.replace('It supports `quality=low|medium|high|auto`; use `low` for fast drafts and thumbnails, and move to `medium`, `high`, or `auto` for final assets.', 'It supports `quality=low|medium|high|xhigh|max|auto`; default to `max` for final assets, and use `low` for explicitly requested fast drafts and thumbnails.')
    s = s.replace('`'+MODEL+'` supports `quality` values `low`, `medium`, `high`, and `auto`.', '`'+MODEL+'` supports `quality` values `low`, `medium`, `high`, `xhigh`, `max`, and `auto`; default to `max` for highest-quality output.')
    s = s.replace('`'+MODEL+'` always uses high fidelity for image inputs, so do not set `input_fidelity` with that model.', 'CLI edits can set `input_fidelity=high|low`; omit it by default and use `high` when explicitly controlling reference preservation.')
    s = s.replace('Do not set `input_fidelity` with `'+MODEL+'`; image inputs already use high fidelity.', 'For CLI edits, omit `input_fidelity` by default or set `high|low` when input preservation control is needed.')
    s = s.replace('CLI `'+MODEL+'` does not support `background=transparent`; ask before using `gpt-image-1.5` unless the user explicitly requested that model.', 'CLI `'+MODEL+'` supports `background=transparent` with PNG or WebP output; preserve native alpha.')
    return s

def script(s):
    s = swap(s, 'Used only when the user explicitly opts into CLI fallback mode, or when explicit\ntransparent output requires the `gpt-image-1.5` fallback path.', 'Used only when the user explicitly opts into CLI/API fallback mode.')
    s = swap(s, 'Defaults to gpt-image-2 and a structured prompt augmentation workflow.', 'Defaults to GPT Image 2.5 Sunburst at max quality and structured prompt augmentation.')
    s = swap(s, 'DEFAULT_MODEL = "gpt-image-2"', 'DEFAULT_MODEL = "gpt-image-2.5-sunburst"')
    s = swap(s, 'DEFAULT_QUALITY = "medium"', 'DEFAULT_QUALITY = "max"')
    s = swap(s, 'ALLOWED_QUALITIES = {"low", "medium", "high", "auto"}', 'ALLOWED_LEGACY_QUALITIES = {"low", "medium", "high", "auto"}\nALLOWED_QUALITIES = ALLOWED_LEGACY_QUALITIES | {"xhigh", "max"}')
    s = swap(s, 'GPT_IMAGE_2_MODEL = "gpt-image-2"', '# Legacy IDs are retained only for explicit compatibility.\nGPT_IMAGE_2_MODELS = {"gpt-image-2", "gpt-image-2-2026-04-21"}\nGPT_IMAGE_25_MODELS = {\n    "gpt-image-2.5-sunburst", "gpt-image-2.5-sunburst-2026-09-08",\n    "gpt-image-2.5-flare", "gpt-image-2.5-flare-2026-09-08",\n}\nFLEXIBLE_SIZE_MODELS = GPT_IMAGE_2_MODELS | GPT_IMAGE_25_MODELS')
    s = s.replace('GPT_IMAGE_2_MIN_PIXELS', 'FLEXIBLE_MIN_PIXELS').replace('GPT_IMAGE_2_MAX_PIXELS', 'FLEXIBLE_MAX_PIXELS').replace('GPT_IMAGE_2_MAX_EDGE', 'FLEXIBLE_MAX_EDGE').replace('GPT_IMAGE_2_MAX_RATIO', 'FLEXIBLE_MAX_RATIO').replace('_validate_gpt_image_2_size', '_validate_flexible_size')
    s = s.replace('"gpt-image-2 size', '"GPT Image flexible size')
    s = swap(s, 'if model == GPT_IMAGE_2_MODEL:', 'if model in FLEXIBLE_SIZE_MODELS:')
    s = swap(s, 'def _validate_quality(quality: str) -> None:\n    if quality not in ALLOWED_QUALITIES:\n        _die("quality must be one of low, medium, high, or auto.")', 'def _validate_quality(quality: str, model: str) -> None:\n    allowed = ALLOWED_QUALITIES if model in GPT_IMAGE_25_MODELS else ALLOWED_LEGACY_QUALITIES\n    if quality not in allowed:\n        _die(f"quality for {model} must be one of {\', \'.join(sorted(allowed))}.")')
    s = swap(s, '"model must be a GPT Image model (for example gpt-image-1.5, gpt-image-1, or gpt-image-1-mini)."', '"model must be a GPT Image model (for example gpt-image-2.5-sunburst)."')
    start = s.index('    if model != GPT_IMAGE_2_MODEL:', s.index('def _validate_model_specific_options'))
    end = s.index('\n\ndef _validate_generate_payload', start)
    s = s[:start] + '''    # Keep legacy compatibility constraints separate from GPT Image 2.5.
    if model in GPT_IMAGE_2_MODELS and background == "transparent":
        _die(f"This CLI does not enable transparent output for legacy {model}. Use the default GPT Image 2.5 model.")
    if input_fidelity is not None and model in GPT_IMAGE_2_MODELS:
        _die(f"input_fidelity is not supported in legacy {model}; image inputs use high fidelity.")
    if input_fidelity is not None and model == "gpt-image-1-mini":
        _die("input_fidelity is not supported in legacy gpt-image-1-mini.")
''' + s[end:]
    s = s.replace('_validate_quality(quality)', '_validate_quality(quality, model)').replace('_validate_quality(args.quality)', '_validate_quality(args.quality, args.model)')
    return s

update('SKILL.md', skill)
update('references/cli.md', cli)
update('references/image-api.md', api)
update('references/codex-network.md', common)
update('references/prompting.md', prompts)
update('references/sample-prompts.md', prompts)
update('scripts/image_gen.py', script)
update('scripts/remove_chroma_key.py', lambda s: swap(s, "This helper supports the imagegen skill's built-in-first transparent workflow:\ngenerate an image on a flat key color, then convert that key color to alpha.", 'Optional postprocessing for assets deliberately generated on a flat key color.\nPrefer native transparency for ordinary transparent-output requests.'))
print('\n'.join(changed))
