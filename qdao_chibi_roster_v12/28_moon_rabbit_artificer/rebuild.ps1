$ErrorActionPreference='Stop'
$characterRoot='E:\work\image\qdao_chibi_roster_v12\28_moon_rabbit_artificer'
$toolRoot='E:\work\image\qdao_chibi_roster_v12'
python -X utf8 -B "$characterRoot\atomic_runner.py" "$characterRoot\assemble_directions.py"
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
$pairs=@(@('s_e','S','E'),@('n_w','N','W'),@('ne_sw','NE','SW'),@('nw_se','NW','SE'))
foreach ($pair in $pairs) {
 python -X utf8 -B "$characterRoot\atomic_runner.py" "$toolRoot\assemble_raw.py" --kind $pair[0] --first "$characterRoot\source\walk-$($pair[1])-final.png" --second "$characterRoot\source\walk-$($pair[2])-final.png" --first-rows 2 --first-cols 4 --second-rows 2 --second-cols 4 --output "$characterRoot\source\pair-$($pair[0]).png"
 if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
}
python -X utf8 -B "$characterRoot\atomic_runner.py" "$toolRoot\process_roster.py" --character-dir $characterRoot --s-e "$characterRoot\source\pair-s_e.png" --n-w "$characterRoot\source\pair-n_w.png" --ne-sw "$characterRoot\source\pair-ne_sw.png" --nw-se "$characterRoot\source\pair-nw_se.png" --idle "$characterRoot\source\idle.png" --portrait-raw "$characterRoot\source\portrait-daoist.png"
exit $LASTEXITCODE
