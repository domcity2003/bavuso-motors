# Candidate-specific mass and range calculations. No physical performance validation.
$ErrorActionPreference = 'Stop'
$lbKg = 0.45359237
$nonPackKg = 90
$riderKg = 90
$availableFraction = 0.90
$candidates = @(
    @{ Name = 'Preferred high-energy pouch'; Kwh = 30; PackWhKg = 390 * 0.80 },
    @{ Name = 'Lighter high-energy pouch'; Kwh = 28; PackWhKg = 390 * 0.80 },
    @{ Name = 'Balanced pouch comparison'; Kwh = 30; PackWhKg = 340 * 0.80 },
    @{ Name = 'Cylindrical comparison'; Kwh = 30; PackWhKg = (23.4 / 0.0745) * 0.80 }
)
function Get-Consumption {
    param([double]$Mph, [double]$CdA, [double]$BikeKg)
    $v = $Mph * 0.44704
    $dragN = 0.5 * 1.225 * $CdA * $v * $v
    $rollingN = 0.015 * ($BikeKg + $riderKg) * 9.80665
    (($dragN + $rollingN) * $v / 0.90 + 300) / $Mph
}
$rows = @(
    foreach ($candidate in $candidates) {
        $packKg = $candidate.Kwh * 1000 / $candidate.PackWhKg
        $bikeKg = $packKg + $nonPackKg
        foreach ($cda in @(0.30, 0.33, 0.35, 0.40)) {
            $wh70 = Get-Consumption -Mph 70 -CdA $cda -BikeKg $bikeKg
            $wh77 = Get-Consumption -Mph 77 -CdA $cda -BikeKg $bikeKg
            $wh125 = Get-Consumption -Mph 125 -CdA $cda -BikeKg $bikeKg
            [pscustomobject]@{
                candidate = $candidate.Name
                nominal_kwh = $candidate.Kwh
                pack_wh_kg = $candidate.PackWhKg
                pack_mass_kg = $packKg
                total_bike_lb = $bikeKg / $lbKg
                drag_area_m2 = $cda
                range_miles_at_70_mph = $candidate.Kwh * 1000 * $availableFraction / $wh70
                range_miles_at_77_mph = $candidate.Kwh * 1000 * $availableFraction / $wh77
                battery_kw_to_hold_125_mph = $wh125 * 125 / 1000
            }
        }
    }
)
$rows | Export-Csv -LiteralPath (Join-Path $PSScriptRoot 'design-variant-results.csv') -NoTypeInformation
$rows | Where-Object { $_.drag_area_m2 -eq 0.35 } |
    Select-Object candidate, nominal_kwh,
    @{n='Bike lb';e={[math]::Round($_.total_bike_lb,1)}},
    @{n='Range at 70 mph';e={[math]::Round($_.range_miles_at_70_mph,1)}},
    @{n='Range at 77 mph';e={[math]::Round($_.range_miles_at_77_mph,1)}} | Format-Table -AutoSize
if ($rows.Count -ne 16) { throw 'Unexpected scenario count.' }
$preferred = $rows | Where-Object { $_.candidate -eq 'Preferred high-energy pouch' -and $_.drag_area_m2 -eq 0.35 }
if ([math]::Abs($preferred.total_bike_lb - 410.39898) -gt 0.01 -or [math]::Abs($preferred.range_miles_at_70_mph - 209.73319) -gt 0.01) {
    throw 'Candidate calculation consistency check failed.'
}
'16 scenarios generated; candidate mass and range checks passed.'
