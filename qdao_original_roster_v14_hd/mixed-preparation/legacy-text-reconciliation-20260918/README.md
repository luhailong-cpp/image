# Historical text reconciliation

This supplement preserves the earlier inventory audit and every original file.
The eleven exact path/current-SHA/original-SHA/frame-sources-SHA bindings are
hardcoded in `legacy_text_reconciliation.py`. Four files recover their recorded
SHA using CRLF to LF; seven need internal LF with one terminal CRLF. No prompt,
receipt, model field, image, source record, or prior audit is rewritten.

For original files, import the module and call:

```python
evidence = reconcile_text(path, expected_sha256, frame_sources_path, frame_sources_sha256)
```

For a self-contained assembly, preserve the actual current text and the complete
bound frame-sources JSON as ordinary evidence bytes. Copy this tool unchanged and
bind its SHA. During checking, pass the original path identities plus those copied
bytes:

```python
evidence = reconcile_bytes(original_path, expected_sha256, frame_sources_path,
                           frame_sources_sha256, current_text_bytes, frame_sources_bytes)
```

Both interfaces return JSON-compatible evidence only. They never return or write
the reconstructed historical text. Unknown paths, other current bytes, other
expected hashes, modified source records, and unbound source paths fail closed.
Do not accept a saved `status` value alone: run the interface against the actual
preserved evidence. Each returned row binds all four hashes, the exact conversion
rule, matching frame-source record keys, and this tool's hash.

CLI without `--report` only prints a fresh result. `--report` can create a new JSON
beside the tool and refuses an existing file. The negative unit tests mutate only
in-memory copies. Reconciliation establishes exact historical text hashes; it is
not visual approval, model confirmation, or permission to change any old artwork.
