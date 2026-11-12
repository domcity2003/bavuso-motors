"""Recalculate Bavuso cost assumptions and audit functional budget coverage.

Run from any directory, Python standard library. Component bundle and fixed
prelaunch estimate inputs live in the two CSVs. This is a planning calculator,
not supplier quotation, manufacturing verification or investment validation.
"""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
VOLUMES = (100, 1000, 10000)
SCENARIOS = ('low', 'base', 'high')


def read(name):
    with (ROOT / name).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def write(name, rows):
    with (ROOT / name).open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


rows = read('cost-model.csv')
index_path = ROOT.parent / 'documentation/registers/component-index.csv'
with index_path.open(encoding='utf-8-sig', newline='') as handle:
    index = list(csv.DictReader(handle))
coverage = [row for row in rows if row['record_type'] == 'Component/function coverage']
assert len(coverage) == len(index) == 158
assert {row['record_id'] for row in coverage} == {row['record_id'] for row in index}
assert len({row['record_id'] for row in rows}) == len(rows)
owners = [row for row in coverage if row['allocation'] == 'Budget owner for entire bundle']
assert len(owners) == len({row['cost_group'] for row in coverage}) == 42
for row in coverage:
    if row not in owners:
        assert all(float(row[f'usd_{v}_{s}']) == 0 for v in VOLUMES for s in SCENARIOS)
for row in owners:
    for volume in VOLUMES:
        values = [float(row[f'usd_{volume}_{scenario}']) for scenario in SCENARIOS]
        assert 0 <= values[0] <= values[1] <= values[2], (row['record_id'], values)

processes = {row['cost_group']: row for row in rows if row['record_type'] == 'Recurring production process'}
assert set(processes) == {'INBOUND', 'IMPORT', 'SCRAP', 'ASSEMBLY', 'EOL', 'FACTORY', 'DELIVERY', 'WARRANTY'}
# The arrays refer to annual capacities 100, 1000, 10000, not actual orders.
rates = {
    'INBOUND': {'low': (.02, .015, .012), 'base': (.04, .03, .025), 'high': (.08, .06, .05)},
    'IMPORT': {'low': (0, 0, 0), 'base': (.025, .025, .025), 'high': (.10, .10, .10)},
    'SCRAP': {'low': (.02, .015, .01), 'base': (.04, .03, .02), 'high': (.08, .06, .04)},
    'ASSEMBLY': {'low': (25*50, 16*45, 8*40), 'base': (40*65, 24*60, 12*55), 'high': (65*85, 40*80, 22*75)},
    'EOL': {'low': (150, 100, 70), 'base': (250, 160, 110), 'high': (450, 300, 220)},
    'FACTORY': {'low': (600, 400, 250), 'base': (1000, 650, 450), 'high': (1700, 1100, 800)},
    'DELIVERY': {'low': (250, 200, 180), 'base': (500, 400, 350), 'high': (900, 750, 650)},
    'WARRANTY': {'low': (.02, .02, .015), 'base': (.04, .035, .03), 'high': (.08, .07, .06)},
}
material = {v: {s: 0 for s in SCENARIOS} for v in VOLUMES}
total = {v: {s: 0 for s in SCENARIOS} for v in VOLUMES}
for j, volume in enumerate(VOLUMES):
    for scenario in SCENARIOS:
        field = f'usd_{volume}_{scenario}'
        material[volume][scenario] = sum(float(row[field]) for row in owners if row['base_included'] == 'True')
        factory_total = material[volume][scenario]
        for key in ('INBOUND', 'IMPORT', 'SCRAP', 'ASSEMBLY', 'EOL', 'FACTORY'):
            charge = rates[key][scenario][j]
            if key in ('INBOUND', 'IMPORT', 'SCRAP'):
                charge *= material[volume][scenario]
            processes[key][field] = round(charge, 2)
            factory_total += round(charge, 2)
        processes['DELIVERY'][field] = rates['DELIVERY'][scenario][j]
        processes['WARRANTY'][field] = round(factory_total * rates['WARRANTY'][scenario][j], 2)
        total[volume][scenario] = round(factory_total + float(processes['DELIVERY'][field]) + float(processes['WARRANTY'][field]), 2)
        assert abs(total[volume][scenario] - sum(float(row[field]) for row in rows if row['base_included'] == 'True')) < .02
write('cost-model.csv', rows)

startup = [row for row in read('startup-costs.csv') if row['annual_volume_scenario'] in tuple(str(v) for v in VOLUMES)]
assert len(startup) == 54
launch_totals = {}
for j, volume in enumerate(VOLUMES):
    selected = [row for row in startup if row['annual_volume_scenario'] == str(volume)]
    specific = {row['cost_id']: row for row in selected}
    for scenario in SCENARIOS:
        field = 'usd_' + scenario
        landed_material = material[volume][scenario] * (1 + rates['INBOUND'][scenario][j] + rates['IMPORT'][scenario][j])
        specific['PRODUCTION_INVENTORY'][field] = round(volume * (8, 10, 12)[j] / 52 * landed_material)
        specific['COLLECTION_GAP'][field] = round(volume * (2, 3, 4)[j] / 52 * total[volume][scenario])
        prelaunch = sum(float(row[field]) for row in selected if row['cost_id'] not in ('PRODUCTION_INVENTORY', 'COLLECTION_GAP', 'RESERVE'))
        specific['RESERVE'][field] = round(prelaunch * {'low': .15, 'base': .25, 'high': .4}[scenario])
    launch_totals[volume] = {s: round(sum(float(row['usd_' + s]) for row in selected)) for s in SCENARIOS}

