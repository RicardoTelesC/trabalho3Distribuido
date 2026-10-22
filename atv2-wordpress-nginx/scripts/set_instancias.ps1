param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(1, 2, 3)]
    [int]$Instancias
)

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$nginxFile = switch ($Instancias) {
    1 { "nginx.1wp.conf" }
    2 { "nginx.2wp.conf" }
    3 { "nginx.conf" }
}

$env:NGINX_CONFIG = "./$nginxFile"

Write-Host "Parando servicos..."
docker compose down

$upArgs = @("compose", "up", "-d", "mysql", "wordpress1", "nginx")
if ($Instancias -ge 2) {
    $upArgs += @("--profile", "wp2", "wordpress2")
}
if ($Instancias -ge 3) {
    $upArgs += @("--profile", "wp3", "wordpress3")
}

Write-Host "Subindo stack ($Instancias instancia(s), nginx=$nginxFile)..."
& docker @upArgs

Write-Host "Aguarde cerca de 60 segundos antes de rodar o Locust."
