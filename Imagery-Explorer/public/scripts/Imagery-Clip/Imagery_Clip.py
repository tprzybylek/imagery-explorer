import os, sys
from osgeo import gdal

#####################################################
raster = 'D:\\test\\S1B_IW_GRDH_1SDV_20170101T045911_20170101T045940_003650_006425_45AB.SAFE\\measurement\\s1b-iw-grd-vh-20170101t045911-20170101t045940-003650-006425-002.tiff'

WKT_Projection = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'

raster_georef = 'D:\\test\\raster_georef.tiff'
raster_output = 'D:\\test\\raster_output.tiff'
raster_output2 = 'D:\\test\\raster_output2.tiff'

#####################################################

def cutByBBox (minX, maxX, minY, maxY):

    dataset = gdal.Open(raster)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize

    #################################################

    GCPs = dataset.GetGCPs()

    GCPX = []
    GCPY = []

    for a, val in enumerate(GCPs):
        GCPX.append(GCPs[a].GCPX)
        GCPY.append(GCPs[a].GCPY)

    geotransform = {'minX':min(GCPX), 'maxX':max(GCPX), 'minY':min(GCPY), 'maxY':max(GCPY)}

    #################################################

    geotransform = [geotransform['minX'], (geotransform['maxX']-geotransform['minX'])/cols, 0, geotransform['maxY'], 0, (geotransform['maxY']-geotransform['minY'])/rows*(-1)]

    error_threshold = 0.125
    resampling = gdal.GRA_NearestNeighbour

    dataset_middle = gdal.AutoCreateWarpedVRT(dataset, None, WKT_Projection, resampling, error_threshold)
    
    dataset_middle.SetGeoTransform(geotransform)
    dataset_middle.SetProjection(WKT_Projection)
    dataset_middle.SetGCPs(GCPs, WKT_Projection)
    
    print dataset_middle.GetGeoTransform()

    #################################################

    xOrigin = geotransform[0]
    yOrigin = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]

    i1 = int((minX - xOrigin) / pixelWidth)
    j1 = int((minY - yOrigin) / pixelHeight)
    i2 = int((maxX - xOrigin) / pixelWidth)
    j2 = int((maxY - yOrigin) / pixelHeight)

    new_cols = i2 - i1 + 1
    new_rows = j1 - j2 + 1

    data = dataset_middle.ReadAsArray(i2, j2, new_cols, new_rows)

    #################################################

    newX = xOrigin + i1 * pixelWidth
    newY = yOrigin + j2 * pixelHeight

    new_transform = (newX, pixelWidth, 0, newY, 0, pixelHeight)

    dst_ds = gdal.GetDriverByName('GTiff').Create(raster_output, new_cols, new_rows, bands = 1, eType = gdal.GDT_Byte)

    dst_ds.SetGeoTransform(new_transform)
    dst_ds.SetProjection(WKT_Projection)
    dst_ds.SetGCPs(GCPs, WKT_Projection)

    dst_ds.GetRasterBand(1).WriteArray(data)

    print dst_ds.GetGeoTransform()

    dataset = None
    dst_ds = None
    dataset_middle = None
    dataset_middle_crop = None
    

cutByBBox(18.30, 18.80, 54.30, 54.80)