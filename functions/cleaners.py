"""
Functions which cleanes data from
DanMax : measument data,
Haldor Topsøe:  MS data, Heater data, Flow data.
"""

import pandas as pd
import numpy as np

def fill_timegaps(df_in, timestamp_name="XRDTimeStamp", threshold=30, freq="10S", fill_vals=np.nan, xscans=False):
    """Function which fills in time series dataframes where time data is missing.

    Args:
        df_in (dataframe): Timeseries Dataframe with gaps in the time sequency.
        timestamp_name (str, optional): Column containing the time stamps.
        threshold (int, optional): Time gap duration threshold in seconds.
        freq (str, optional): Time frequency for filling in the time gaps. Default to "10S".
        fill_vals (np.nan, optional): Value to fill in the gaps.
        xscans (bool, optional): If data is divided in xscans. Defaults to false.

    Returns:
        (dataframe): fill_timegaps
    """
    
    #check that the datetime column is the first column
    timecolumn = [key for key in dict(df_in.dtypes) if np.issubdtype(df_in.dtypes[key], np.datetime64)]
    
    if timecolumn:
        current_cols = df_in.columns.to_list()
        stripped_cols = [c for c in current_cols if c not in timecolumn]
        rearranged_cols = timecolumn + stripped_cols
        df_in = df_in[rearranged_cols]  # We moved the datetime columns to the first position.
        
    df = df_in.copy()
    dfD = df[timestamp_name].diff()
    n = len(dfD[dfD.dt.total_seconds() > threshold].index.to_list())
    
    for i in range(n):
        df.reset_index(inplace=True, drop=True)
        #print(df)
        df_delta = df[timestamp_name].diff()
        idx = df_delta[df_delta.dt.total_seconds() > threshold].index.to_list()[0]

        # Create dummy dataframes
        r = pd.date_range(start=df[timestamp_name].iloc[idx-1], end=df[timestamp_name].iloc[idx], freq=freq)
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
        
        if xscans:
            df = df.reset_index()
            #print(df)
            posx = df.x.unique()[:-1]
            num_nan = len(df[pd.isnull(df['x'])].index.to_list())
            first_idx = df[pd.isnull(df['x'])].index.to_list()[0]
            last_idx = df[pd.isnull(df['x'])].index.to_list()[-1]
            first = df.loc[first_idx-1]['x']
            f = np.where(posx == first)[0][0]
            vals = []
            i = 0
            for j in range(num_nan):
                if f+i == len(posx):
                    f, i = 0, 0

                idx = posx[i+f]
                i += 1
                vals.append(idx)
                
            df.loc[first_idx:last_idx, 'x'] = vals
            
    
    #df = df.reset_index().drop(columns='index')
            
    return df