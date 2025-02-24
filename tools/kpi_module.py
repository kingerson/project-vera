"""
Creado el 5/12/2023 a las 3:51 p. m.

@author: jacevedo
"""

import plotly.express as px
from sql_tools import query_reader
from plotly import graph_objects as go
import infofinanciera_reading
import reclamos_reading
import contratos_reading
import pandas as pd
from datetime import datetime
from prousuario_tools import get_sb_colors

from datetime import date
from pandas.tseries.offsets import MonthEnd, MonthBegin

pd.options.mode.chained_assignment = None  # default='warn'

start_date = (date.today()-MonthBegin(13)).date()
end_date = (date.today()-MonthBegin(1)).date()



detalles = {
    'info': 'Información Financiera',
    'reclamos': 'Reclamaciones',
    'promedio':{
        'yaxis_title': 'Promedio de días mensual',
        'title': 'Promedio de días de respuesta',
        'col_name': 'kpi_dias',
        'ymax': 60,
        'ymin': 40,
        'upper_line_color': 'red',
        'lower_line_color': 'green',
        'yformat': None
    },
    'casos':{
        'yaxis_title': 'Porcentaje mensual',
        'title': 'Porcentaje de casos a tiempo',
        'col_name': 'kpi_casos',
        'ymax': 1.0,
        'ymin': 0.7,
        'lower_line_color': 'red',
        'upper_line_color': 'green',
        'yformat': ',.0%'
    }
}


def add_kpi_metrics(data):
    data['duracion'] = (data.fecha_cierre - data.fecha_inicio).dt.days
    data['sla_vencido'] = data['duracion'] > 60
    meses = data.fecha_cierre.dt.to_period('M').dt.start_time
    # return data

def add_kpi_contratos(data):
    data['sla_vencido'] = data['duracion'] > 60
    meses = data.fecha_cierre.dt.to_period('M').dt.start_time
    # return data


def kpi_calculator(df):
    agrupado = df.groupby(df.fecha_cierre.dt.to_period('M').dt.start_time)
    a_tiempo = df.groupby([df.fecha_cierre.dt.to_period('M').dt.start_time, 'sla_vencido']).size()
    a_tiempo = a_tiempo.loc[a_tiempo.index.isin([False], level=1)].reset_index(level=1, drop=True)
    df = pd.DataFrame([agrupado['duracion'].sum(), agrupado.size(), a_tiempo],
                 index=['tiempo_total', 'total_casos', 'casos_a_tiempo']).T
    df['kpi_casos'] = df.casos_a_tiempo / df.total_casos
    df['kpi_dias'] = df.tiempo_total / df.total_casos
    return df

import plotly.graph_objects as go

def avoid_annotation_overlap(fig, annotations, tolerance=10):
    """
    Adjusts the positions of Plotly annotations to avoid overlap.

    Parameters:
    - fig: Plotly Figure object
    - annotations: List of annotation dictionaries
    - tolerance: Minimum distance to consider annotations as non-overlapping (default is 10)

    Returns:
    - Updated annotations
    """

    def is_overlapping(a, b):
        print(a)
        print(b)
        """
        Check if two annotations overlap.
        """
        a_x = a['x']
        a_y = a['y']
        a_width = a_x + a['ax']

        b_x = b['x']
        b_y = b['y']
        b_width = b_x + b['ax']

        return (
            (a_x <= b_x <= a_width or b_x <= a_x <= b_width) and
            (a_y <= b_y <= a['yref'] or b_y <= a_y <= a['yref'] + a['ay'])
        )

    updated_annotations = []

    for i, annotation in enumerate(annotations):
        for j in range(i):
            if is_overlapping(annotation, annotations[j]):
                # Adjust the y-coordinate to avoid overlap
                # annotation['x'] = pd.to_datetime(annotation['x']).timestamp()
                annotation['y'] -= tolerance
                break

        updated_annotations.append(annotation)

    return updated_annotations


# annotations = [
#     dict(
#         x=1,
#         y=1,
#         xref='paper',
#         yref='paper',
#         text='Annotation 1',
#         showarrow=True,
#         arrowhead=7,
#         ax=0,
#         ay=-40
#     ),
#     dict(
#         x=1,
#         y=1,
#         xref='paper',
#         yref='paper',
#         text='Annotation 2',
#         showarrow=True,
#         arrowhead=7,
#         ax=0,
#         ay=-40
#     ),
#     # Add more annotations as needed
# ]

# annotations = avoid_annotation_overlap(fig, annotations)

# fig.update_layout(annotations=annotations)


def create_annotation(x, y, text, ypos):
    return dict(
            x=x,
            y=y,
            # xref="paper",
            # yref="paper",
            text=text,
            showarrow=True,
            font=dict(
                family="Calibri",
                size=16,
                color="#a64500"
                ),
            align="left",
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=get_sb_colors()["sb gray dark"],
            ax=-60,
            ay=ypos,
            bordercolor=get_sb_colors()["sb gray dark"],
            borderwidth=2,
            borderpad=4,
            bgcolor=get_sb_colors()["cold gray 88"],
            # opacity=0.8
            )

