"""
Function for interpolative merging of timeseries dataframes.
"""

import pandas as pd
import numpy as np


def interpolative_merge(df1, df2, df1_time, df2_time, columns, floor=[], inplace=False):
    """Functions which merges pandas timeseries dataframes by interpolating data.

    Args:
        df1 (dataframe): The dataframe to merge data into.
        df2 (dataframe): The dataframe to merge data from.
        df1_time (str): Column name for timeseries in df1
        df2_time (str): Column name for timeseried in df2
        columns (list): Columns from df2 to be merged and interpolated into df1
        floor (list, optional): Columns in df2 which should be floored, rounding down to nearest int. Defaults to [].
        inplace (bool, optional): If True, the merge will overwrite df1. Defaults to False.

    Returns:
        (dataframe): Merged and interpolated dataframe.
    """
    
    if inplace:
        df = df1
    else:
        df = df1.copy()
        
    zero_point =  df1[df1_time][0]
    
    df1_zero_corrected = (df[df1_time] - zero_point).dt.total_seconds().to_numpy()
    df2_zero_corrected = (df2[df2_time] - zero_point).dt.total_seconds().to_numpy()

    for col in columns:
        values = df2[col].to_numpy()
        data_interpolated = np.interp(df1_zero_corrected, df2_zero_corrected, values)
        df[col] = data_interpolated  # Adding interpolated column from df2 to df1
        
    for col in floor:
        df[col] = df[col].apply(np.floor).astype(int)
    
    return df