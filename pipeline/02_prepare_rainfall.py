
"""
STEP 2: Prepare Rainfall

Uses complete June-September monsoon seasons from 2024 and 2025.
Calculates annual monsoon rainfall totals and their two-year mean.

Output:
data/processed/total_monsoon_rainfall.tif
"""

import glob
import os
import subprocess
import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd

import config


SELECTED_YEARS = ["2024", "2025"]
MONSOON_MONTHS = ["06", "07", "08", "09"]


def find_boundary_file():
    candidates = (
        glob.glob(os.path.join(config.BOUNDARY_RAW_DIR, "*.geojson"))
        + glob.glob(os.path.join(config.BOUNDARY_RAW_DIR, "*.shp"))
    )

    if not candidates:
        raise FileNotFoundError(
            f"No boundary file found in {config.BOUNDARY_RAW_DIR}"
        )

    return candidates[0]


def select_rainfall_files():
    all_files = sorted(
        glob.glob(os.path.join(config.RAINFALL_RAW_DIR, "*.tif"))
    )

    selected = {}

    for year in SELECTED_YEARS:
        selected[year] = {}

        for month in MONSOON_MONTHS:
            expected_name = f"chirps-v2.0.{year}.{month}.tif"

            matches = [
                f for f in all_files
                if os.path.basename(f) == expected_name
            ]

            if not matches:
                raise FileNotFoundError(
                    f"Missing rainfall file: {expected_name}"
                )

            selected[year][month] = matches[0]

    return selected


def main():
    print("=== STEP 2: Prepare Rainfall ===")

    if not os.path.exists(config.DEM_CLIPPED_UTM):
        raise FileNotFoundError(
            f"{config.DEM_CLIPPED_UTM} not found. "
            "Run 01_prepare_dem.py first."
        )

    # Get exact target grid from DEM
    with rasterio.open(config.DEM_CLIPPED_UTM) as src:
        target_bounds = src.bounds
        target_width = src.width
        target_height = src.height

    print(
        f"Target grid: {target_width} x {target_height}"
    )

    # Select complete monsoon seasons
    selected_files = select_rainfall_files()

    print("Selected monsoon seasons:")

    for year in SELECTED_YEARS:
        print(f"{year}:")
        for month, path in selected_files[year].items():
            print(f"  {os.path.basename(path)}")

    boundary = gpd.read_file(find_boundary_file())

    yearly_months = {}

    for year in SELECTED_YEARS:
        yearly_months[year] = []

        for month in MONSOON_MONTHS:
            fpath = selected_files[year][month]
            fname = os.path.splitext(os.path.basename(fpath))[0]

            # Clip to study boundary
            with rasterio.open(fpath) as src:
                boundary_reproj = boundary.to_crs(src.crs)

                out_image, out_transform = mask(
                    src,
                    boundary_reproj.geometry,
                    crop=True,
                    nodata=-9999,
                    filled=True
                )

                out_meta = src.meta.copy()

            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "nodata": -9999
            })

            clipped_path = os.path.join(
                config.PROCESSED_DIR,
                f"rainfall_{fname}_clipped.tif"
            )

            with rasterio.open(clipped_path, "w", **out_meta) as dst:
                dst.write(out_image)

            # Reproject and align exactly to DEM grid
            aligned_path = os.path.join(
                config.PROCESSED_DIR,
                f"rainfall_{fname}_utm.tif"
            )

            subprocess.run([
                "gdalwarp",
                "-t_srs", config.UTM_EPSG,
                "-te",
                str(target_bounds.left),
                str(target_bounds.bottom),
                str(target_bounds.right),
                str(target_bounds.top),
                "-ts",
                str(target_width),
                str(target_height),
                "-r", "bilinear",
                "-overwrite",
                "-dstnodata", "-9999",
                clipped_path,
                aligned_path
            ], check=True)

            # Read aligned monthly rainfall
            with rasterio.open(aligned_path) as src:
                data = src.read(1).astype("float64")
                data[data == -9999] = np.nan

            yearly_months[year].append(data)

            print(f"Processed: {fname}")

    # Calculate annual June-September rainfall totals
    annual_totals = []

    for year in SELECTED_YEARS:
        monthly_stack = np.stack(yearly_months[year])

        # Require all four months to be valid at each pixel
        valid_mask = np.all(
            np.isfinite(monthly_stack),
            axis=0
        )

        annual_total = np.sum(
            np.where(np.isfinite(monthly_stack), monthly_stack, 0),
            axis=0
        )

        annual_total[~valid_mask] = np.nan
        annual_totals.append(annual_total)

        print(
            f"{year} monsoon rainfall min/max: "
            f"{np.nanmin(annual_total):.2f} / "
            f"{np.nanmax(annual_total):.2f} mm"
        )

    # Calculate two-year mean
    annual_stack = np.stack(annual_totals)

    # Require valid data in both years
    valid_mask = np.all(
        np.isfinite(annual_stack),
        axis=0
    )

    mean_rainfall = np.mean(
        np.where(np.isfinite(annual_stack), annual_stack, 0),
        axis=0
    )

    mean_rainfall[~valid_mask] = np.nan

    # Save final raster
    first_aligned = selected_files["2024"]["06"]
    first_aligned_path = os.path.join(
        config.PROCESSED_DIR,
        f"rainfall_{os.path.splitext(os.path.basename(first_aligned))[0]}_utm.tif"
    )

    with rasterio.open(first_aligned_path) as src:
        profile = src.profile.copy()

    profile.update(
        dtype="float32",
        nodata=np.nan,
        compress="lzw"
    )

    with rasterio.open(config.RAINFALL_TOTAL_PATH, "w", **profile) as dst:
        dst.write(mean_rainfall.astype("float32"), 1)

    print(
        f"Two-year mean monsoon rainfall min/max: "
        f"{np.nanmin(mean_rainfall):.2f} / "
        f"{np.nanmax(mean_rainfall):.2f} mm"
    )

    print(f"Saved: {config.RAINFALL_TOTAL_PATH}")
    print("=== STEP 2 COMPLETE ===")


if __name__ == "__main__":
    main()
