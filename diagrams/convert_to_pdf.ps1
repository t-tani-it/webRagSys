# webRagSys diagrams -> PDF batch script (ASCII only for PS5.1)
# Usage: run this script in PowerShell
# Requires: Node.js (npx available)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $PSCommandPath

$diagrams = @(
    @{ Input = "01_flowchart.mmd";      Output = "01_flowchart.pdf";      Config = $null }
    @{ Input = "02_sequence.mmd";       Output = "02_sequence.pdf";       Config = $null }
    @{ Input = "03a_class_rag.mmd";     Output = "03a_class_rag.pdf";     Config = "puppeteer_landscape.json" }
    @{ Input = "03b_class_modules.mmd"; Output = "03b_class_modules.pdf"; Config = $null }
    @{ Input = "04_mindmap.mmd";        Output = "04_mindmap.pdf";        Config = $null }
    @{ Input = "05_state.mmd";          Output = "05_state.pdf";          Config = $null }
)

Write-Host "=== webRagSys diagrams -> PDF ===" -ForegroundColor Cyan
Write-Host ""

foreach ($d in $diagrams) {
    $inputFile = Join-Path $ScriptDir $d.Input
    $outputFile = Join-Path $ScriptDir $d.Output

    if (-not (Test-Path $inputFile)) {
        Write-Warning ("Missing: " + $inputFile)
        continue
    }

    Write-Host ("Converting: " + $d.Input + " -> " + $d.Output + " ... ") -NoNewline

    try {
        if ($d.Config) {
            $configFile = Join-Path $ScriptDir $d.Config
            npx.cmd -y @mermaid-js/mermaid-cli -i $inputFile -o $outputFile -p $configFile --pdfFit *>&1
        } else {
            npx.cmd -y @mermaid-js/mermaid-cli -i $inputFile -o $outputFile --pdfFit *>&1
        }
        Write-Host "done" -ForegroundColor Green
    } catch {
        Write-Host ("ERROR: " + $_) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== done ===" -ForegroundColor Cyan
Write-Host ("Out: " + $ScriptDir)
