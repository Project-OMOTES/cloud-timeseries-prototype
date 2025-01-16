# Comparison between influxdb v1, postgresql & minio+parquet
250 assets, 35136 timesteps (1 year, 15 min resolution), 1 carrier, 10 KPI's

100% CPU == 1 core

| Action                                               | Influxdb v1             | PostgreSQL                                   | Minio+Parquet                                          |
|------------------------------------------------------|-------------------------|----------------------------------------------|--------------------------------------------------------|
| Query single KPI for single asset and single carrier | 0.30367 seconds         | 0.3081 seconds                               | 0.0186 seconds (using prefix,  pyarrow, localhost)     |
| Query single KPI for all assets and single carrier   | 63.23 seconds           | 14.416 seconds (due to join on time columns) | 0.9208 seconds (using filters, pyarrow, localhost)     |
| Storage usage                                        | ~1.5GB                  | 661MB ~ 1GB                                  | 667MB (polars, partitioned by asset_id and carrier_id) |
| CPU usage                                            | Uses >100% on 2nd query | Uses 100%  on 2nd query                      | Uses ~60% during benchmark                             |
| Memory usage                                         | Uses 3.2GB on 2nd query | Uses 1,3GB on 2nd query                      | Uses 370MB during benchmark                            | 


# Latency
On datacenter between 2 VM's (HESI):
```
DuckDB took 19.128907918930054 seconds which means 0.025505210558573407 second per q when accessing a single KPI individually for a single carrier and asset
DuckDB took 12.597334146499634 seconds which means 0.050389336585998534 second per q when accessing each profile individually for all carriers
DuckDB took 11.203127145767212 seconds which means 3.7343757152557373 second per q when accessing each carrier individually for all assets using WHERE
DuckDB took 10.246855735778809 seconds which means 3.415618578592936 second per q when accessing each carrier individually for all assets using partition key
DuckDB Took 3.842059373855591 seconds when accessing the profile for all assets at once for a single carrier
Pyarrow took 6.34181547164917 seconds to retrieve one kpi for all assets and carriers
Pyarrow took 8.10236382484436 seconds which means 0.03240945529937744 second per q to retrieve one kpi for a single asset and all carriers
Pyarrow took 4.392092943191528 seconds which means 1.4640309810638428 second per asset to retrieve one kpi for all assets and one carrier
Pyarrow took 32.70883631706238 seconds which means 0.13083534526824953 second per q to retrieve one kpi for one asset and one carrier using filters
Pyarrow took 6.256944179534912 seconds which means 0.02502777671813965 second per q to retrieve one kpi for one asset and one carrier using prefix
```
Peak link speed achieved: 1 Gbps <<-- (Ensure SSD/NVME storage, at least 1 Gbps network link between machines)

Locally:
```
DuckDB took 14.120677947998047 seconds which means 0.01882757059733073 second per q when accessing a single KPI individually for a single carrier and asset
DuckDB took 7.322590589523315 seconds which means 0.02929036235809326 second per q when accessing each profile individually for all carriers
DuckDB took 4.816350221633911 seconds which means 1.6054500738779705 second per q when accessing each carrier individually for all assets using WHERE
DuckDB took 4.761843681335449 seconds which means 1.5872812271118164 second per q when accessing each carrier individually for all assets using partition key
DuckDB Took 2.284662961959839 seconds when accessing the profile for all assets at once for a single carrier
Pyarrow took 2.88019061088562 seconds to retrieve one kpi for all assets and carriers
Pyarrow took 5.035520076751709 seconds which means 0.020142080307006836 second per q to retrieve one kpi for a single asset and all carriers
Pyarrow took 2.7862579822540283 seconds which means 0.9287526607513428 second per asset to retrieve one kpi for all assets and one carrier
Pyarrow took 18.681511402130127 seconds which means 0.0747260456085205 second per q to retrieve one kpi for one asset and one carrier using filters
Pyarrow took 3.3406684398651123 seconds which means 0.01336267375946045 second per q to retrieve one kpi for one asset and one carrier using prefix
```

# Difficulty when writing unpartitioned dataframes
- Check if dataframe can be partitioned upon adding data
- Check if we can append to existing files when simulator goes through new timesteps (e.g. Python generator across timesteps)
  - So simulator does not need to keep all timesteps in memory throughout the computation.
  - Answer: Cannot be done easily as Parquet files writes out per 'row group'. This is a group of rows/values of which metadata is created. 
    Normally this rowgroup should be 600-1000MB large so caching all this info is required up to this point. Tooling doesn't support this properly
    so we will need to either write out multiple files per partition (one file per dump) or cache it in custom code which then appends a rowgroup to
    an open file on a dump.

# Can we perform all queries from MapEditor/NWN-DTK frontend/ESDL-generic? 
?

# Where are we going to keep the metadata?
E.g. asset_class, asset_name etc. for an asset_id. Can always store an JSON or similar file.
Preferably something that we can retrieve with pyarrow as well.
An example structure could be:

```json
{ "esdl_metadata": {"some key": "some value"},
  "asset_metadata": {
    "asset_id": {
      "asset_class": "enum[HeatingDemand, ResidualHeatSource, Pipe]",
      "asset_name": "str",
      "capability": "enum[Consumer, Producer, Transport]",
      "carrier_ids": ["str"]
    }
  }
}
```

This could be versioned through JSON schema or something similar to ensure the document may
be parsed across various versions of ESDL metadata format.

# Hardware requirements
- NVME/SSD storage (otherwise SLOOOWW)
- `>= 1Gb` network link between minio storage & using components
