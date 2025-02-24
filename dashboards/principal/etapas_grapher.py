"""
Creado el 23/6/2023 a las 3:11 p. m.

@author: jacevedo
"""

import locale
from datetime import datetime

import plotly.express as px

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')


etapas_map = {
    1: "recepcion",
    2: "analisis",
    3: "revision_tecnica",
    4: "revision_legal",
    5: "aprobacion",
    6: "notificacion",
}

etapas_duration_map = {
    1: 1,
    2: 32,
    3: 3,
    4: 3,
    5: 2,
    6: 2,
}


def plot_distribucion_etapas(df, color='#1F77B4', titulo=None):
    df = df[df['nombre_etapa'] != 'notificacion']
    df['proporcion_duracion'] = df['proporcion_duracion'].clip(upper=3)

    fig = px.box(
        df.sort_values('orden_etapa'),
        height=600,
        x='nombre_etapa', y='proporcion_duracion',
        # color='nombre_etapa',
        # color_discrete_sequence=px.colors.sequential.Blues[::2],
        # category_orders=etapas_map,
        custom_data=['codigo', 'duracion_etapa', 'tipo_info'],
        points='all',
        template='presentation',
        # color_discrete_map={x: y for x, y in zip(etapas_map.values(), px.colors.qualitative.T10)}
        )
    fig.update_layout(
        yaxis_tickformat='0%',
        xaxis_ticks='outside',
        xaxis_tickfont=dict(color='#F0F3F5', size=14),
        yaxis_tickfont=dict(color='#F0F3F5', size=14),
        xaxis_title=None,
        yaxis_title='Porcion consumida del plazo',
        yaxis_title_font_color='#F0F3F5',
        xaxis_autorange=True,
        xaxis_automargin=True,
        paper_bgcolor='#0D3048',
        # plot_bgcolor='#0A2336',
        # plot_bgcolor='#6f94a6',
        # font_color='#F0F3F5'

    )
    fig.update_traces(
        hovertemplate=(
            'Código: %{customdata[0]}'
            '<br>Nombre Etapa: %{x}'
            '<br>Duración Etapa: %{customdata[1]:,.1f} días'
            '<br>Informacion solicitada: %{customdata[2]}'
            '<extra></extra>'
        ),
        marker_color=color,
        # text=["Text D", "Text E", "Text F"],
        text='5',
        opacity=1,
    )
    fig.add_hline(y=1, line_dash='dash', annotation_text='Límite establecido<br> por procedimiento', annotation_font_size=14)
    fig.add_hrect(y0=0, y1=0.8, line_width=0, fillcolor='green', opacity=0.2)
    fig.add_hrect(y0=0.8, y1=1, line_width=0, fillcolor='orange', opacity=0.2)
    fig.add_hrect(y0=1, y1=3, line_width=0, fillcolor='red', opacity=0.1)
    key = 0
    for val in etapas_map.values():
        try:
            fig.add_annotation(
                text=str(df.nombre_etapa.value_counts()[val]),
                x=key, y=-0.1, showarrow=False
            )
            key+=1
        except:
            pass
    fig.add_annotation(
        text=(
            f"{len(df[df['proporcion_duracion']>=1])} tarde <br>"
            f"{len(df[df['proporcion_duracion']<1])} a tiempo"
                ),
        # align="right",
        # yref='paper',
        # xref='paper',
        font_size=14,
        x=6, y=-.22, showarrow=False
    )
    fig.add_annotation(
        # text=titulo,
        text='Distribución de tiempo transcurrido<br>'+titulo,
        font_size=14,
        font_color='#F0F3F5',
        align="left",
        yref='paper',
        xref='paper',
        x=0, y=1.1, showarrow=False
    )
    fig.add_annotation(
        # text=titulo,
        text=f'{datetime.today().strftime("%d de %b de %Y")}<br><b>{len(df):,} etapas</b>',
        font_size=14,
        font_color='#F0F3F5',
        align="right",
        yref='paper',
        xref='paper',
        x=1, y=1.1, showarrow=False
    )
    fig.add_trace(
        px.box(
        df['proporcion_duracion'],        points='all'
        )['data'][0]
    )
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')

    return fig