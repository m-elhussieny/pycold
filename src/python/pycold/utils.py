import numpy as np
from datetime import datetime
import pandas as pd
from os.path import join
import gdal

NAN_VAL = -9999


def get_block_y(block_id, n_block_x):
    """
    Parameters
    ----------
    block_id: integer
    n_block_x: integer, number of blocks at x xis

    Returns
    -------
    current block id at y axis
    """
    return int((block_id - 1) / n_block_x) + 1


def get_block_x(block_id, n_block_x):
    """
    Parameters
    ----------
    block_id: integer
    n_block_x: integer, number of blocks at x xis

    Returns
    -------
    current block id at x axis
    """
    return (block_id - 1) % n_block_x + 1


def get_col_index(pos, n_cols, current_block_x, block_width):
    """
    Parameters
    ----------
    pos
    n_cols
    current_block_x
    block_width

    Returns
    -------

    """
    return int((pos - 1) % n_cols) - (current_block_x - 1) * block_width


def get_row_index(pos, n_cols, current_block_y, block_height):
    """
    Parameters
    ----------
    pos: start from 1
    n_cols
    current_block_y
    block_height

    Returns
    -------

    """
    return int((pos - 1) / n_cols) - (current_block_y - 1) * block_height
    

def assemble_cmmaps(config, result_path, cmmap_path, starting_date, n_cm_maps, keyword):
    """
    this function reorganized block-based fix-interval CM intermediate files into map-based output (one map per interval)
    Parameters
    ----------
    config: dictionary
        pycold config dictionary
    result_path: string
        the path where block-based CM intermediate files are
    cmmap_path: string
        the path to save the new map-based output
    starting_date: integer
        the starting date of the dataset
    n_cm_maps: integer
        the number of change magnitude outputted per pixel
    keyword: {'CM', 'CM_date', 'CM_direction'}
    Returns
    -------

    """
    if keyword == 'CM':
        output_type = np.int16
    elif keyword == 'CM_date':
        output_type = np.int32
    elif keyword == 'CM_direction':
        output_type = np.uint8

    cm_map_list = [np.full((config['n_rows'], config['n_cols']),
                           NAN_VAL, dtype=output_type) for x in range(n_cm_maps)]
    for iblock in range(config['n_blocks']):
        current_block_y = int(np.floor(iblock / config['n_block_x'])) + 1
        current_block_x = iblock % config['n_block_y'] + 1
        try:
            cm_block = np.load(join(result_path, '{}_x{}_y{}.npy'.format(keyword, current_block_x, current_block_y)))
        except OSError as e:
            print('Reading CM files fails: {}'.format(e))
        #    continue

        cm_block_reshape = np.reshape(cm_block, (config['block_width'] * config['block_height'],
                                                 n_cm_maps))
        hori_profile = np.hsplit(cm_block_reshape, n_cm_maps)
        for count, maps in enumerate(cm_map_list):
            maps[(current_block_y - 1) * config['block_height']:current_block_y * config['block_height'],
            (current_block_x - 1) * config['block_width']:current_block_x * config['block_width']] = \
                hori_profile[count].reshape(config['block_height'], config['block_width'])

    # output cm images
    for count, cm_map in enumerate(cm_map_list):
        ordinal_date = starting_date + count * config['CM_OUTPUT_INTERVAL']
        outfile = join(cmmap_path, '{}_maps_{}_{}{}.npy'.format(keyword, str(ordinal_date),
                                                                pd.Timestamp.fromordinal(ordinal_date - 366).year,
                                                                get_doy(ordinal_date)))
        np.save(outfile, cm_map)


def get_rowcol_intile(pos, block_width, block_height, block_x, block_y):
    """
    calculate row and col in original images based on pos index and block location
    Parameters
    ----------
    pos: integer
        position id of the pixel (i.e., i_row * n_cols + i_col + 1)
    block_width: integer
        the width of each block
    block_height: integer
        the height of each block
    block_x:integer
        block location at x direction
    block_y:integer
        block location at y direction
    Returns
    -------
    (original_row, original_col)
    row and col number (starting from 1) in original image (e.g., Landsat ARD 5000*5000)
    """
    original_row = int(pos / block_width + (block_y - 1) * block_height + 1)
    original_col = int(pos % block_width + (block_x - 1) * block_width + 1)
    return original_row, original_col


def gdal_save_file_1band(out_path, array, gdal_type, trans, proj, cols, rows, image_format='GTiff'):
    """
    save array as tiff format
    Parameters
    ----------
    out_path : full outputted path
    array : numpy array to be saved
    gdal_type: gdal type
    trans: transform coefficients
    proj: projection
    rows: the row number
    cols: the col number
    image_format: default is GTiff
    Returns
    -------
    TRUE OR FALSE
    """
    outdriver = gdal.GetDriverByName(image_format)
    outdata = outdriver.Create(out_path, cols, rows, 1, gdal_type)
    if outdata == None:
        return False
    outdata.GetRasterBand(1).WriteArray(array)
    outdata.FlushCache()
    outdata.SetGeoTransform(trans)
    outdata.FlushCache()
    outdata.SetProjection(proj)
    outdata.FlushCache()
    return True


def get_time_now(tz):
    """
    Parameters
    ----------
    tz: string

    Returns
    -------
    datatime format of current time
    """
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')


def get_doy(ordinal_date):
    """
    Parameters
    ----------
    ordinal_date: int
    a ordinal date (MATLAB-format ordinal date)

    Returns: string
    -------
    doy
    """
    return str(pd.Timestamp.fromordinal(ordinal_date-366).timetuple().tm_yday).zfill(3)


def get_anchor_days(starting_day, n_cm_maps, interval):
    """
    get a list of starting days for each change magnitude time slices
    Parameters
    ----------
    starting_days
    n_cm_maps
    interval

    Returns
    -------

    """
    return np.arange(start=starting_day, stop=starting_day + n_cm_maps * interval,
                     step=interval)
