$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$buildPath = Join-Path $projectRoot 'dist'
$indexPath = Join-Path $buildPath 'index.html'
$demoSource = Join-Path $projectRoot 'public\data\demo.json'
$demoFolder = Join-Path $buildPath 'data'
$demoOutput = Join-Path $demoFolder 'demo.json'
$zipPath = Join-Path $projectRoot 'Proyecto-Final-itchio.zip'

if (-not (Test-Path -LiteralPath $indexPath -PathType Leaf)) {
    throw 'No se encontró dist/index.html. Ejecuta npm run build primero.'
}

if (-not (Test-Path -LiteralPath $demoSource -PathType Leaf)) {
    throw 'No se encontró public/data/demo.json.'
}

New-Item -ItemType Directory -Path $demoFolder -Force | Out-Null
Copy-Item -LiteralPath $demoSource -Destination $demoOutput -Force

Compress-Archive -Path (Join-Path $buildPath '*') -DestinationPath $zipPath -Force
Write-Host "Paquete para itch.io creado: $zipPath"
