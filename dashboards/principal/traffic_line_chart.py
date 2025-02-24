"""
Creado el 25/5/2022 a las 12:56 p. m.

@author: jacevedo
"""
import plotly.express as px
from plotly.offline import plot
from pandas import DataFrame
from tools.prousuario_tools import get_sb_colors

colors = get_sb_colors()





def create_rolling_periods(series):
    df = DataFrame(
        # [series, series.rolling(7, center=True, min_periods=1).mean(),
        # series.rolling(30, center=True, min_periods=1).mean()],
        [series,
         series.rolling(7, min_periods=1, center=True, win_type='gaussian').mean(std=3),
         series.rolling(30, min_periods=1, center=True, win_type='gaussian').mean(std=3)
         ],
        index=['diarias', 'promedio_7', 'promedio_30']
    ).T
    return df


def plot_line(data):
    data = create_rolling_periods(data)
    lane_shape = 'spline'
    if data[data.index>"2021-06-25"].shape[0] > 333:
        lane_shape = 'linear'
    fig = px.line(
        data,
        line_shape=lane_shape,
        template='plotly_white',
        # color_discrete_sequence=[colors['cold gray 88'], colors['sb gray light'], colors['naranja sb']],
        color_discrete_sequence=[colors['sb gray dark'], colors['turquesa pro'], colors['naranja sb']],
        height=500,
        labels={'value': 'Cantidad de Entradas', 'index': 'Fecha de Entrada', 'variable': 'Periodo'}
    )
    fig.update_traces(
        line_width=3
    )
    fig.update_xaxes(showgrid=False, gridwidth=1, gridcolor='Black')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='Black')
    promedio = data.diarias.mean()
    desviacion = data.diarias.std()
    fig.add_hline(promedio+desviacion, line_dash='dash', line_color='white')
    fig.add_hline(promedio-desviacion, line_dash='dash', line_color='white')
    # plot(fig)
    return fig

# grupero = Grouper(key='fecha_creacion', freq='D')
# data = create_rolling_periods(df.groupby(grupero).size())
# plot_line(data)
# fig = plot_line(data[data.index>"2021-06-25"])
# plot(fig)
# plot_bars(data)
