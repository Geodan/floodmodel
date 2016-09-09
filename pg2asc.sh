#!/bin/bash
left=$1
bottom=$2
right=$3
top=$4

if [ $# -lt 4 ]
  then
    echo "Not enough arguments supplied. Expected <left> <bottom> <right> <top>"
    exit 1
fi

mkdir tmp

echo "Exporting pointcloud to raster"
where="ST_Intersects(Geometry(pa),ST_Transform(ST_SetSrid(ST_MakeEnvelope($left,$bottom,$right,$top),32631),28992))"
echo "WHERE " $where
pdal pipeline ./config/pg2dem_pipeline.json --readers.pgpointcloud.where=$where

echo "Warping to UTM"
gdalwarp -s_srs 'EPSG:28992' -t_srs 'EPSG:32631'  -overwrite ./tmp/dtm.mean.tif ./tmp/dtm_utm.mean.tif

echo "Translating to ascii grid"
gdal_translate -of AAIGrid -a_nodata -9999 ./tmp/dtm_utm.mean.tif ./tmp/dtm_utm.mean.asc
echo "Projection    UTM
Zone          51
Datum         WGS84
Zunits        NO
Units         METERS
Spheroid      WGS84
Xshift        500000.0000000000
Yshift        10000000.0000000000
Parameters" > ./tmp/dtm_utm.mean.prj

echo "Writing extent file"
echo "$left, $bottom,
$left, $top,
$right, $top,
$right, $bottom" > ./config/extent.csv


echo "Done, files written to ./tmp"
