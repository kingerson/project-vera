"""
Creado el 31/5/2022 a las 12:01 p. m.

@author: jacevedo
"""
import locale
from datetime import timedelta

import pandas as pd
import plotly.express as px
from plotly.offline import plot

import sql_tools
from lectura_crm_odata import reclamos_reading
from prousuario_tools import get_tipos_viafirma
from dashboards.banks_rank_grapher import creates_banks_ranks

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')
#%%


def get_limit_dates(key_date = None, freq='W'):
    now = pd.Timestamp('today').to_period(freq).start_time
    if key_date:
        now = pd.Timestamp(key_date).to_period(freq).start_time
    end = now - timedelta(days = now.weekday())
    start = end_date-timedelta(days=7*8)
    return end, start

def check_sign(x):
    try:
        result = firmas.loc[firmas.asunto.str.contains(x), 'fecha_firma'].values[-1]
    except Exception as e:
        result = None
    return result


def check_response(x):
    try:
        result = firmas.loc[firmas.asunto.str.contains(x), 'tipo_respuesta'].values[-1]
    except Exception as e:
        result = None
    return result


def assign_response(asuntos, tipos):
    tipo_respuesta = pd.Series(None, index=asuntos.index, dtype=object)
    for tipo in tipos.keys():
            tipo_respuesta.loc[asuntos.str.contains(tipo)] = tipo
    favorabilidad = tipo_respuesta.map(tipos)
    return tipo_respuesta, favorabilidad


def get_firmas():
    query = "select * from FIRMAS where tipo = 'reclamos'"
    df = sql_tools.query_reader(query, mode='all')
    return df


def semanizer(series):
    result = (
        series
        .dt.to_period('W')
        .apply(lambda r: r.start_time)
    )
    return result


def get_entradas_salidas():
    result = pd.DataFrame([
        semanizer(aperturas['fecha_creacion']).value_counts(),
        semanizer(cierres['fecha_cierre']).value_counts()
    ], index=['Entradas', 'Salidas']).T
    return result


def get_period_data(df):
    inicio = df.fecha_cierre >= start_date
    final = df.fecha_cierre < end_date
    result = df[inicio & final]
    return result


def get_pendientes():
    semanas = set(semanizer(matriz['fecha_creacion']))
    pendientes = {}
    retrasadas = {}
    for n in semanas:
        filtro_descartada = matriz.status_cierre != 'Descartada'
        sin_descartes = matriz[filtro_descartada]
        filtro_na = sin_descartes.fecha_cierre.isna()
        filtro_month = sin_descartes.fecha_cierre >= n
        sin_cierre = sin_descartes[(filtro_na | filtro_month)]
        filtro_entrada = sin_cierre.fecha_creacion < n
        entro_antes = sin_cierre[filtro_entrada]
        mas60 = (n - entro_antes.fecha_inicio).dt.days > 60
        pending = entro_antes.shape[0]
        late = entro_antes[mas60].shape[0]
        pendientes[n.date()] = pending
        retrasadas[n.date()] = late
    pendings = pd.DataFrame([pendientes, retrasadas], index=['pendientes', 'retrasadas']).T.sort_index()
    pendings['a_tiempo'] = pendings.pendientes - pendings.retrasadas
    pendings['a_tiempo%'] = pendings.a_tiempo/pendings.pendientes
    pendings['retrasadas%'] = pendings.retrasadas/pendings.pendientes
    filtro_inicio = pendings.index >= start_date.date()
    filtro_final = pendings.index < end_date.date()
    sla = pendings[filtro_inicio & filtro_final]
    return sla

def graphs_entradas_salidas(data):
    fig = px.bar(data, barmode='group', template='presentation', text_auto=True,
                 width=1100, height=600, opacity=0.8)
    fig.update_layout(
        yaxis_showgrid=False
        , showlegend=False
        , bargap=0.35
        , xaxis_tickvals=list(data.index)
        , xaxis_ticktext=[f.strftime('%d %b') for f in data.index]
        , uniformtext_minsize=20, uniformtext_mode='show'
    )

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
    plot(fig)


def graphs_sla():
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
        )
        , uniformtext_minsize=12, uniformtext_mode='show',
        bargap=0.5
        # ,textfont_align='left'

    )
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
    plot(fig)


