"""
Creado el 24/6/2022 a las 4:16 p. m.

@author: jacevedo
"""
from dash import dcc
from pandas import Grouper, DataFrame
import plotly.express as px
from prousuario_tools import get_sb_colors
colors = get_sb_colors()


SLIDER_LAYOUT = dict(
        # rangeselector=dict(
        #     buttons=list([
        #         # dict(step="all", label='lodo'),
        #         dict(count=7,
        #              label="7d",
        #              step="day",
        #              stepmode="backward"),
        #         dict(count=30,
        #              label="30d",
        #              step="day",
        #              stepmode="backward"),
        #         dict(count=56,
        #              label="8w",
        #              step="day",
        #              stepmode="backward"),
        #     ])
        # ),
        rangeslider=dict(
            visible=True,
            thickness=0.1,
        ),
        type="date",
        autorange=True
    )

def agrupador(data, date_col, freq='D'):
    grupero = Grouper(key=date_col, freq=freq)
    data = data.groupby(grupero).size()
    return data

def flujo_frame(entradas, salidas, freq='D'):
    flujo = DataFrame([
    agrupador(entradas, 'fecha_creacion', freq=freq),
    agrupador(salidas, 'fecha_cierre', freq=freq)
    ], index=['Recibidas', 'Completadas']).T.fillna(0)
    return flujo

def flujo_figure(data):
    lane_shape = 'spline'
    if data.shape[0] > 333:
        lane_shape = 'linear'
    fig = px.line(
        data,
        line_shape=lane_shape,
        template='plotly_white',
        color_discrete_sequence=[colors['turquesa pro'], colors['naranja sb']],
        height=500,
        width=800,
        range_y=[0,data.values.max()*1.1],
        labels={'value': 'Cantidad', 'index': 'Fecha', 'variable': 'Métrica'}
    )
    fig.update_traces(
        mode='lines+markers',
        line_width=3,
        opacity = 0.8,
    )
    fig.update_layout(
        autosize=False,
        showlegend=True,
        xaxis=SLIDER_LAYOUT,
        paper_bgcolor='#0D3048',
        plot_bgcolor='#0A2336',
        font_color='#F0F3F5',
        legend=dict(orientation="h", yanchor="top", y=1.15, xanchor="left", x=0),
        legend_title=None
    )
    fig.update_xaxes(showgrid=False, gridwidth=1, gridcolor='Black')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='Black')
    promedio_entradas = data['Recibidas'].mean()
    promedio_salidas = data['Completadas'].mean()
    # desviacion = data.diarias.std()
    fig.add_hline(promedio_entradas, line_dash='dash', line_color=colors['turquesa pro'])
    fig.add_hline(promedio_salidas, line_dash='dash', line_color=colors['naranja sb'])
    # plot(fig)
    return fig

def creates_fig(entradas, salidas, freq='D'):
    data = flujo_frame(entradas, salidas, freq=freq)
    fig = flujo_figure(data)
    return fig

def creates_dcc(entradas, salidas, freq='D'):
    graph = dcc.Graph(
        figure=creates_fig(entradas, salidas, freq=freq),
        style=dict(width='50%', display='inline-block')
    )
    return graph