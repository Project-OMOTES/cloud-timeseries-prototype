import datetime
import random
import uuid

import pandas

NUM_OF_ASSETS = 250
KPIs = ["HeatIn_Q1", "Heat_flow1", "PostProc_Velocity1", "HeatIn_Q2", "Heat_flow2", "PostProc_Velocity2", "HeatIn_Q3", "Heat_flow3", "PostProc_Velocity3", "HeatIn_Q4"]
START_DATETIME = datetime.datetime.fromisoformat('2020-01-01T00:00:00+00:00')
END_DATETIME = datetime.datetime.fromisoformat('2021-01-01T00:00:00+00:00')
RESOLUTION = datetime.timedelta(minutes=15)

CARRIER_ID = str(uuid.uuid4())
SIMULATION_RUN_ID = str(uuid.uuid4())

esdl_id = str(uuid.uuid4())
asset_ids = [str(uuid.uuid4()) for _ in range(0, NUM_OF_ASSETS)]


times = []
carrier_ids = []
asset_ids_ = []
asset_classes = []
asset_names = []
capabilities = []
simulation_runs = []
simulation_types = []
kpis = {}

current_time = START_DATETIME
while current_time < END_DATETIME:
    for asset_i, asset_id in enumerate(asset_ids):
        times.append(current_time)
        carrier_ids.append(CARRIER_ID)
        asset_ids_.append(asset_id)
        asset_names.append(asset_id)
        asset_classes.append(random.choice(['HeatingDemand', 'Pipe', 'ResidualHeatSource']))
        capabilities.append(random.choice(['Consumer', 'Transport', 'Producer']))
        simulation_runs.append(SIMULATION_RUN_ID)
        simulation_types.append("EndScenarioSizingDiscountedStagedHIGHS")

        for kpi in KPIs:
            kpis.setdefault(kpi, []).append(random.uniform(0, 10))

    current_time = current_time + RESOLUTION

df = pandas.DataFrame({'time': times, 'carrier_id': carrier_ids, 'asset_id': asset_ids_, 'asset_class': asset_classes, 'asset_name': asset_names, 'capabilities': capabilities, 'simulation_run': simulation_runs, 'simulation_type': simulation_types, **kpis})
print(df)
df.to_parquet('test.parquet')
