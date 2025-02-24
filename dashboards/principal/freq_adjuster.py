"""
Creado el 30/6/2022 a las 11:06 a. m.

@author: jacevedo
"""
import pandas as pd

def convert_data(df):
    df = pd.DataFrame().from_dict(df)
    for c in df.columns[df.columns.str.contains('fecha')]:
        df[c] = pd.to_datetime(df[c])
    return df

def adjust_freq(data, freq, tab):
    # print(data.head())
    data = convert_data(data)
    # print(data.head())
    amount_of_periods = data.fecha_creacion.dropna().apply(
        lambda x: pd.to_datetime(x).to_period(freq).start_time).nunique()
    if tab == 'tab-rankings':
        if freq == 'D' and amount_of_periods > 14:
            freq = 'W-MON'
            amount_of_periods = data.fecha_creacion.dropna().apply(
                lambda x: pd.to_datetime(x).to_period(freq).start_time).nunique()
        if freq == 'W-MON' and amount_of_periods > 12:
            freq = 'M'
            amount_of_periods = data.fecha_creacion.dropna().apply(
                lambda x: pd.to_datetime(x).to_period(freq).start_time).nunique()
        if freq == 'M' and amount_of_periods > 12:
            freq = 'Y'
        return freq
    elif tab == 'tab-flujo':
        if freq == 'D' and amount_of_periods > 42:
            freq = 'W-MON'
            amount_of_periods = data.fecha_creacion.dropna().apply(
                lambda x: pd.to_datetime(x).to_period(freq).start_time).nunique()
        if freq == 'W-MON' and amount_of_periods > 52:
            freq = 'M'
            amount_of_periods = data.fecha_creacion.dropna().apply(
                lambda x: pd.to_datetime(x).to_period(freq).start_time).nunique()
        if freq == 'M' and amount_of_periods > 18:
            freq = 'Y'
        return freq
    else:
        return freq