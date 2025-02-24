"""
Creado el 12/7/2022 a las 8:43 a. m.

@author: jacevedo
"""




def graphs_entradas_salidas(data, freq='W'):
    fig = px.bar(data, barmode='group', template='presentation', text_auto=True,
                 width=1100, height=600, opacity=0.8)
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
        data.Entradas.mean(),
        line_dash='dash',
        line_color=px.colors.qualitative.T10[1],
        line_width=3
    )
    fig.add_hline(
        data.Salidas.mean(),
        line_dash='dash',
        line_color=px.colors.qualitative.T10[0],
        line_width=3
    )

    fig.update_traces(
        textposition='outside',
        textfont_family='Calibri',
        # textfont_size = 20

    )
    # plot(fig, filename=f'flujo_{freq}.html')
    return fig

def graphs_sla(sla, freq='W'):
    fig = px.bar(sla, y=['retrasadas', 'a_tiempo'], text_auto=True, color_discrete_sequence=['#E45756',
                                                                                             '#54A24B'], opacity=0.8,
                 template='presentation', width=1000, height=600,
                 custom_data=['pendientes', 'a_tiempo%', 'retrasadas%'], range_y=[0, sla.pendientes.max() * 1.3])
    fig.update_layout(
        yaxis_showgrid=False,
        xaxis_tickvals=list(sla.index),
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

    )
    return fig
    # plot(fig, filename=f'sla_{freq}.html')

def graphs_favorabilidad(favorabilidad, freq='W'):
    max_y = favorabilidad.con_decision.max()
    fig = px.bar(favorabilidad, y=['Favorable', 'Desfavorable'],
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
        if trace.name == "Desfavorable"
        else trace.update(texttemplate='%{customdata[0]:.0%}')
    )

    plot(fig, filename=f'favorabilidad_{freq}.html')


def graphs_montos(montos, freq='W'):
    max_y = montos.max()
    fig = px.bar(montos,
                 text_auto=True, color_discrete_sequence=['#0d3048'],
                 opacity=0.8, template='presentation', width=1100, height=600,
                 range_y=[0, max_y * 1.2]
                 )

    fig.update_layout(
        yaxis_showgrid=False,
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


def plots_weekly_ranks(aperturas, freq='W'):
    grupero_semanal = pd.Grouper(key='fecha_creacion', freq=freq)
    eif_per_week = aperturas.groupby([grupero_semanal, 'eif']).size()
    entries_per_bank = creates_banks_ranks(eif_per_week)
    entries_per_bank.update_layout(
        xaxis_tickmode='array',
        xaxis_tickvals=list(set(eif_per_week.index.get_level_values(0))),
        xaxis_ticktext=[(f - timedelta(days=6)).strftime('%d %b') for f in set(eif_per_week.index.get_level_values(0))]
    )
    if freq == 'M':
        entries_per_bank.update_layout(
            xaxis_tickmode='array',
            xaxis_tickvals=list(set(eif_per_week.index.get_level_values(0))),
            xaxis_ticktext=[f.strftime("%b '%y") for f in
                            set(eif_per_week.index.get_level_values(0))]
        )
    plot(entries_per_bank, filename=f'entires_per_bank_{freq}.html')
    sleep(0.5)
    cat_per_week = aperturas.groupby([grupero_semanal, 'categoria']).size()
    entries_per_cat = creates_banks_ranks(cat_per_week, color_col='categoria')
    entries_per_cat.update_layout(
        xaxis_tickmode='array',
        xaxis_tickvals=list(set(eif_per_week.index.get_level_values(0))),
        xaxis_ticktext=[(f - timedelta(days=6)).strftime('%d %b') for f in set(eif_per_week.index.get_level_values(0))]
    )
    if freq == 'M':
        entries_per_cat.update_layout(
            xaxis_tickmode='array',
            xaxis_tickvals=list(set(eif_per_week.index.get_level_values(0))),
            xaxis_ticktext=[f.strftime('%b %y') for f in
                            set(eif_per_week.index.get_level_values(0))]
        )
    plot(entries_per_cat, filename=f'entries_per_cat_{freq}.html')
