import datetime
import random
import uuid

import polars

NUM_OF_ASSETS = 250
KPIs = ["HeatIn_Q1", "Heat_flow1", "PostProc_Velocity1", "HeatIn_Q2", "Heat_flow2", "PostProc_Velocity2", "HeatIn_Q3", "Heat_flow3", "PostProc_Velocity3", "HeatIn_Q4"]
START_DATETIME = datetime.datetime.fromisoformat('2020-01-01T00:00:00+00:00')
END_DATETIME = datetime.datetime.fromisoformat('2021-01-01T00:00:00+00:00')
RESOLUTION = datetime.timedelta(minutes=15)

CARRIER_IDS = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
SIMULATION_RUN_ID = str(uuid.uuid4())

esdl_id = str(uuid.uuid4())
asset_ids = [str(uuid.uuid4()) for _ in range(0, NUM_OF_ASSETS)]


df_times = []
df_kpis = {}
df_asset_ids = []
df_carrier_ids = []
for carrier_id in CARRIER_IDS:
    for asset_i, asset_id in enumerate(asset_ids):
        current_time = START_DATETIME

        while current_time < END_DATETIME:
            df_times.append(current_time)

            for kpi in KPIs:
                df_kpis.setdefault(kpi, []).append(random.uniform(0, 10))
            df_asset_ids.append(asset_id)
            df_carrier_ids.append(carrier_id)
            current_time = current_time + RESOLUTION

        print(f'Done {asset_i}/{len(asset_ids)}')

print('Writing out results')
df = polars.DataFrame({'time': df_times, 'asset_id': df_asset_ids, 'carrier_id': df_carrier_ids, **df_kpis})
df.write_parquet(f'single_file_per_asset_part_with_carrier/{esdl_id}', partition_by=['asset_id', 'carrier_id'])
print('Done!')
