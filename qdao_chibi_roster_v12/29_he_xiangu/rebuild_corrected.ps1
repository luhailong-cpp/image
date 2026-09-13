$ErrorActionPreference='Stop'
$characterRoot='E:\work\image\qdao_chibi_roster_v12\29_he_xiangu'
$toolRoot='E:\work\image\qdao_chibi_roster_v12'
python -X utf8 -B "$characterRoot\repair_phase_cells.py"
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
$phaseArgs=@()
foreach ($phase in 1..8) {$phaseArgs += @('--phase',("$characterRoot\source\phase-corrected\phase-{0:00}.png" -f $phase))}
python -X utf8 -B "$toolRoot\assemble_phases.py" @phaseArgs --output-dir "$characterRoot\source\corrected-transposed"
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
$pairs=@(@('s_e','S','E'),@('n_w','N','W'),@('ne_sw','NE','SW'),@('nw_se','NW','SE'))
foreach ($pair in $pairs) {
 python -X utf8 -B "$toolRoot\assemble_raw.py" --kind $pair[0] --first "$characterRoot\source\corrected-transposed\walk-$($pair[1]).png" --second "$characterRoot\source\corrected-transposed\walk-$($pair[2]).png" --first-rows 2 --first-cols 4 --second-rows 2 --second-cols 4 --output "$characterRoot\source\corrected-pair-$($pair[0]).png"
 if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
}
python -X utf8 -B "$toolRoot\process_roster.py" --character-dir $characterRoot --s-e "$characterRoot\source\corrected-pair-s_e.png" --n-w "$characterRoot\source\corrected-pair-n_w.png" --ne-sw "$characterRoot\source\corrected-pair-ne_sw.png" --nw-se "$characterRoot\source\corrected-pair-nw_se.png" --idle "$characterRoot\source\idle-v2.png"
exit $LASTEXITCODE
