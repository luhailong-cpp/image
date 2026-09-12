$ErrorActionPreference = 'Stop'
$charRoot = $PSScriptRoot
$rosterRoot = Split-Path -Parent $charRoot
python -X utf8 (Join-Path $charRoot 'assemble_directions.py')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -X utf8 (Join-Path $rosterRoot 'process_roster.py') --character-dir $charRoot --portrait (Join-Path $charRoot 'sources/portrait.png') --portrait-prompt (Join-Path $charRoot 'prompts/portrait.txt') --cardinal (Join-Path $charRoot 'sources/cardinal_assembled.png') --cardinal-prompt (Join-Path $charRoot 'prompts/cardinal_assembled.txt') --diagonal (Join-Path $charRoot 'sources/diagonal_assembled.png') --diagonal-prompt (Join-Path $charRoot 'prompts/diagonal_assembled.txt') --duration 120
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -X utf8 (Join-Path $charRoot 'supplement_manifest.py') $charRoot
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -X utf8 (Join-Path $charRoot 'clean_export_edges.py') --narrow
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -X utf8 (Join-Path $charRoot 'clean_export_edges.py')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -X utf8 (Join-Path $charRoot 'verify_artifacts.py')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'Artifact export passed. Recheck the portrait, PNG contacts and decoded GIF contact before updating visual QC.'