# Stage0 is early work nested within a future full program, not added to it.
# Stage0B is additional to Stage0A. Items have distinct work scopes.
stage_specs = [
    ('Stage0A', 'A_DESIGN', 'Architecture and package design; no fabrication release', (35000, 75000, 150000), 'Base600engineeringhours x125USD/h; low350hours x100; high1000hours x150. Paid equivalent; owner work may defer cash but not work.'),
    ('Stage0A', 'A_BUCK', 'Non-ridden rider/package buck and dimensional mockups', (2500, 6000, 14000), 'Materials and paid shop fabrication only; no battery or roadworthy chassis.'),
    ('Stage0A', 'A_MODULE', 'Limited-energy cell/module thermal and mechanical coupons', (5000, 12000, 30000), 'Small sample batch and containment/instrumentation consumables; not700celltractionpack; supply may be refused.'),
    ('Stage0A', 'A_BENCH', 'Qualified limited-energy bench setup and execution labor', (6000, 15000, 35000), 'Base120engineeringhours x125USD/h, plus equipment rental in A_INSTRUMENTS; no motorcycle riding.'),
    ('Stage0A', 'A_INSTRUMENTS', 'Measurement rentals fixtures and safe limited-energy supply', (4000, 10000, 25000), 'Temporary instrumentation and bench fixtures; no full HV motor dynamometer purchase.'),
    ('Stage0A', 'A_REVIEW', 'Independent cell/pack/chassis concept review', (5000, 12500, 30000), 'Base100specialisthours x125USD/h; scope excludes completed vehicle certification.'),
    ('Stage0B', 'B_PARTS', 'One custom engineering prototype hardware envelope', (0, 0, 0), 'Recomputed1.2/1.5/2.0 x100volumecomponentlow/base/high subtotal. Includes700cells and one motor/inverter; no assumed stock or exact released BOM.'),
    ('Stage0B', 'B_ENGINEERING', 'Detailed prototype integration and build engineering labor', (70000, 150000, 300000), 'Base1200hours x125USD/h, additional to A_DESIGN. Excludes production engineering and completed durability certification.'),
    ('Stage0B', 'B_TEST', 'Outsourced motor/charge/structural subassembly bench campaign', (15000, 35000, 90000), 'Limited contracted rig time and setup; not a guarantee alltests pass or entire brake/range/compliance campaign completed.'),
    ('Stage0B', 'B_SPACE', 'Short-term workshop lifting equipment and insurance allocation', (8000, 20000, 50000), 'Project-specific workshop/handling arrangements; no factory lease or staff runway.'),
]
for stage, key, title, amounts, basis in stage_specs:
    row = dict(cost_id=key, annual_volume_scenario=stage, description=title, cash_category='Early feasibility stage - nested in full program', basis=basis,
               usd_low=amounts[0], usd_base=amounts[1], usd_high=amounts[2], confidence='Unquoted scoped allowance; not a guaranteed completed build price',
               timing='Stage0A before major hardware; Stage0B only after feasibility/design readiness',
               double_count_control='Stage0B incremental afterStage0A. Both replace corresponding early work inside24monthlaunchprogram; never add to fullprogram again.')
    if key == 'B_PARTS':
        for scenario, factor in (('low', 1.2), ('base', 1.5), ('high', 2)):
            row['usd_' + scenario] = round(material[100][scenario] * factor)
    startup.append(row)
stage_totals = {}
for stage in ('Stage0A', 'Stage0B'):
    selected = [row for row in startup if row['annual_volume_scenario'] == stage]
    reserve = dict(selected[0])
    reserve.update(cost_id=stage+'_RESERVE', description='Early-stage uncertainty reserve', basis='25percent ofstagebudget; no guaranteed adequacy or physical success', cash_category='Early-stage contingency')
    for scenario in SCENARIOS:
        reserve['usd_' + scenario] = round(sum(float(row['usd_' + scenario]) for row in selected) * .25)
    startup.append(reserve)
    stage_totals[stage] = {s: round(sum(float(row['usd_'+s]) for row in selected) + float(reserve['usd_'+s])) for s in SCENARIOS}
write('startup-costs.csv', startup)

summary = dict(
    date='2026-10-25', currency='USD', status='Unquoted planning scenarios; not supplier commitments or build release',
    coverage=dict(component_index_records=len(index), mapped_records=len(coverage), bundles=len(owners), recurring_processes=len(processes),
                  meaning='Functional budget coverage only; exact installed leafparts remain unselected'),
    material_per_bike=material, recurring_delivered_per_bike=total, launch_cash_24month=launch_totals,
    early_stage_cash=stage_totals,
    early_stage_combined={s: stage_totals['Stage0A'][s]+stage_totals['Stage0B'][s] for s in SCENARIOS},
    early_stage_scope='A:nonriddenbuckandlimitedenergybenches; B:onecustomengineeringprototypeenvelopeandbenchwork. Not guaranteed toproduce rideablebikeorcloseallgoals.',
    cell_price_assumption_usd_each={100:[20,40,80],1000:[15,30,70],10000:[10,20,60]},
    exchange_rate_assumption_usd_per_eur=1.10,
    audits=['158recordIDs match source index','42singlebudgetowners; allincludedchildrowszero','low<=base<=high componentinputs',
            '8recurringprocessformulasreconciled','inventoryandcashgaprecalculated','prelaunchreserveexcludesworkingcapital',
            'Stage0nestednotaddedtolaunchcash'],
    exclusions='No purchasedrealestate,cellfactory,financinginterest,worldwidehomologationorretailpriceforecast; see narrative.'
)
(ROOT/'cost-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
