# Comparison between influxdb v1, postgresql & minio+parquet
250 assets, 35136 timesteps (1 year, 15 min resolution), 1 carrier, 10 KPI's

100% CPU == 1 core

| Action                                               | Influxdb v1             | PostgreSQL                                   | Minio+Parquet                                          |
|------------------------------------------------------|-------------------------|----------------------------------------------|--------------------------------------------------------|
| Query single KPI for single asset and single carrier | 0.30367 seconds         | 0.3081 seconds                               | 0.0186 seconds (using prefix,  pyarrow)                |
| Query single KPI for all assets and single carrier   | 63.23 seconds           | 14.416 seconds (due to join on time columns) | 0.9208 seconds (using filters, pyarrow)                |
| Storage usage                                        | ~1.5GB                  | 661MB ~ 1GB                                  | 667MB (polars, partitioned by asset_id and carrier_id) |
| CPU usage                                            | Uses >100% on 2nd query | Uses 100%  on 2nd query                      | Uses ~60% during benchmark                             |
| Memory usage                                         | Uses 3.2GB on 2nd query | Uses 1,3GB on 2nd query                      | Uses 370MB during benchmark                            | 


# Latency
Test between 2 VM's

# Difficulty when writing unpartitioned dataframes
- Check if dataframe can be partitioned upon adding data
- Check if we can append to existing files when simulator goes through new timesteps (e.g. Python generator across timesteps)
  - So simulator does not need to keep all timesteps in memory throughout the computation.

# Can we perform all queries from Ewoud/MapEditor 


# Where are we going to keep the metadata?
E.g. asset_class, asset_name etc. for an asset_id. Can always store an JSON or similar file.
Preferably something that we can retrieve with pyarrow as well.

# Hardware requirements
NVME/SSD storage (otherwise SLOOOWW)
