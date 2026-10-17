$ErrorActionPreference='Stop'
$sourceRoot=[IO.Path]::GetFullPath('E:/work/image/designs/class-skills-20260928/integration/server')
$targetRoot=[IO.Path]::GetFullPath('E:/work/xuanming-server-mmo')
$files=Get-ChildItem -LiteralPath $sourceRoot -Recurse -File | Where-Object { $_.FullName -notlike '*contract.txt' }
foreach($file in $files) {
    $relative=[IO.Path]::GetRelativePath($sourceRoot,$file.FullName)
    $target=[IO.Path]::GetFullPath((Join-Path $targetRoot $relative))
    if(-not $target.StartsWith($targetRoot+[IO.Path]::DirectorySeparatorChar)) { throw '目标越界' }
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target)) | Out-Null
    Copy-Item -LiteralPath $file.FullName -Destination $target -Force
}
Write-Output ('已应用服务端文件: '+$files.Count)
