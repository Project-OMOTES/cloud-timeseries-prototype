import time

import duckdb

con = duckdb.connect(":memory:")
con.sql("""
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

start = time.time()
print(len(con.sql('SELECT time, PostProc_Velocity1 FROM read_parquet([\'s3://test-parquet/test.parquet\']) WHERE asset_id = \'77563ead-7bba-4739-abb4-47b415655062\';').fetchall()))
end = time.time()

print(f'Took {end - start} seconds')