def grafica_kpi(data, proceso, **kwargs):
    col_name = kwargs['col_name']
    yaxis_title = kwargs['yaxis_title']
    title = kwargs['title']
    upper_line_color = kwargs['upper_line_color']
    lower_line_color = kwargs['lower_line_color']
    yformat = kwargs['yformat']
    ydata = data[col_name]
    # print(type(ydata))
    xdata = data.index
    ymin = min(ydata.min(), kwargs['ymin'])
    ymax = max(ydata.max(), kwargs['ymax'])
    promedio = ydata[-18:].mean()
    new_name = 'Indicador mensual'
    ydata = ydata.rename(new_name).to_frame()
    ydata['Tendencia'] = ydata.rolling(6,1).mean()
    # ydata[col_name].rename(yaxis_title, inplace=True)
    print(ydata.columns)
    print(ydata.head())
    fig = px.line(ydata, range_y=[ymin*0.95, ymax*1.04],
                   # width=1000, height=500,
                  color_discrete_sequence=px.colors.sequential.Agsunset_r[1::5]

    )
    fig.update_traces(hovertemplate='%{x|%b %Y}: %{y:.1f}')
    if yformat == ',.0%':
        fig.update_traces(hovertemplate='%{x|%b}: %{y:.1%}')
    fig.update_layout(
        # title=f"{proceso}<br>{title}",
        title=title,
        yaxis_title=yaxis_title,
        paper_bgcolor = get_sb_colors()['blue sb dark'],
        # paper_bgcolor = '#0CCCC6',
        # plot_bgcolor = get_sb_colors()['blue sb darker'],
        plot_bgcolor = '#111111',
        font_family='Calibri',
        font_color='#ffffff',
        # showlegend=False,
        yaxis_gridcolor = '#283442',
        xaxis_gridcolor = '#283442',
        yaxis_showgrid=True,
        xaxis_showgrid=True,
        yaxis_tickformat=yformat
    )
    fig.add_hline(promedio, line_dash='dot', line_width=1)
    # fig.add_hline(ymax, line_dash='dash', line_color=upper_line_color, line_width=1, name='Límite máximo')
    # fig.add_hline(ymin, line_dash='dash', line_color=lower_line_color, line_width=1, name='Límite mínimo')
    fig.add_trace(
        go.Scatter(
            x=[min(xdata), max(xdata)+ pd.offsets.MonthBegin(1)], y=[ymin, ymin],
            mode='lines', line_width=1, line_color=lower_line_color, line_dash='dash', name='Límite mínimo')
    )
    fig.add_trace(
        go.Scatter(
            x=[min(xdata), max(xdata)+ pd.offsets.MonthBegin(1)], y=[ymax, ymax],
            mode='lines', line_width=1, line_color=upper_line_color, line_dash='dash', name='Límite máximo')
    )


    mes_anterior = f"Mes anterior: {ydata[new_name][-2]:.1f}"
    mes_actual = f"Mes actual: {ydata[new_name][-1]:.1f}"
    mes_trasanterior = f"Penúltimo mes: {ydata[new_name][-3]:.1f}"
    mes_anterior = f"Último mes: {ydata[new_name][-2]:.1f}"
    mes_actual = f"Mes actual<br>hasta ahora: {ydata[new_name][-1]:.1f}"
    mes_trasanterior = f"{ydata.index[-3]:%b %Y}:<br>{ydata[new_name][-3]:.1f}"
    mes_anterior = f"{ydata.index[-2]:%b %Y}:<br>{ydata[new_name][-2]:.1f}"
    mes_actual = f"{ydata.index[-1]:%b %Y}:<br>{ydata[new_name][-1]:.1f}"
    if yformat == ',.0%':
        mes_trasanterior = f"{ydata.index[-3]:%b %Y}:<br>{ydata[new_name][-3]:.1%}"
        mes_anterior = f"{ydata.index[-2]:%b %Y}:<br>{ydata[new_name][-2]:.1%}"
        mes_actual = f"{ydata.index[-1]:%b %Y}:<br>{ydata[new_name][-1]:.1%}"
    annotations = [
        create_annotation(xdata[-3], ydata[new_name][-3], mes_trasanterior, 90),
        create_annotation(xdata[-2], ydata[new_name][-2], mes_anterior, 60),
        create_annotation(xdata[-1], ydata[new_name][-1], mes_actual, 30)
        # create_annotation(range(0,len(xdata))[-3], ydata[new_name][-3], mes_trasanterior, 90),
        # create_annotation(range(0,len(xdata))[-2], ydata[new_name][-2], mes_anterior, 60),
        # create_annotation(range(0,len(xdata))[-1], ydata[new_name][-1], mes_actual, 30)
        ]
    # annotations = avoid_annotation_overlap(fig, annotations)
    fig.update_layout(annotations=annotations)
    fig.update_layout(
        showlegend=True,
        legend_title='Leyenda',
        legend_orientation='h',
        legend_y=1.08,
        legend_xanchor='right',
        legend_x=1,

    )

    return fig

