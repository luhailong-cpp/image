$ErrorActionPreference = 'Stop'
$source = Get-Content -LiteralPath 'E:\work\mmorpg-client\.codex\unity-mcp-client.ps1' -Raw
$definitionStart = $source.IndexOf("`$ErrorActionPreference = 'Stop'")
$definitionEnd = $source.LastIndexOf("`$session = Start-UnityMcp")
Invoke-Expression $source.Substring($definitionStart, $definitionEnd - $definitionStart)
$session = Start-UnityMcp
try {
    Send-McpJson $session @{ jsonrpc = '2.0'; id = 21; method = 'tools/list'; params = @{} }
    $rpc = Receive-McpResponse $session 21 30
    $rpc | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath 'E:\work\image\client_ui_refresh_20260908\qa\official-mcp-tools.json' -Encoding utf8
    $rpc.result.tools | Select-Object name,description | ConvertTo-Json -Depth 10
}
finally { Stop-UnityMcp $session }
