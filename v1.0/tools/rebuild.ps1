$ErrorActionPreference = 'Stop'
$v1Root = Split-Path $PSScriptRoot -Parent
$bikeRoot = Split-Path $v1Root -Parent
& (Join-Path $bikeRoot '.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe') (Join-Path $PSScriptRoot 'build-v1.py')
if ($LASTEXITCODE -ne 0) { throw 'V1 CAD generation failed' }
