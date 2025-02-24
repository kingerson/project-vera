"""
Creado el 12/7/2022 a las 8:45 a. m.

@author: jacevedo
"""
from datetime import timedelta
from time import sleep

import pandas as pd
from plotly import express as px
from plotly.offline import plot

from dashboards.principal.banks_rank_grapher import creates_banks_ranks


def entradas_salidas_bars(data, freq='W'):
    fig = px.bar(data, barmode='group', template='presentation', text_auto=True,
                 width=1050, height=600, opacity=0.8)
    fig.update_layout(
        yaxis_showgrid=False,
        showlegend=False,
        bargap=0.35,
        xaxis_tickvals=list(data.index),
        xaxis_ticktext=[f.strftime('%d %b') for f in data.index],
        uniformtext_minsize=20, uniformtext_mode='show'
    )
    if freq == 'M':
        fig.update_layout(xaxis_ticktext=[f.strftime("%b '%y") for f in data.index])

    fig.add_hline(
        data.entradas.mean(),
        line_dash='dash',
        line_color=px.colors.qualitative.T10[0],
        line_width=3
    )
    fig.add_hline(
        data.salidas.mean(),
        line_dash='dash',
        line_color=px.colors.qualitative.T10[1],
        line_width=3
    )

    fig.update_traces(
        textposition='outside',
        textfont_family='Calibri',
        # textfont_size = 20

    )
    # plot(fig, filename=f'flujo_{freq}.html')
    return fig


def sla_bars(sla, freq='W'):
    fig = px.bar(sla, y=['retrasadas', 'a_tiempo'], text_auto=True, color_discrete_sequence=['#E45756',
                                                                                             '#54A24B'], opacity=0.8,
                 template='presentation', width=1000, height=600,
                 custom_data=['pendientes', 'a_tiempo%', 'retrasadas%'], range_y=[0, sla.pendientes.max() * 1.3])
    fig.update_layout(
        yaxis_showgrid=False,
        xaxis_tickvals=list(sla.index),
        yaxis_tickformat=",.0f",
        xaxis_ticktext=[f.strftime('%d %b') for f in sla.index],
        showlegend=False,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.99,
            title="Leyenda",
        ),
        uniformtext_minsize=12, uniformtext_mode='show',
        bargap=0.5
        # ,textfont_align='left'
    )
    if freq == 'M':
        fig.update_layout(xaxis_ticktext=[f.strftime("%b '%y") for f in sla.index])
        fig.update_layout(yaxis_tickformat=",.0f")
    fig.update_traces(
        texttemplate=(
            'P: <b>%{customdata[0]:.}</b>'
            '<br>✅: %{customdata[1]:.0%}'
            '<br>❌: %{customdata[2]:.0%}'
            '<br> '

        ),
        textposition='outside',
        textfont_size=13
    )
    fig.for_each_trace(
        lambda trace: trace.update(texttemplate=None) if trace.name == "retrasadas" else ()
    )
    fig.add_hline(
        sla.pendientes.mean(),
        line_dash='dash',
        line_color="#3366cc",
        line_width=3,
        opacity=0.5

    )
    return fig
    # plot(fig, filename=f'sla_{freq}.html')


def favorabilidad_bars(favorabilidad, freq='W'):
    max_y = favorabilidad.con_decision.max()
    fig = px.bar(favorabilidad, y=['F', 'D'],
                 text_auto=True, color_discrete_sequence=px.colors.qualitative.D3[2:4],
                 opacity=0.8, template='presentation', width=1100, height=600,
                 custom_data=['%_favorable', '%_desfavorable', 'con_decision'], range_y=[0, max_y * 1.2]
                 )

    fig.update_layout(
        yaxis_showgrid=False,
        xaxis_tickvals=list(favorabilidad.index),
        xaxis_ticktext=[f.strftime('%d %b') for f in favorabilidad.index],
        showlegend=False,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.99,
            title="Leyenda",
        ),
        uniformtext_minsize=20, uniformtext_mode='show',
        bargap=0.5
    )
    if freq == 'M':
        fig.update_layout(xaxis_ticktext=[f.strftime("%b '%y") for f in favorabilidad.index])

    fig.update_traces(
        textposition='outside',
        textfont_size=16
    )

    fig.for_each_trace(
        lambda trace:
        trace.update(texttemplate=(
            '<b>%{customdata[2]}</b>'
            '<br> '
            '%{customdata[1]:.0%}'
        )
        )
        if trace.name == "D"
        else trace.update(texttemplate='%{customdata[0]:.0%}')
    )

    # plot(fig, filename=f'favorabilidad_{freq}.html')
    return fig


def montos_bars(montos, freq='W'):
    max_y = montos.max()
    fig = px.bar(montos,
                 text_auto=True, color_discrete_sequence=['#0d3048'],
                 opacity=0.8, template='presentation', width=1100, height=600,
                 range_y=[0, max_y * 1.2]
                 )

    fig.update_layout(
        yaxis_showgrid=False,
        yaxis_title="Monto en DOP",
        xaxis_tickvals=list(montos.index),
        xaxis_ticktext=[f.strftime('%d %b') for f in montos.index],
        showlegend=False,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.99,
            title="Leyenda",
        ),
        uniformtext_minsize=20, uniformtext_mode='show',
        bargap=0.5
    )
    if freq == 'M':
        fig.update_layout(xaxis_ticktext=[f.strftime("%b '%y") for f in montos.index])

    fig.update_traces(
        texttemplate=(
            '$%{y:,.2s}'
        ),
        textposition='outside',
        textfont_size=16
    )

    fig.add_hline(
        montos.mean(),
        line_dash='dash',
        line_color='#f77245',
        line_width=3,
    )

    plot(fig, filename=f'montos_{freq}.html')


def creates_fig(aperturas, freq, group_col):
    grupero_semanal = pd.Grouper(key='fecha_creacion', freq=freq)
    data_per_period = aperturas.groupby([grupero_semanal, group_col]).size()
    color_col = group_col
    entries_per_group = creates_banks_ranks(data_per_period, color_col=color_col)
    entries_per_group.update_layout(
        xaxis_tickmode='array',
        xaxis_tickvals=list(set(data_per_period.index.get_level_values(0))),
        xaxis_ticktext=[(f - timedelta(days=6)).strftime('%d %b') for f in set(data_per_period.index.get_level_values(0))]
    )
    if freq == 'M':
        entries_per_group.update_layout(
            xaxis_tickmode='array',
            xaxis_tickvals=list(set(data_per_period.index.get_level_values(0))),
            xaxis_ticktext=[f.strftime("%b '%y") for f in
                            set(data_per_period.index.get_level_values(0))]
        )
    return entries_per_group


def make_light(fig):
    fig.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font_color='#000000'
    )
    return fig

def plots_weekly_ranks(aperturas, freq='W'):
    entries_per_bank = creates_fig(aperturas, freq, 'eif')
    entries_per_cat = creates_fig(aperturas, freq, 'categoria')
    entries_per_channel = creates_fig(aperturas, freq, 'canal')
    entries_per_bank = make_light(entries_per_bank)
    entries_per_cat = make_light(entries_per_cat)
    plot(entries_per_bank, filename=f'entires_per_bank_{freq}.html')
    sleep(0.5)
    plot(entries_per_cat, filename=f'entires_per_cat_{freq}.html')
    # sleep(0.5)
    # plot(entries_per_channel, filename=f'entries_per_channel_{freq}.html')




