# Bavuso Motors: steady-speed energy model. All inputs below are study assumptions.
# Run from any directory. No network access or external dependencies.
$ErrorActionPreference = 'Stop'
$lbPerKg = 1 / 0.45359237
$bikeKg = 400 / $lbPerKg # Ceiling calculation; a finished bike must be lighter.
$riderGearKg = 90
$rho = 1.225
$gravity = 9.80665
$crr = 0.015
$efficiency = 0.90
$auxWatts = 300
$usableFraction = 0.90 # Combined unavailable capacity/reserve allowance, not aging.
$nonPackKg = 90
$packWhKg = 220
$rangeBaselineMph = 70
$comfortDesignMph = 77

function Get-Scenario {
    param([double]$Mph, [double]$CdA, [double]$HeadwindMph = 0)
    $groundSpeed = $Mph * 0.44704
    $airSpeed = ($Mph + $HeadwindMph) * 0.44704
    $dragN = 0.5 * $rho * $CdA * $airSpeed * $airSpeed
    $rollingN = $crr * ($bikeKg + $riderGearKg) * $gravity
    $batteryW = ($dragN + $rollingN) * $groundSpeed / $efficiency + $auxWatts
    $whMi = $batteryW / $Mph
    $nominalKwh = $whMi * 200 / 1000 / $usableFraction
    [pscustomobject]@{
        speed_mph = $Mph
        drag_area_m2 = $CdA
        headwind_mph = $HeadwindMph
        battery_kw = $batteryW / 1000
        wh_per_mile = $whMi
        nominal_kwh_for_200_miles = $nominalKwh
        pack_lb_at_220_wh_kg = $nominalKwh * 1000 / $packWhKg * $lbPerKg
        range_miles_at_400_lb_budget = ($bikeKg - $nonPackKg) * $packWhKg * $usableFraction / $whMi
        required_pack_wh_kg_at_400_lb_budget = $nominalKwh * 1000 / ($bikeKg - $nonPackKg)
    }
}

$rows = @(
    foreach ($cda in @(0.30, 0.40, 0.50)) {
        foreach ($mph in @(55, 65, $rangeBaselineMph, 75, $comfortDesignMph)) { Get-Scenario -Mph $mph -CdA $cda }
    }
)
$rows | Export-Csv -LiteralPath (Join-Path $PSScriptRoot 'range-weight-scenarios.csv') -NoTypeInformation
$rows | Select-Object speed_mph, drag_area_m2,
    @{n='Wh/mile';e={[math]::Round($_.wh_per_mile,1)}},
    @{n='Nominal kWh / 200 mi';e={[math]::Round($_.nominal_kwh_for_200_miles,1)}},
    @{n='Pack lb / 220 Wh/kg';e={[math]::Round($_.pack_lb_at_220_wh_kg)}} | Format-Table -AutoSize

'125 mph battery power, kW (separate top-speed check):'
foreach ($cda in @(0.30, 0.40, 0.50)) {
    $s = Get-Scenario -Mph 125 -CdA $cda
    'CdA {0}: {1:N1} kW' -f $cda, $s.battery_kw
}
'70 mph range baseline, CdA 0.40, 10 mph headwind:'
Get-Scenario -Mph $rangeBaselineMph -CdA 0.40 -HeadwindMph 10 | Format-List
'Allowed pack at 400 lb ceiling: {0:N1} kg / {1:N1} kWh nominal' -f ($bikeKg - $nonPackKg), (($bikeKg - $nonPackKg) * $packWhKg / 1000)

# Dimensional/consistency checks on the central scenario.
$central = Get-Scenario -Mph $rangeBaselineMph -CdA 0.40
if ([math]::Abs($central.nominal_kwh_for_200_miles * 1000 * $usableFraction / $central.wh_per_mile - 200) -gt 0.000001) {
    throw 'Energy-to-range consistency check failed.'
}
if ($central.wh_per_mile -le (Get-Scenario -Mph 55 -CdA 0.40).wh_per_mile) {
    throw 'Speed sensitivity check failed.'
}
'Model consistency checks passed.'
