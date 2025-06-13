
## DEM Pre-Processing and Covariate Generator
One of the key scripts in this repository, `terrain_covariates_pipeline.py`, implements a full workflow for generating terrain-derived covariates from a raw DEM. These covariates are intended for use in machine learning-based land cover and wetland classification models.

### Key Steps Included:
- **DEM smoothing** (feature-preserving)
- **Depression breaching** using least-cost methods
- **Flow accumulation** using both D8 and D∞ algorithms
- **Stream network extraction** from contributing area thresholds
- **Stochastic depression analysis** (PDEP)
- **Topographic Wetness Index (TWI)**
- **Canopy Height Model (CHM)** from DSM and DEM
- **Solar exposure metrics** via time-in-daylight analysis

All outputs are saved as GeoTIFFs or shapefiles, and the script is structured for modularity and reproducibility.

### Tools Used
This script is built using the [Whitebox Workflows Python API](https://pypi.org/project/whitebox-workflows/). Each tool used is documented in detail in the [Whitebox User Manual](https://www.whiteboxgeo.com/manual/wbw-user-manual/book/tool_help.html), which provides technical background on how tools are derived and what each output represents.

### Use Case
This workflow was originally developed as part of a wetland mapping project across the Canadian portion of the Great Lakes–St. Lawrence River Basin, where terrain-derived metrics are essential for identifying wetland structure and extent at landscape scales.

---
