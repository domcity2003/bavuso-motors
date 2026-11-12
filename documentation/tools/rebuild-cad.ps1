$ErrorActionPreference = 'Stop'
$cadProjectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$cadPython = Join-Path $cadProjectRoot '.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe'
if (-not (Test-Path -LiteralPath $cadPython)) { throw 'Official portable FreeCAD runtime missing; see documentation/cad-studio.md' }
& $cadPython (Join-Path $PSScriptRoot 'build-freecad-package.py')
if ($LASTEXITCODE -ne 0) { throw 'FreeCAD model build failed' }
