# Screening arithmetic, not an electrochemical simulation or selected pack design.
# Run range-weight-model.ps1 first if its inputs change.
$ErrorActionPreference = 'Stop'
$culture = [System.Globalization.CultureInfo]::InvariantCulture
$rangeRows = Import-Csv -LiteralPath (Join-Path $PSScriptRoot 'range-weight-scenarios.csv')
$bikeLimitKg = 400 * 0.45359237
$nonPackKg = 90
$packBudgetKg = $bikeLimitKg - $nonPackKg
$availableFraction = 0.90
$densities = @(265, 284, (23.4 / 0.0745), 322, 340, 375, 390, 450)
$results = @(
    foreach ($row in $rangeRows) {
        if ([double]::Parse($row.speed_mph, $culture) -ne 70) { continue }
        $cda = [double]::Parse($row.drag_area_m2, $culture)
        $whMi = [double]::Parse($row.wh_per_mile, $culture)
        $energy = [double]::Parse($row.nominal_kwh_for_200_miles, $culture)
        foreach ($fraction in @(0.75, 0.80, 0.85)) {
            foreach ($cellDensity in $densities) {
                $packDensity = $cellDensity * $fraction
                $packKg = $energy * 1000 / $packDensity
                [pscustomobject]@{
                    range_baseline_mph = 70
                    drag_area_m2 = $cda
                    cell_wh_kg = $cellDensity
                    cells_fraction_of_pack_mass = $fraction
                    nominal_pack_wh_kg = $packDensity
                    nominal_kwh_for_200_miles = $energy
                    pack_mass_kg_for_200_miles = $packKg
                    total_bike_lb_for_200_miles = ($packKg + $nonPackKg) / 0.45359237
                    range_miles_at_400_lb_ceiling = $packBudgetKg * $packDensity * $availableFraction / $whMi
                    cell_wh_kg_required_at_400_lb_ceiling = $energy * 1000 / $packBudgetKg / $fraction
                }
            }
        }
    }
)
$results | Export-Csv -LiteralPath (Join-Path $PSScriptRoot 'battery-screening-results.csv') -NoTypeInformation
$results | Where-Object { $_.cells_fraction_of_pack_mass -eq 0.80 -and $_.drag_area_m2 -eq 0.30 } |
    Select-Object @{n='Cell Wh/kg';e={[math]::Round($_.cell_wh_kg,1)}},
    @{n='Pack Wh/kg';e={[math]::Round($_.nominal_pack_wh_kg,1)}},
    @{n='Bike lb for 200 mi';e={[math]::Round($_.total_bike_lb_for_200_miles,1)}},
    @{n='Range at 400 lb';e={[math]::Round($_.range_miles_at_400_lb_ceiling,1)}} |
    Format-Table -AutoSize

'Illustrative 10-80% charging: ideal average power required, without losses/taper:'
foreach ($minutes in @(10,20,30)) {
    $energy = [double]::Parse(($rangeRows | Where-Object { $_.speed_mph -eq '70' -and $_.drag_area_m2 -eq '0.3' }).nominal_kwh_for_200_miles, $culture)
    '{0} minutes: {1:N1} kW average / {2:N1} energy-equivalent C' -f $minutes, ($energy * 0.70 * 60 / $minutes), (0.70 * 60 / $minutes)
}
if ($results.Count -ne 72) { throw 'Unexpected scenario count.' }
$sanity = $results | Where-Object { $_.cell_wh_kg -eq 340 -and $_.cells_fraction_of_pack_mass -eq 0.85 -and $_.drag_area_m2 -eq 0.30 }
if ([math]::Abs($sanity.total_bike_lb_for_200_miles - 390.8118) -gt 0.1) { throw 'Screening arithmetic check failed.' }
'72 screening scenarios generated; arithmetic check passed.'
