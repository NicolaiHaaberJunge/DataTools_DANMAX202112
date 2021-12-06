"""
Functions which parses data from
DanMax : measument data,
Haldor Topsøe:  MS data, Heater data, Flow data.
"""

import pandas as pd
import re
import os

def every_10th_scan(folder, keyname=".txt"):
    
    wanted_files = sorted([f for f in os.listdir(folder) if f.endswith(".txt")])

    output_file = open(os.path.join(folder, "combined.txt"), "a+")
    for file in wanted_files:
        with open(os.path.join(folder,file), "r") as f:
            lines = f.readlines()
            for line in lines:
                idx  = int(line.split(',')[0])
                if idx % 10 == 0:
                    output_file.write(line)

    output_file.close()
    
    
def join_xrd_topas(dftp, dfxrd):
    
    dftp = pd.merge(dftp, dfxrd, on="scan")
    dftp = dftp.set_index("XRDTimeStamp")
    dftp.index = dftp.index.floor(freq="s")
    dftp.index.name = "XRDTimeStamp"
    dftp = dftp.reset_index()
    
    return dftp


def danmax_xrd(file, timestamp_name="XRDTimeStamp", xscan=False):
    """Function for parsing DanMax xrd data.

    Args:
        file (str): DanMax timestamp file, .txt

    Returns:
        (dataframe): Dataframe with xrd timestamp data.
    """
    
    
    
    df_xrd = pd.read_csv(
        file,
        sep=",",
        names=["scan", "sample" ,timestamp_name],
        parse_dates=[timestamp_name],
        date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S.%f')
    )

    return df_xrd

def topas(file):  
    """Function for parsing topas refined data.

    Args:
        file (str): Topas data file, .txt

    Returns:
        (dataframe): Dataframe with topas refined data.
    """

    df_topas = pd.read_csv(file, sep=':', names=[i for i in range(0, 150)])
    df_topas.dropna(axis=1, how="all", inplace=True)
    df_topas.set_index(0, inplace=True)
    df_topas.index.name = "scan"
    new_col_names = dict(zip(df_topas.iloc[:, 1::2].columns.to_list(), df_topas.iloc[0, ::2].values))
    df_topas.rename(columns=new_col_names, inplace=True)
    df_topas = df_topas.iloc[:, 1::2]
    df_topas.reset_index(inplace=True)
    df_topas.rename(columns=lambda x: x.strip(), inplace=True)
    return df_topas

def heater(file, sheet_name="Log", timestamp_name="HistoricalTimeString"):
    """Function for parsing data from Topsøe MS system into a pandas dataframe.

    Args:
        file (str): Heater data file, .xlsm
        sheet_name (str, optional): Sheet Name in the excel file. Defaults to "Log".
        timestamp_name (str, optional): The column name containing the timestamp in the excel file. 
                                        Defaults to "HistoricalTimeString".

    Returns:
        (dataframe): Dataframe with heater data.
    """

    df_heater = pd.read_excel(
        file, sheet_name=sheet_name,
        parse_dates=[timestamp_name],
        date_parser=lambda x: pd.to_datetime(x, format='%d-%m-%y %H:%M:%S'))
    
    return df_heater

def ms(file):
    """Function for parsing data from Topsøe MS system into a pandas dataframe.

    Args:
        file (str): MS data file, .asc.

    Returns:
        (dataframe): Dataframe with MS data.
    """
    
    # findinx sections of relevant data in MS data file.
    idx = []
    with open(file, "r") as f:  # Finding relevant indexes
        lines = f.readlines()

        for i in range(len(lines)):
            line = lines[i]
            if re.search(r"^Datablock", line):
                idx.append(i)

            if re.search(r"^Cycle", line):
                idx.append(i)

    # Reading in data to dataframes
    df_mz_values = pd.read_csv(file,
                        skiprows=idx[0]+1,
                        nrows=idx[1]-idx[0]-2,
                        names=range(15),
                        usecols=[0, 1],
                        sep="\t",
                        engine="python",
                        skip_blank_lines=False)

    df_ms_data = pd.read_csv(file,
                             skiprows=idx[1],
                             sep="\t",
                             engine="python")

    # Cleaning Column Names
    mz_vals = dict(zip(df_mz_values[0], df_mz_values[1].astype(int)))  # Getting the mz values

    df_ms_data.rename(columns=mz_vals, inplace=True)
    df_ms_data.drop(columns=df_ms_data.columns[-1], inplace=True) 
    df_ms_data.drop(columns=[col for col in df_ms_data.columns if bool(re.search("Threshold", str(col)))], inplace=True )

    # Creating timestamp column from Date and Time columns.

    df_ms_data['MSTimeStamp'] = (df_ms_data[['Date', 'Time']]).agg(' '.join, axis=1)
    df_ms_data.drop(columns=['Time', "Date"], inplace=True)
    df_ms_data = df_ms_data.set_index("MSTimeStamp").reset_index()
    df_ms_data["MSTimeStamp"] = df_ms_data["MSTimeStamp"].apply(lambda x: pd.to_datetime(x , format="%d-%m-%Y %H:%M:%S:%f"))
    
    return df_ms_data

def gas_system(file, timestamp_name="Timestamp"):
    """Function for parsing data from Topsøe gas system into a pandas dataframe.

    Args:
        file (str): gas system data file.
        timestamp_name (str, optional): The column name containing the timestamp in the gas system data file.

    Returns:
        (dataframe): Dataframe with heater data.
    """

    df_gas = pd.read_csv(
        file, sep="\t",
        skiprows=[0, 2],
        parse_dates=[timestamp_name],
        date_parser=lambda x: pd.to_datetime(x, format="%d-%m-%Y %H:%M:%S.%f"))

    return df_gas