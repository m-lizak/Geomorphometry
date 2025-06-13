# ------------------------------------------------------------------------------
# Terrain Covariate Generator for Wetland Classification Modeling
# Author: Maciej Lizak
#
# Description:
# This script generates a suite of terrain-derived covariates from a DEM for use 
# in land cover or wetland classification models. It leverages the Whitebox 
# Workflows Python API to preprocess the DEM (smoothing, breaching), compute 
# hydrological and geomorphometric indices (flow accumulation, TWI, CHM, etc.), 
# and export the results for downstream modeling tasks.
#
# Each tool used here is documented in the official Whitebox Workflows manual, 
# which provides detailed explanations of their derivation and interpretation:
# https://www.whiteboxgeo.com/manual/wbw-user-manual/book/tool_help.html
# ------------------------------------------------------------------------------


### Import Libraries & Declare Env Variables
from whitebox_workflows import WbEnvironment 

# Initialize Whitebox Workflows environment
wbe = WbEnvironment("YOUR_KEY_HERE")
wbe.max_procs = -1  # Use all available CPU cores
wbe.verbose = True  # Enable verbose logging

print("\nReading Rasters")
wbe.working_directory = '/home/mlizak/DEM_Processing/'

# Load raw input DEM
dem = wbe.read_raster('/home/mlizak/DEM_Processing/file_Inputs/dem.tif')

### DEM Pre-Processing (Smoothing and Depression Breaching)

print("\nSmoothing DEM")
# Apply feature-preserving smoothing to reduce noise while preserving edges
dem_smoothed = wbe.feature_preserving_smoothing(
    dem, 
    filter_size=10, 
    normal_diff_threshold=8.0, 
    iterations=3
)

# Save smoothed DEM
wbe.write_raster(dem_smoothed, "/home/mlizak/DEM_Processing/file_Outputs/dem_smoothed.tif", compress=True)
print("\nSaved Smoothed DEM")

# Load smoothed DEM
dem_smoothed = wbe.read_raster("/home/mlizak/DEM_Processing/file_Outputs/dem_smoothed.tif")

print("\nBreaching Depressions")
# Correct spurious depressions using least-cost breaching algorithm
dem_corrected = wbe.breach_depressions_least_cost(
    dem_smoothed,
    max_dist=7,
    fill_deps=False
)

# Save hydrologically corrected DEM
wbe.write_raster(dem_corrected, "/home/mlizak/DEM_Processing/file_Outputs/dem_corrected.tif", compress=True)
print("\nSaved Hydrologically Corrected DEM")

# Reload corrected DEM
dem_corrected = wbe.read_raster("/home/mlizak/DEM_Processing/file_Outputs/dem_corrected.tif")

### Hillshade Generation (Optional)
# hillshade = wbe.hillshade(dem_corrected, azimuth=315.0, altitude=30.0)
# wbe.write_raster(hillshade, "/home/mlizak/DEM_Processing/file_Outputs/corrected_hillshade.tif", compress=True)

### D8 Flow Accumulation
print("Running D8 Flow Accumulation")
d8 = wbe.d8_flow_accum(dem_corrected, out_type="specific contributing area")
wbe.write_raster(d8, "/home/mlizak/DEM_Processing/file_Outputs/d8.tif", compress=True)

### Stream Extraction
print("Running Stream Extraction")
# Threshold D8 output to extract stream network (threshold may need tuning)
streams = d8 > 12
streams_vector = wbe.raster_to_vector_lines(streams)
wbe.write_vector(streams_vector, "/home/mlizak/DEM_Processing/file_Outputs/streams_vector.shp")

### D∞ Flow Accumulation
print("Running D∞ Flow Accumulation")
dinf = wbe.d_inf_flow_accumulation(
    dem_corrected, 
    out_type="Specific Contributing Area", 
    log=False
)
wbe.write_raster(dinf, "/home/mlizak/DEM_Processing/file_Outputs/dinf.tif", compress=True)

### Depth to Water Estimation (Optional)
# print("Running Depth To Water")
# depth = wbe.depth_to_water(dem_corrected, streams)
# wbe.write_raster(depth, "/home/mlizak/DEM_Processing/file_Outputs/depthToWater.tif", compress=True)

### Stochastic Depression Analysis (Very Memory Intensive)
print("Running Stochastic Depression Analysis")
pdep = wbe.stochastic_depression_analysis(
    dem_corrected,
    rmse=1.63,
    range=90,
    iterations=100
)
wbe.write_raster(pdep, "/home/mlizak/DEM_Processing/file_Outputs/pdep.tif", compress=True)

### Topographic Wetness Index
print("Computing Topographic Wetness Index")
slope = wbe.read_raster('/home/mlizak/DEM_Processing/file_Inputs/slope.tif')
twi = wbe.wetness_index(sca=dinf, slope=slope)
wbe.write_raster(twi, "/home/mlizak/DEM_Processing/file_Outputs/twi.tif", compress=True)

### Canopy Height Model
print("Computing Canopy Height Model")
dsm = wbe.read_raster('/home/mlizak/DEM_Processing/file_Inputs/dsm.tif')
chm = wbe.subtract(dsm, dem_corrected)
wbe.write_raster(chm, "/home/mlizak/DEM_Processing/file_Outputs/canopyHeight.tif", compress=True)

### Time in Daylight (based on terrain and solar geometry)
print("Computing Time in Daylight")
timeInDaylight = wbe.time_in_daylight(
    dsm, 
    lat=44.938,
    long=-82.495, 
    az_fraction=15.0, 
    max_dist=100.0, 
    utc_offset="-05:00", 
    start_day=91,   # Approx. April 1st
    end_day=273,    # Approx. September 30th
    start_time="00:00:00", 
    end_time="23:59:59"
)
wbe.write_raster(timeInDaylight, "/home/mlizak/DEM_Processing/file_Outputs/timeInDaylight")

### License Check (Optional or For Specific Tools)
wbe.check_in_license("crowded-drinking-goshawks")
