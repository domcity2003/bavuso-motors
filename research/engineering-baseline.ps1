# Screening calculations, not a vehicle simulation or qualified parts list.
# October 25, 2026. Codex (GPT-6 family).
$ErrorActionPreference = 'Stop'
$lbKg = 0.45359237
$cellWh = 37.57
$cellKg = 0.0973
$count = 800
$cellMass = $count * $cellKg
$energy = $count * $cellWh / 1000
$budget = @(
    [pscustomobject]@{ Item='Complete pack'; Kg=$cellMass/0.8; Basis='800 typical cells; assumed 80% cell mass fraction' },
    [pscustomobject]@{ Item='Motor'; Kg=10.3; Basis='EMRAX 208 liquid-cooled reference, v1.5' },
    [pscustomobject]@{ Item='Inverter'; Kg=6.75; Basis='Cascadia CM200DX reference' },
    [pscustomobject]@{ Item='Reduction and final drive'; Kg=5; Basis='Engineering allowance, including shaft support and guards' },
    [pscustomobject]@{ Item='Frame, subframe and swingarm'; Kg=16; Basis='Engineering allowance, excludes pack case' },
    [pscustomobject]@{ Item='Suspension and steering'; Kg=10; Basis='Engineering allowance, including yokes and damper' },
    [pscustomobject]@{ Item='Wheels, tires and bearings'; Kg=17; Basis='Engineering allowance, excludes brake rotors' },
    [pscustomobject]@{ Item='Friction brakes and ABS'; Kg=7; Basis='Engineering allowance, includes rotors and fluid' },
    [pscustomobject]@{ Item='Onboard AC charger'; Kg=3; Basis='BROGEN compact 6.6 kW catalog ceiling; unqualified' },
    [pscustomobject]@{ Item='EVCC, inlet and charge routing'; Kg=2; Basis='Engineering allowance; charge-specific switching' },
    [pscustomobject]@{ Item='DC/DC and low voltage battery'; Kg=2; Basis='Engineering allowance' },
    [pscustomobject]@{ Item='External thermal system'; Kg=5; Basis='Engineering allowance, pumps/radiators/fans/hoses/all coolant; no refrigerant chiller' },
    [pscustomobject]@{ Item='Body, seat, controls, lighting and vehicle wiring'; Kg=11; Basis='Engineering allowance; HV vehicle cables included' },
    [pscustomobject]@{ Item='Other mounts, fasteners and stand'; Kg=4; Basis='Engineering allowance; no double count of component internal hardware' }
)
$budget | Export-Csv -LiteralPath (Join-Path $PSScriptRoot 'engineering-mass-budget.csv') -NoTypeInformation
$bikeKg = ($budget | Measure-Object -Property Kg -Sum).Sum
$contingency = 0.05 * ($bikeKg - $cellMass)
$riderKg = 90
$rho = 1.225
$crr = 0.015
$g = 9.80665
$eta = 0.90
$aux = 300
function Get-RoadLoad {
    param([double]$Mph, [double]$CdA, [double]$MassKg, [double]$HeadwindMph=0, [double]$Grade=0)
    $v = $Mph * 0.44704
    $air = ($Mph + $HeadwindMph) * 0.44704
    $rolling = $crr * ($MassKg + $riderKg) * $g
    $drag = 0.5 * $rho * $CdA * $air * $air
    $gradeForce = ($MassKg + $riderKg) * $g * $Grade
    $wheelW = ($rolling + $drag + $gradeForce) * $v
    [pscustomobject]@{ BatteryW=$wheelW/$eta+$aux; WheelW=$wheelW; WhMile=($wheelW/$eta+$aux)/$Mph }
}
function Get-CdALimit {
    param([double]$Kwh, [double]$MassKg, [double]$Available=0.90, [double]$Health=1)
    $v = 70 * 0.44704
    $allowedW = $Kwh*1000*$Available*$Health/200*70
    (($allowedW-$aux)*$eta/$v-$crr*($MassKg+$riderKg)*$g)/(0.5*$rho*$v*$v)
}
$scenarios = @(
    foreach ($case in @(
        @{Name='Reference';Mass=$bikeKg;Health=1;Energy=$energy},
        @{Name='Reference plus contingency';Mass=$bikeKg+$contingency;Health=1;Energy=$energy},
        @{Name='Reference at 90% battery health';Mass=$bikeKg;Health=0.9;Energy=$energy},
        @{Name='Minimum published cell energy';Mass=$bikeKg;Health=1;Energy=800*36.72/1000},
        @{Name='Lightweight target, unproven';Mass=$cellMass/0.85+88;Health=1;Energy=$energy}
    )) {
        foreach ($cda in @(0.30,0.33,0.35,0.37,0.40)) {
            $p70 = Get-RoadLoad 70 $cda $case.Mass
            $p77 = Get-RoadLoad 77 $cda $case.Mass
            $p125 = Get-RoadLoad 125 $cda $case.Mass
            $p130 = Get-RoadLoad 130 $cda $case.Mass
            $wind = Get-RoadLoad 70 $cda $case.Mass 10
            [pscustomobject]@{
                scenario=$case.Name; bike_kg=$case.Mass; bike_lb=$case.Mass/$lbKg
                nominal_kwh=$case.Energy; battery_health=$case.Health; cda_m2=$cda
                wh_mile_70=$p70.WhMile
                range_70=$case.Energy*1000*0.9*$case.Health/$p70.WhMile
                range_77=$case.Energy*1000*0.9*$case.Health/$p77.WhMile
                range_70_headwind_10=$case.Energy*1000*0.9*$case.Health/$wind.WhMile
                battery_kw_125=$p125.BatteryW/1000; wheel_kw_125=$p125.WheelW/1000
                battery_kw_130=$p130.BatteryW/1000
                cda_limit_for_200=Get-CdALimit $case.Energy $case.Mass 0.9 $case.Health
            }
        }
    }
)
$scenarios | Export-Csv -LiteralPath (Join-Path $PSScriptRoot 'engineering-performance.csv') -NoTypeInformation
$reference = $scenarios | Where-Object { $_.scenario -eq 'Reference' -and $_.cda_m2 -eq 0.35 }
$v70 = 70*0.44704
$deltaDragW = 0.5*$rho*0.01*$v70*$v70*$v70/$eta
$deltaKwh = $deltaDragW/70*200/1000/0.9
$deltaMassKwh = $crr*10*$g*$v70/$eta/70*200/1000/0.9
$tireDiameter = 17*0.0254+2*0.160*0.60
$tireRadius = $tireDiameter/2
$wheelRpm125 = 125*0.44704/([math]::PI*$tireDiameter)*60
$shaftKw125 = $reference.wheel_kw_125/0.97
$shaftRpm125 = $wheelRpm125*3.1
$shaftTorque125 = $shaftKw125*1000/($shaftRpm125*2*[math]::PI/60)
$rawCellLiters = 800*125.4*42.2*8.25/1e6
$summary = [ordered]@{
    date='2026-10-25'; model='Codex GPT-6 family'; nominal_kwh=$energy
    cells_kg=$cellMass; pack_kg=$cellMass/0.8; outside_pack_kg=$bikeKg-$cellMass/0.8
    reference_bike_kg=$bikeKg; reference_bike_lb=$bikeKg/$lbKg
    contingency_kg=$contingency; bike_with_contingency_lb=($bikeKg+$contingency)/$lbKg
    lightweight_target_lb=($cellMass/0.85+88)/$lbKg
    lightweight_with_contingency_lb=(($cellMass/0.85+88)+0.05*($cellMass/0.85+88-$cellMass))/$lbKg
    nonpack_limit_for_400_at_80pct=400*$lbKg-$cellMass/0.8
    nonpack_limit_for_400_at_85pct=400*$lbKg-$cellMass/0.85
    cda_limit_new=Get-CdALimit $energy $bikeKg
    cda_limit_90pct_health=Get-CdALimit $energy $bikeKg 0.9 0.9
    cda_limit_80pct_health=Get-CdALimit $energy $bikeKg 0.9 0.8
    nominal_kwh_saved_per_0_01_cda_at_70=$deltaKwh
    nominal_kwh_saved_per_10kg_at_70=$deltaMassKwh
    raw_cell_liters=$rawCellLiters
    conceptual_module_liters=275*185*105/1e6
    conceptual_pack_envelope_liters=600*260*560/1e6
    tire_geometric_diameter_m=$tireDiameter; wheel_rpm_125=$wheelRpm125
    motor_rpm_125_at_3_1=$shaftRpm125; shaft_kw_125=$shaftKw125; shaft_nm_125=$shaftTorque125
    peak_wheel_nm_at_150_motor_nm=150*3.1*0.97
    kinetic_energy_kj_125=0.5*($bikeKg+90)*[math]::Pow(125*0.44704,2)/1000
    grade5pct_extra_battery_kw_77=($bikeKg+90)*$g*0.05*(77*0.44704)/$eta/1000
    charging_10_80_kwh=$energy*0.7
    charging_10_80_minutes_net30=$energy*0.7/30*60
    charging_10_80_minutes_net40=$energy*0.7/40*60
    charging_10_80_minutes_net50=$energy*0.7/50*60
}
$summary | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'engineering-summary.json') -Encoding utf8
# Independent dimensional and limiting-case checks, not physical validation.
if ([math]::Abs($energy-30.056) -gt 1e-8) { throw 'Cell energy arithmetic failed' }
$zeroDrag = Get-RoadLoad 70 0 $bikeKg
$closedForm = (($crr*($bikeKg+$riderKg)*$g*$v70/$eta)+$aux)/70
if ([math]::Abs($zeroDrag.WhMile-$closedForm) -gt 1e-8) { throw 'Rolling/auxiliary limit failed' }
$inverse = Get-RoadLoad 70 (Get-CdALimit $energy $bikeKg) $bikeKg
if ([math]::Abs($energy*1000*0.9/$inverse.WhMile-200) -gt 1e-8) { throw 'Inverse drag budget failed' }
if ($scenarios.Count -ne 25) { throw 'Scenario count failed' }
foreach ($row in $scenarios) {
    if ($row.range_77 -ge $row.range_70 -or $row.range_70_headwind_10 -ge $row.range_70 -or $row.battery_kw_130 -le $row.battery_kw_125) { throw 'Speed/wind monotonicity failed' }
}
$summary | ConvertTo-Json
$reference | Format-List
'25 scenarios exported; energy, limiting-case, inverse-budget and speed/wind checks passed.'
