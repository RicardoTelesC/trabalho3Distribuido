param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("cenario1", "cenario2", "cenario3")]
    [string]$Cenario,

    [Parameter(Mandatory = $true)]
    [int]$Usuarios,

    [int]$SpawnRate = 0,
    [int]$DuracaoSegundos = 60,
    [int]$Instancias = 3,
    [string]$PostPath = ""
)

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if ($SpawnRate -le 0) {
    $SpawnRate = [Math]::Min($Usuarios, 50)
}

$locustFile = switch ($Cenario) {
    "cenario1" { "locustfile_cenario1_imagem_1mb.py" }
    "cenario2" { "locustfile_cenario2_texto_400kb.py" }
    "cenario3" { "locustfile_cenario3_imagem_300kb.py" }
}

& "$PSScriptRoot\set_instancias.ps1" -Instancias $Instancias
Start-Sleep -Seconds 60

$outDir = Join-Path $Root "resultados\$Cenario\inst_$Instancias"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$csvPrefix = "/mnt/locust/resultados/$Cenario/inst_$Instancias/users_$Usuarios/run"

$dockerArgs = @("compose", "run", "--rm")
if ($PostPath) {
    $dockerArgs += @("-e", "POST_PATH=$PostPath")
}
$dockerArgs += @(
    "locust",
    "-f", "/mnt/locust/$locustFile",
    "--host=http://nginx",
    "--headless",
    "-u", "$Usuarios",
    "-r", "$SpawnRate",
    "-t", "${DuracaoSegundos}s",
    "--csv", $csvPrefix
)

Write-Host "Executando Locust: $Cenario | $Usuarios usuarios | $Instancias WP | ${DuracaoSegundos}s"
& docker @dockerArgs

$statsLocal = Join-Path $outDir "users_$Usuarios/run_stats.csv"
$manifestPath = Join-Path $Root "resultados/manifest.json"
$manifest = @()
if (Test-Path $manifestPath) {
    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
}
$manifest += [ordered]@{
    cenario      = $Cenario
    instancias   = $Instancias
    usuarios     = $Usuarios
    stats_csv    = $statsLocal
    locust_file  = $locustFile
    duracao_s    = $DuracaoSegundos
}
($manifest | ConvertTo-Json -Depth 4) | Set-Content -Encoding UTF8 $manifestPath
Write-Host "Stats: $statsLocal"