def get_favorabilidad():
    grupero = pd.Grouper(key='fecha_cierre', freq='W')
    result = (
        cierres
        .groupby([grupero, 'favorabilidad'])
        .size()
        .rename('cantidad')
        .sort_index()
        .reset_index()
        .pivot(index='fecha_cierre', columns='favorabilidad', values='cantidad')
        .fillna(0)
        .astype(int)
    )

    result['con_decision'] = result.Desfavorable + result.Favorable
    result['%_desfavorable'] = result.Desfavorable / result['con_decision']
    result['%_favorable'] = result.Favorable / result['con_decision']
    result.index = result.index - timedelta(6)
    return result


def graphs_favorabilidad():
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
        )
        , uniformtext_minsize=20, uniformtext_mode='show',
        bargap=0.5
    )

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

    plot(fig)


def get_montos():
    no_acreditacion = (cierres.monto_total == 0) & (cierres.monto_total.isna())
    grouper = pd.Grouper(key='fecha_cierre', freq='W')
    favorable = cierres.favorabilidad == "Favorable"
    reconsideracion = cierres.reconsideracion == False
    result = (
        cierres[favorable & reconsideracion & ~no_acreditacion]
        .groupby(grouper)
        .sum()['monto_total']
        .sort_index()
    )
    result.index = result.index - timedelta(6)
    return result


def graphs_montos():
    max_y = montos.max()
    fig = px.bar(montos,
                 text_auto=True, color_discrete_sequence=['#0d3048'],
                 opacity=0.8, template='presentation', width=1100, height=600,
                 range_y=[0, max_y * 1.2]
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
        )
        , uniformtext_minsize=20, uniformtext_mode='show',
        bargap=0.5
    )

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

    plot(fig)


def plots_weekly_ranks():
    grupero_semanal = pd.Grouper(key='fecha_creacion', freq='W')
    eif_per_week = aperturas.groupby([grupero_semanal, 'eif']).size()
    entries_per_bank = creates_banks_ranks(eif_per_week)
    cat_per_week = aperturas.groupby([grupero_semanal, 'categoria']).size()
    entries_per_cat = creates_banks_ranks(cat_per_week, color_col='categoria')
    entries_per_bank.update_layout(
        xaxis_tickmode='array',
        xaxis_tickvals=list(set(eif_per_week.index.get_level_values(0))),
        xaxis_ticktext=[(f - timedelta(days=6)).strftime('%d %b') for f in set(eif_per_week.index.get_level_values(0))]
    )
    plot(entries_per_bank)
    entries_per_cat.update_layout(
        xaxis_tickmode='array',
        xaxis_tickvals=list(set(eif_per_week.index.get_level_values(0))),
        xaxis_ticktext=[(f - timedelta(days=6)).strftime('%d %b') for f in set(eif_per_week.index.get_level_values(0))]
    )
    plot(entries_per_cat)


def merges_matriz_viafirma():
    tipos_viafirma = get_tipos_viafirma()
    firmas['tipo_respuesta'], firmas['favorabilidad'] = assign_response(firmas.asunto, tipos_viafirma['reclamos'])
    fin_firma = matriz.fecha_cierre.isna()
    matriz['fecha_viafirma'] = matriz['codigo'].apply(lambda x: check_sign(x[-6:]))
    matriz['respuesta_viafirma'] = matriz['codigo'].apply(lambda x: check_response(x[-6:]))
    matriz['favorabilidad_viafirma'] = matriz['respuesta_viafirma'].map(tipos_viafirma['reclamos'])
    return matriz
#%%

# claims2 = reclamos_reading.main('2020-08-16')
#%%

# matriz = pd.read_excel(r"C:\Users\jacevedo\Documents\ProUsuario Project\new_salidas\reclamaciones_2022_04 - Copy.xlsx", sheet_name='CRM')
#%%
filepath = r"C:\Users\jacevedo\Documents\ProUsuario Project\viafirma\matriz_31_05.xlsx"
matriz = pd.read_excel(filepath)

#%%


#%%

firmas = get_firmas()
end_date, start_date = get_limit_dates()
claims = reclamos_reading.main(start_date.date())
matriz = merges_matriz_viafirma()
cierres = get_period_data(matriz)
aperturas = get_period_data(claims)
entradas_salidas = get_entradas_salidas()
graphs_entradas_salidas(entradas_salidas)
sla = get_pendientes()
graphs_sla()
favorabilidad = get_favorabilidad()
graphs_favorabilidad()
montos = get_montos()
graphs_montos()
plots_weekly_ranks()
