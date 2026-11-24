# SINDHU-DRISHTI-ML

An AI/ML-based geospatial hazard assessment pipeline for landslide and flood risk analysis, red-zone mapping, and village-level risk assessment.

## Project Structure

```text
SINDHU-DRISHTI-ML/
│
├── pipeline/
│   ├── data/
│   │   ├── outputs/
│   │   ├── processed/
│   │   └── raw/
│   │       ├── boundary/
│   │       ├── dem/
│   │       ├── landslide_inventory/
│   │       ├── landuse/
│   │       ├── population/
│   │       ├── rainfall/
│   │       ├── roads/
│   │       ├── soil/
│   │       └── villages/
│   │
│   ├── 01_prepare_dem.py
│   ├── 01b_prepare_stream_distance.py
│   ├── 01c_prepare_soil.py
│   ├── 02_prepare_rainfall.py
│   ├── 03_prepare_landslide_points.py
│   ├── 04_build_training_data.py
│   ├── 05_train_model.py
│   ├── 06_generate_redzone_map.py
│   ├── 07_prepare_population.py
│   ├── 08_village_risk_join.py
│   ├── 10_carrying_capacity.py
│   ├── 11_load_postgis.py
│   ├── 12_flood_hazard.py
│   ├── 13_prepare_landuse.py
│   └── config.py
│
├── run_pipeline.py
├── pipeline_run_log.txt
├── requirements.txt
├── .gitignore
└── README.md
```

## Key Features

- Geospatial DEM preprocessing and terrain analysis.
- Rainfall, soil, and stream-distance feature extraction.
- Landslide inventory preprocessing and training dataset generation.
- Random Forest-based landslide susceptibility prediction.
- District-wide red, yellow, and green hazard-zone mapping.
- Population and village-level risk assessment.
- Flood hazard analysis.
- PostGIS integration for geospatial data management.

## Technology Stack

- Python
- Scikit-learn
- NumPy and Pandas
- Rasterio and GDAL
- GeoPandas
- PyProj
- PostgreSQL and PostGIS

## Installation

```bash
git clone https://github.com/selva2006-GM/SINDHU-DRISHTI-ML.git

cd SINDHU-DRISHTI-ML

pip install -r requirements.txt
```

## Running the Pipeline

```bash
python run_pipeline.py
```

## Project Objective

To develop a geospatial machine learning system that combines terrain, rainfall, soil, population, and other geographic datasets to identify potential hazard-prone regions and support data-driven disaster risk assessment.

---

**SINDHU-DRISHTI-ML**  
*Geospatial Intelligence for Disaster Risk Assessment.*