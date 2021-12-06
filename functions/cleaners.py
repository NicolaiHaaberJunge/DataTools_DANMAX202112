"""
Functions which cleanes data from
DanMax : measument data,
Haldor Topsøe:  MS data, Heater data, Flow data.
"""

import pandas as pd
import numpy as np

def fill_timegaps(df_in, timestamp_name="XRDTimeStamp", threshold=30, freq="10S", fill_vals=np.nan):
    """Function which fills in time series dataframes where time data is missing.

    Args:
        df_in (dataframe): Timeseries Dataframe with gaps in the time sequency.
        timestamp_name (str, optional): Column containing the time stamps.
        threshold (int, optional): Time gap duration threshold in seconds.
        freq (str, optional): Time frequency for filling in the time gaps. Default to "10S".
        fill_vals (np.nan, optional): Value to fill in the gaps.

    Returns:
        (dataframe): fill_timegaps
    """
    
    df = df_in.copy()
    dfD = df[timestamp_name].diff()
    n = len(dfD[dfD.dt.total_seconds() > threshold].index.to_list())
    
    for i in range(n):
        df.reset_index(inplace=True)        
        df_delta = df[timestamp_name].diff()
        idx = df_delta[df_delta.dt.total_seconds() > threshold].index.to_list()[0]

        # Create dummy dataframes
        r = pd.date_range(start=df.XRDTimeStamp.iloc[idx-1], end=df.XRDTimeStamp.iloc[idx], freq=freq)
        df_ny = df.copy().loc[0:r.shape[0]-1]
        df_ny.set_index(timestamp_name, inplace=True)

        df_ny.loc[:] = fill_vals
        df_ny.index = r
        df_ny.index.name = timestamp_name

        # Create dummy dataframes
        df.set_index(timestamp_name, inplace=True)

        df1 = df.iloc[:idx-1, :]
        df2 = df.iloc[idx:, :]

        df = pd.concat([df1, df_ny, df2], axis=0)

    return df.reset_index().drop(columns='index')