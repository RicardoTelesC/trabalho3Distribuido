# Executa a matriz minima do enunciado: 3 cenarios x 3 niveis de usuarios x 3 instancias WP.
# Aviso: 1000 usuarios exige maquina robusta; ajuste $UserLevels se necessario.

$UserLevels = @(10, 100, 1000)
$Instancias = @(1, 2, 3)
$Cenarios = @("cenario1", "cenario2", "cenario3")

foreach ($c in $Cenarios) {
    foreach ($i in $Instancias) {
        foreach ($u in $UserLevels) {
            Write-Host "`n=== $c | inst=$i | users=$u ===" -ForegroundColor Cyan
            & "$PSScriptRoot\run_locust_headless.ps1" `
                -Cenario $c `
                -Usuarios $u `
                -Instancias $i `
                -DuracaoSegundos 60
        }
    }
}

Write-Host "`nGerando graficos..."
python "$PSScriptRoot\gerar_graficos.py"