valid_decisions = ['Compleja', 'Concluída', 'Desestimada', 'No Objeción']
def get_contrato_kpi(data):
    # filtro_sib = data.tipo_consulta == 'SIB'
    # filtro_ra = data.tipo_consulta == 'RA'
    filtro_decisiones = data.decision.isin(valid_decisions)
    data['mes'] = data.fecha_notificacion.dt.to_period('M').values
    # data[filtro_decisiones].estatus_tarde.value_counts(normalize=True)
    grupero = data[filtro_decisiones].groupby(['mes', 'tipo_consulta'])
    total_casos = grupero.size().reset_index().pivot_table(index='mes', columns='tipo_consulta', values=0)
    total_casos.columns = ['total_ra', 'total_sib']
    kpi_tiempos = grupero.tiempo_de_respuesta.mean().reset_index().pivot_table(index='mes', columns='tipo_consulta', values='tiempo_de_respuesta')
    # kpi_casos = data[filtro_decisiones].groupby(['mes', 'estatus_tarde']).size().reset_index().pivot_table(index='mes', columns='estatus_tarde', values=0)
    # kpi_casos.columns = ['temprano', 'tarde']
    # kpi_casos['a_tiempo'] = kpi_casos.temprano / kpi_casos.sum(axis=1)
    kpi_casos = data[filtro_decisiones].groupby(['mes']).estatus_tarde.value_counts(normalize=True).reset_index().pivot_table(index='mes', columns='estatus_tarde', values='proportion')
    kpi_contratos = pd.concat([total_casos, kpi_tiempos, kpi_casos], axis=1)
    return kpi_contratos


def get_kpi_data(type, start_date=start_date):
    if type == 'reclamos':
        query = f"select * from RESULTADOS_RECLAMOS where FECHA_CIERRE > date '{start_date}'"
        cierres_claims = query_reader(query, mode='all')

        add_kpi_metrics(cierres_claims)
        kpi_data = kpi_calculator(cierres_claims)
    elif type == 'contratos':
        contratos = contratos_reading.read_matriz()
        filtro_fecha = contratos.fecha_notificacion.dt.date > start_date
        data = contratos[filtro_fecha]
        kpi_data = get_contrato_kpi(contratos[filtro_fecha])
        # contratos = pd.read_excel(path, sheet_name='Matriz Contratos', header=3)
        # contratos.columns = contratos.columns.str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    else:
        query = f"select * from RESULTADOS_INFO where FECHA_CIERRE > date '{start_date}'"
        cierres_info = query_reader(query, mode='all')
        cierres_info = cierres_info[~(cierres_info.codigo == 'CI-22-005782')]
        add_kpi_metrics(cierres_info)
        kpi_data = kpi_calculator(cierres_info)
    return kpi_data

def get_kpi_graphs(type='reclamos'):
    kpi_data = get_kpi_data(type)
    fig_promedio = grafica_kpi(kpi_data, detalles[type], **detalles['promedio'])
    fig_casos = grafica_kpi(kpi_data, detalles[type], **detalles['casos'])
    return fig_promedio, fig_casos

def get_evidencias():
    period = '2024Q4'
    columnas = ['codigo', 'fecha_inicio', 'fecha_cierre', 'duracion', 'sla_vencido']
    query = f"select * from RESULTADOS_RECLAMOS where FECHA_CIERRE > date '{start_date}'"
    cierres_claims = query_reader(query, mode='all')
    add_kpi_metrics(cierres_claims)
    filtro_mes = cierres_claims.fecha_cierre.dt.to_period('Q') == period
    evidencia_claims = cierres_claims[filtro_mes][columnas]

    query = f"select * from RESULTADOS_INFO where FECHA_CIERRE > date '{start_date}'"
    cierres_info = query_reader(query, mode='all')
    add_kpi_metrics(cierres_info)
    filtro_mes = cierres_info.fecha_cierre.dt.to_period('Q') == period
    evidencia_info = cierres_info[filtro_mes][columnas]

    query = f"select * from RESULTADOS_CONTRATOS where RESULTADOS_CONTRATOS.FECHA_NOTIFICACION > date '{start_date}'"
    cierres_contratos = query_reader(query, mode='all')
    columnas = ['codigo', 'fecha_creacion', 'fecha_notificacion', 'tipo_consulta', 'tiempo_de_respuesta', 'estatus_tarde']
    filtro_mes = cierres_contratos.fecha_notificacion.dt.to_period('Q') == period
    evidencia_contratos = cierres_contratos[filtro_mes][columnas]
    with pd.ExcelWriter(f"evidencias_kpi_{period.replace('Q', '-T')}.xlsx") as writer:
        evidencia_claims.to_excel(writer, sheet_name='Reclamaciones', index=False)
        evidencia_info.to_excel(writer, sheet_name='Información Financiera', index=False)
        evidencia_contratos.to_excel(writer, sheet_name='Contratos', index=False)



