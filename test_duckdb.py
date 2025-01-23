import time
import uuid
import datetime
import random

import duckdb
import pyarrow.fs as arrow_fs
import pandas

NUM_OF_ASSETS = 250
KPIs = ["HeatIn_Q1", "Heat_flow1", "PostProc_Velocity1", "HeatIn_Q2", "Heat_flow2", "PostProc_Velocity2", "HeatIn_Q3", "Heat_flow3", "PostProc_Velocity3", "HeatIn_Q4"]
START_DATETIME = datetime.datetime.fromisoformat('2020-01-01T00:00:00+00:00')
#END_DATETIME = datetime.datetime.fromisoformat('2020-01-02T00:00:00+00:00')
END_DATETIME = datetime.datetime.fromisoformat('2021-01-01T00:00:00+00:00')
RESOLUTION = datetime.timedelta(minutes=15)

CARRIER_IDS = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
SIMULATION_RUN_ID = str(uuid.uuid4())

esdl_id = str(uuid.uuid4())
asset_ids = [str(uuid.uuid4()) for _ in range(0, NUM_OF_ASSETS)]


sql_conn = duckdb.connect(':memory:')

sql_conn.sql("set memory_limit = '500MB';")
sql_conn.sql('SET threads TO 1;')

df_times = []
df_kpis = {}
df_asset_ids = []
df_carrier_ids = []
first = True
current_time = START_DATETIME
while current_time < END_DATETIME:
    for carrier_i, carrier_id in enumerate(CARRIER_IDS):
        for asset_i, asset_id in enumerate(asset_ids):
            df_times.append(current_time)

            for kpi in KPIs:
                df_kpis.setdefault(kpi, []).append(random.uniform(0, 10))
            df_asset_ids.append(asset_id)
            df_carrier_ids.append(carrier_id)

    test_df = pandas.DataFrame({'time': df_times, 'asset_id': df_asset_ids, 'carrier_id': df_carrier_ids, **df_kpis})
    if first:
        first = False
        # create a new table from the contents of a DataFrame
        sql_conn.execute("CREATE TABLE test_df_table AS SELECT * FROM test_df")
    else:
        # insert into an existing table from the contents of a DataFrame
        sql_conn.execute("INSERT INTO test_df_table SELECT * FROM test_df")

    df_times = []
    df_asset_ids = []
    df_carrier_ids = []
    df_kpis = {}

    print(f'Done timestep: {current_time} / {END_DATETIME}')

    current_time = current_time + RESOLUTION

print(sql_conn.execute('SELECT * FROM test_df_table limit 10').df())



# Causes an OOM due to https://github.com/duckdb/duckdb/issues/11817 if immediately written to S3
before_subquery = time.time()
print(sql_conn.execute(f"COPY (SELECT * FROM test_df_table ORDER BY asset_id, carrier_id) TO '/tmp/{esdl_id}/' (FORMAT PARQUET, PARTITION_BY (asset_id, carrier_id), OVERWRITE_OR_IGNORE);"))
after_subquery = time.time()
print(f'Subquery order by took {after_subquery - before_subquery} seconds')

s3 = arrow_fs.S3FileSystem(access_key='test',
                           secret_key='12345678',
                           scheme='http',
                           endpoint_override='localhost:9000')

print('Moving parquet files to minio')
arrow_fs.copy_files(f'file:///tmp/{esdl_id}', f'test-parquet/{esdl_id}', destination_filesystem=s3)

sql_conn.sql("""
CREATE SECRET secret1 (
    TYPE S3,
    PROVIDER CREDENTIAL_CHAIN,
    CHAIN 'env;config',
    REGION 'XX-XXXX-X       ',
    ENDPOINT 'localhost:9000',
    URL_STYLE 'path',
    USE_SSL false,
    KEY_ID 'test',
    SECRET '12345678'
);
""")

print(sql_conn.sql(f'SELECT time, asset_id, HeatIn_Q1 FROM read_parquet([\'s3://test-parquet/{esdl_id}/*/*/*.parquet\']);').df())

print('done!')
