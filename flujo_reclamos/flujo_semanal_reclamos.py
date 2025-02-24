"""
Creado el 31/5/2022 a las 12:01 p. m.

@author: jacevedo
"""
import locale
from datetime import date, timedelta
from time import sleep
import pandas as pd
import plotly.express as px
from plotly.offline import plot
import plotly.subplots as sp
import plotly.graph_objects as go
from prousuario_tools import get_sb_colors

import sql_tools
import reclamos_reading
from frequent_graphers import entradas_salidas_bars, sla_bars, favorabilidad_bars, montos_bars, plots_weekly_ranks

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')
#%%

FREQ = 'W'
colores = get_sb_colors()

def get_limit_dates(key_date=None, freq='W'):
    # noinspection PyTypeChecker
    end = pd.Timestamp('today').to_period(freq).start_time
    if key_date:
        end = pd.Timestamp(key_date).to_period(freq).start_time
    start = end - timedelta(weeks=8)
    if freq == 'M':
        start = end-pd.offsets.MonthBegin()*6
    elif freq == 'D':
        start = end-pd.offsets.Day()*30
    return end, start


def get_firmas():
    query = "select * from RESULTADOS_RECLAMOS"
    df = sql_tools.query_reader(query, mode='all')
    return df


def semanizer(series):
    result = (
        series
        .dt.to_period('W')
        .apply(lambda r: r.start_time)
    )
    return result


def get_entradas_salidas(aperturas, cierres, freq='W'):
    result = pd.DataFrame([
        aperturas['fecha_creacion'].dt.to_period(freq).apply(lambda x: x.start_time).value_counts(),
        cierres['fecha_cierre'].dt.to_period(freq).apply(lambda x: x.start_time).value_counts()
    ], index=['entradas', 'salidas']).T
    return result


def get_period_data(df, date_col, start_date, end_date):
    inicio = df[date_col] >= start_date
    final = df[date_col] < end_date
    result = df[inicio & final]
    return result


def get_pendientes(claims, start_date='2022-01-01', end_date=None , freq='W'):
    pendientes = claims[claims.fecha_creacion < end_date].copy()
    results = get_results('2022-01-01', end_date, con_descartes=True)
    matriz = pd.merge(pendientes, results, on='codigo', how='left')
    periods = list(set(matriz['fecha_creacion'].dt.to_period(freq).dt.end_time+timedelta(1)))
    periods.sort()
    pendientes = {}
    retrasadas = {}
    # sin_cierre = matriz.fecha_cierre.isna()
    # post_firma = matriz.etapa.isin(['Notificación y Entrega', 'EIF Notificada', 'Entregado al Usuario', 'Cumplimiento'])
    desestimado = matriz.respuesta_crm.isin(['Desestimado por el usuario', 'Sin Respuesta'])
    # matriz = matriz[~desestimado & sin_cierre & ~post_firma].copy()
    # matriz = matriz[~desestimado & ~post_firma].copy()
    matriz = matriz[~desestimado].copy()
    for n in periods:
        filtro_descartada = matriz['status_cierre'] != 'D'
        sin_inactiva = matriz.activa_x
        sin_descartes = matriz[filtro_descartada & sin_inactiva]
        filtro_na = sin_descartes['fecha_cierre'].isna()
        filtro_despues = sin_descartes['fecha_cierre'] >= n
        sin_cierre = sin_descartes[(filtro_na | filtro_despues)]
        filtro_entrada = sin_cierre['fecha_verificacion'] < n
        entro_antes = sin_cierre[filtro_entrada]
        mas60 = (n - entro_antes['fecha_verificacion']).dt.days > 60
        pending = entro_antes.shape[0]
        late = entro_antes[mas60].shape[0]
        pendientes[n.date()-timedelta(7)] = pending
        retrasadas[n.date()-timedelta(7)] = late
    pendings = pd.DataFrame([pendientes, retrasadas], index=['pendientes', 'retrasadas']).T.sort_index()
    pendings['a_tiempo'] = pendings['pendientes'] - pendings['retrasadas']
    pendings['a_tiempo%'] = pendings['a_tiempo']/pendings['pendientes']
    pendings['retrasadas%'] = pendings['retrasadas']/pendings['pendientes']
    return pendings.iloc[-8:]
    # return entro_antes[mas60]

def get_favorabilidad(cierres, freq='W'):
    grupero = pd.Grouper(key='fecha_cierre', freq=freq)
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

    result['con_decision'] = result['D'] + result['F']
    result['%_desfavorable'] = result['D'] / result['con_decision']
    result['%_favorable'] = result['F'] / result['con_decision']
    result.index = result.index - timedelta(6)
    return result


def get_montos(cierres, freq='W'):
    cierres['monto'] = cierres.monto_instruido_dop.fillna(0) + cierres.monto_instruido_usd.fillna(0) * 56
    grouper = pd.Grouper(key='fecha_cierre', freq=freq)
    favorable = cierres.favorabilidad == "F"
    carta = cierres.tipo_respuesta == "Carta Informativa"
    reconsideracion = cierres.reconsideracion.astype(bool)
    result = (
        cierres[favorable & ~reconsideracion & ~carta]
        .groupby(grouper)['monto']
        .sum()
        .sort_index()
    )
    result.index = result.index - timedelta(6)
    return result


def get_results(start_date, end_date, con_descartes=False):
    query = ("select * from RESULTADOS_RECLAMOS"
             f" where"
             f" (FECHA_CIERRE >= to_DATE('{start_date}', 'yyyy-mm-dd')"
             f" and FECHA_CIERRE < to_DATE('{end_date}', 'yyyy-mm-dd'))"
             )
    if con_descartes:
        query = query + " or STATUS_CIERRE = 'D'"
    result = sql_tools.query_reader(query, mode='all')
    return result


#%%

def generate_favor_tipo_data(mezcla, group_col='tipo_reclamo'):
    tipo_favor = mezcla[mezcla.favorabilidad.isin(['F', 'D'])].groupby([group_col, 'favorabilidad']).size().reset_index().pivot_table(index=group_col, columns='favorabilidad', values=0).fillna(0).astype(int)
    tipo_favor['total'] = tipo_favor.sum(axis=1)
    tipo_favor.sort_values(by='total', ascending=False, inplace=True)
    top = tipo_favor.nlargest(15, 'total')
    top.loc['OTROS'] = tipo_favor.iloc[16:-1].sum()
    top['F_pct'] = top.F / top.total
    top['D_pct'] = top.D / top.total
    top['diferencia'] =  top.F_pct - top.D_pct
    top.sort_values('diferencia', inplace=True)
    return top

#%%
def create_tipo_favor_graph(top):
    fig = px.bar(top,
                 x=['F_pct', 'D_pct'], barmode='relative', text_auto=True,
                 template='presentation',
                 color_discrete_map=dict(F='rgb(26,152,80)', D='rgb(215,48,39)'),
                 opacity=0.8,
                 orientation='h', range_x=[-0.02,1],
                 # width=1600, height=800,

                 )
    fig.update_traces(texttemplate='<b>%{x:.0%}</b>')
    # fig.update_traces(texttemplate='%{x:.0%}')
    fig.update_layout(font_family='Arial', yaxis_automargin=True, showlegend=True,
                      xaxis_showgrid=False, yaxis_zeroline=False, xaxis_zeroline=False,
                      xaxis_visible=False, yaxis_title=None, yaxis_tickfont_size=15, legend_orientation='h',
                      legend_title=None, legend_y=-0.03)
    annotations = []
    for idx, val in enumerate(top.total.astype(int)):
        annotations.append(
            dict(yref='y', x=1.15, y=idx, xref='paper',
            text=f'{val:,.0f} - <b>{val/top.total.sum():,.0%}', textangle=0, align='left',
            font=dict(
                family='Calibri',
                size=15
            ),
            showarrow=False)
        )
    annotations.append(
            dict(yref='y', x=1.15, y=len(top)+0.2, xref='paper',
            text=f'<b>Cantidad<br>de casos</b>', textangle=0, align='left',
            font=dict(
                family='Calibri',
                size=15
            ),
            showarrow=False
                 ))
    fig.update_layout(annotations=annotations)
    labels = {"F_pct": "Favorable", "D_pct": "Desfavorable"}


    for idx, val in enumerate(labels.items()):
        print(idx, val)
        if fig.data[idx]['name'] == val[0]:
            fig.data[idx]['name'] = val[1]

    plot(fig)
#%%


def main():
    claims = reclamos_reading.main('2022-01-01', added_columns={'new_etapaactiva': {'etapa':str}})
    freq = 'W'
    end_date = date.today()
    end_date = pd.to_datetime(end_date).to_period('W').start_time.date()
    # end_date = pd.to_datetime(end_date).to_period('W').end_time.date()
    start_date = end_date - timedelta(weeks=8)
    end_date = end_date - timedelta(1)
    # end_date = end_date + timedelta(1)
    end_date = end_date.strftime('%Y-%m-%d')
    start_date = start_date.strftime('%Y-%m-%d')
    # start_date ='2023-12-25'
    # end_date = '2024-02-18'
    entradas = reclamos_reading.main(start_date, end_date, added_columns={'new_etapaactiva': {'etapa':str}})
    salidas = get_results(start_date, end_date)
    entradas_salidas = get_entradas_salidas(entradas, salidas, freq=freq)
    fig = entradas_salidas_bars(entradas_salidas, freq=freq)
    plot(fig)
    sleep(0.10)
    # end_date = '2024-04-02'
    sla = get_pendientes(claims, end_date=end_date, freq=freq)
    fig = sla_bars(sla, freq=freq)
    plot(fig)
    sleep(0.10)
    favorabilidad = get_favorabilidad(salidas, freq=freq)
    fig = favorabilidad_bars(favorabilidad, freq=freq)
    plot(fig)
    sleep(0.10)
    print('inicia montos')
    montos = get_montos(salidas, freq=freq)
    # montos = get_montos(roselis, freq=freq)
    montos_bars(montos, freq=freq)
    print('termina montos')
    sleep(0.5)
    plots_weekly_ranks(entradas, freq=freq)
    # M3tricas de las notas de cada slide
    entradas_salidas.mean()
    sla.mean()
    print(favorabilidad.sum()['O'])
    print(favorabilidad.sum()['F'] / favorabilidad.sum()['con_decision'])
    montos.mean()
#%%
    filtro_mes = entradas.fecha_creacion.dt.to_period('M') == '2023-09'
    entradas[filtro_mes].reconsideracion.value_counts()
    filtro_mes = salidas.fecha_cierre.dt.to_period('M') == '2023-09'
    print(salidas[filtro_mes].shape[0])
    favorable = salidas.favorabilidad == 'F'
    decision = salidas.favorabilidad.isin(('F', 'D'))
    print(salidas[filtro_mes & favorable].shape[0] / salidas[filtro_mes & decision].shape[0])



    #%%
    #Metricas de sexo
    print('-' * 30)
    print('Metricas de sexo')
    print(f'Entradas de personas: {entradas.genero.value_counts().sum()}')
    print(f"Hombres: {entradas.genero.value_counts(normalize=True)['Masculino']:.0%}")
    print(f"Mujeres: {entradas.genero.value_counts(normalize=True)['Femenino']:.0%}")
    print('-'*30)
    entradas_totales = entradas.genero.value_counts().sum()
    entradas_genero = entradas.genero.value_counts(normalize=True)
    mezcla = pd.merge(salidas, claims, on='codigo', how='left')
    filtro_decisiones = mezcla.favorabilidad.isin(['F', 'D'])
    filtro_masculino = mezcla.genero == 'Masculino'
    filtro_femenino = mezcla.genero == 'Femenino'
    print('-'*30)
    print(f"Favorabilidad general: {mezcla[filtro_decisiones].favorabilidad.value_counts(normalize=True)['F']:.0%}")
    print(f"Favorabilidad Hombres: {mezcla[filtro_decisiones & filtro_masculino].favorabilidad.value_counts(normalize=True)['F']:.0%}")
    print(f"Favorabilidad Mujeres: {mezcla[filtro_decisiones & filtro_femenino].favorabilidad.value_counts(normalize=True)['F']:.0%}")
    print('-'*30)
    favor_genero = [
        mezcla[filtro_decisiones & filtro_masculino].favorabilidad.value_counts(normalize=True)['F'],
        mezcla[filtro_decisiones & filtro_femenino].favorabilidad.value_counts(normalize=True)['F']
        ]

    filtro_favorable = mezcla.favorabilidad == 'F'
    filtro_reconsidera = mezcla.reconsideracion_y
    mezcla['monto'] = mezcla.monto_instruido_dop.fillna(0) + mezcla.monto_instruido_usd.fillna(0) + 56
    monto_m = mezcla[filtro_masculino & filtro_favorable & ~filtro_reconsidera].monto.sum()
    monto_f = mezcla[filtro_femenino & filtro_favorable & ~filtro_reconsidera].monto.sum()
    print(f"Monto total general: DOP {mezcla[filtro_favorable & ~filtro_reconsidera].monto.sum()/1000000:,.2f} M")
    print(f"Monto total hombres: DOP {monto_m/1000000:,.2f} M")
    print(f"Monto total mujeres: DOP {monto_f/1000000:,.2f} M")
    print('-' * 30)
    montos_genero = [
        mezcla[filtro_masculino & filtro_favorable & ~filtro_reconsidera].monto.sum(),
        mezcla[filtro_femenino & filtro_favorable & ~filtro_reconsidera].monto.sum()
    ]

    print(f"Monto promedio hombres: DOP {monto_m/(monto_m+monto_f)}")
    print(f"Monto promedio hombres{monto_f/(monto_m+monto_f)}")

    print(mezcla[filtro_masculino & filtro_favorable & ~filtro_reconsidera].monto.mean())
    print(mezcla[filtro_femenino & filtro_favorable & ~filtro_reconsidera].monto.mean())
    print(mezcla[filtro_favorable & ~filtro_reconsidera].monto.mean())
    print(mezcla[filtro_masculino & filtro_favorable & ~filtro_reconsidera].monto.mean()/mezcla[filtro_favorable & ~filtro_reconsidera].monto.mean() - 1)
    print(mezcla[filtro_femenino & filtro_favorable & ~filtro_reconsidera].monto.mean()/mezcla[filtro_favorable & ~filtro_reconsidera].monto.mean() - 1)
    print(monto_m)
    print(monto_f)
    print(monto_m / (monto_m + monto_f))
    print(monto_f / (monto_m + monto_f))

    montos_promedio = [
        mezcla[filtro_masculino & filtro_favorable & ~filtro_reconsidera].monto.mean(),
        mezcla[filtro_femenino & filtro_favorable & ~filtro_reconsidera].monto.mean()
    ]
#%%
fav_general = mezcla[filtro_decisiones].favorabilidad.value_counts(normalize=True)['F']
monto_general = mezcla[filtro_favorable & ~filtro_reconsidera].monto.sum()
monto_general_promedio = mezcla[filtro_favorable & ~filtro_reconsidera].monto.mean()
    # Create subplots with 1 row and 2 columns
    def agrega_trace(fig, data, total, col, title, formato='porciento'):
        formatos = {
            'porciento': '<b>%{y:.0%}<b>',
            'dinero': '<b>$%{y:.3s}<b>'
        }
        total_titles = {
            1:f'Total de casos<br>recibidos<br><b>{total}',
            2:f'Favorabilidad<br>general<br><b>{total:.0%}',
            3:f'Monto total<br>dispuesto a acreditar<br><b>${total/1000000:,.1f} M',
            4:f'Monto promedio general<br>dispuesto a acreditar<br><b>${total:,.2f}'
        }
        labels = ['H', 'M']
        text=data
        print(title)
        if title == 'Monto total<br> a acreditar':
            text=[data, data/total]
        fig.add_trace(go.Bar(x=labels, y=data, text=text,
                             texttemplate=formatos[formato]), row=1, col=col)
        fig['layout'][f'yaxis{col}']['range'] = [0,max(data)*1.1]
        fig['layout'][f'yaxis{col}']['range'] = [0,max(data)*1.1]
        fig.add_annotation(dict(
            yref='paper', x=0.5, y=-0.4, xref=f'x{col}',
            text=f"{total_titles[col]}", textangle=0, align='center',
            font=dict(
                family='Calibri',
                size=25
            ),
            showarrow=False
                 ))
    titles=[
        'Reclamaciones<br>Recibidas',
        'Favorabilidad',
        'Monto total<br> a acreditar',
        'Monto promedio<br> a acreditar'
    ]
    fig = sp.make_subplots(rows=1, cols=4, subplot_titles=titles)
    agrega_trace(fig, entradas_genero.values, int(entradas_totales), 1, titles[0] , 'porciento')

    agrega_trace(fig, favor_genero, fav_general, 2, titles[1],  'porciento')
    agrega_trace(fig, montos_genero, monto_general,3, titles[2], 'dinero')
    agrega_trace(fig, montos_promedio, monto_general_promedio, 4, titles[3], 'dinero')
    fig.update_layout(
        showlegend=False, template='presentation', font_family='Arial', font_size=25,
        width=1400, height=600, uniformtext_minsize=25, uniformtext_mode='show',
        # margin={'autoexpand': True}
        # margin={'g': 10, 't': 10}
        margin={'b': 150}

    )
    fig.update_annotations(selector={"y":1.0}, font_size=25, y=1.1)
    fig.update_yaxes(visible=False, automargin=True)
    fig.update_traces(width=0.5,
                      marker_color=[colores['blue sb dark'], colores['sb gray light']],
                      marker_cornerradius=5, textposition='outside')
    plot(fig)
#%%
from sql_tools import query_reader
query = ("SELECT * FROM RESULTADOS_RECLAMOS WHERE FECHA_CIERRE > DATE '2023-09-01'")
results = query_reader(query, mode='all')
mezcla = pd.merge(results, claims[['codigo', 'tipo_reclamo', 'eif']], on='codigo', how='right')
data = generate_favor_tipo_data(mezcla)
data.index = [val if len(val) < 45 else val[:45]+'...' for val in data.index ]

create_tipo_favor_graph(data)

#%%

error_trans = mezcla[mezcla.tipo_reclamo == 'TRANSFERENCIA ERRONEA '].copy()
data = generate_favor_tipo_data(error_trans, group_col='eif')
data.index = [val if len(val) < 45 else val[:45]+'...' for val in data.index ]

create_tipo_favor_graph(data.drop('OTROS'))

#%%

error_trans = mezcla[mezcla.tipo_reclamo == 'DEPOSITO MAL APLICADO'].copy()
data = generate_favor_tipo_data(error_trans, group_col='eif')
data.index = [val if len(val) < 45 else val[:45]+'...' for val in data.index ]

create_tipo_favor_graph(data.drop('OTROS'))
#%%
#
mezcla = pd.merge(salidas, claims, on='codigo', how='left')
por_tipo = mezcla.groupby(['tipo_reclamo', 'favorabilidad']).size().reset_index().pivot_table(index='tipo_reclamo', columns='favorabilidad', values=0)
por_tipo['decisiones'] = por_tipo['F']+ por_tipo['D']
por_tipo['favorabilidad'] = (por_tipo['F'] / por_tipo['decisiones']).fillna(0)
# por_tipo.to_excel('t42023_por_tipo.xlsx')
data = generate_favor_tipo_data(mezcla)

# mezcla[mezcla.tipo_reclamo == 'TRANSFERENCIA ERRONEA '].eif.value_counts(normalize=True)

create_tipo_favor_graph(data)

mezcla[mezcla.tipo_reclamo == 'DEPOSITO MAL APLICADO'].eif.value_counts(normalize=True)
mezcla[mezcla.tipo_reclamo == 'TRANSFERENCIA ERRONEA '].groupby(['eif', 'favorabilidad']).size()

#%%

# TOP 10 POR SEXO

top10 = entradas.tipo_reclamo.value_counts(ascending=False)[:10]
top10.loc['OTROS'] = entradas.tipo_reclamo.value_counts()[10:].sum()

sex_partition = pd.DataFrame()
for top in top10.index:
    filtro = entradas.tipo_reclamo == top
    sex_partition[top]=entradas[filtro].genero.value_counts(normalize=True)
sex_partition = sex_partition.T
sex_partition.loc['OTROS'] = entradas[~entradas.tipo_reclamo.isin(top10.index[:10])].genero.value_counts(normalize=True)
sex_partition


#%%
from prousuario_tools import get_sb_colors
def create_tipo_sexo_graph(top):
    fig = px.bar(top,
                 x=['Masculino', 'Femenino'], barmode='relative', text_auto=True,
                 template='presentation',
                 color_discrete_map=dict(Masculino=get_sb_colors()['blue sb dark'], Femenino=get_sb_colors()['sb gray']),
                 opacity=0.8,
                 orientation='h', range_x=[-0.02,1],
                 # width=1600, height=800,

                 )
    fig.update_traces(texttemplate='<b>%{x:.0%}</b>')
    # fig.update_traces(texttemplate='%{x:.0%}')
    fig.update_layout(font_family='Arial', yaxis_automargin=True, showlegend=True,
                      xaxis_showgrid=False, yaxis_zeroline=False, xaxis_zeroline=False, yaxis_autorange='reversed',
                      xaxis_visible=False, yaxis_title=None, yaxis_tickfont_size=15, legend_orientation='h',
                      legend_title=None, legend_y=-0.03)
    annotations = []
    for idx, val in enumerate(top10.values):
        annotations.append(
            dict(yref='y', x=1.15, y=idx, xref='paper',
            text=f'{val:,.0f} - <b>{val/top10.sum():,.0%}</b>', textangle=0, align='left',
            font=dict(
                family='Calibri',
                size=15
            ),
            showarrow=False)
        )
    annotations.append(
            dict(yref='y', x=1.15, y=len(top)+0.2, xref='paper',
            text=f'<b>Cantidad<br>de casos</b>', textangle=0, align='left',
            font=dict(
                family='Calibri',
                size=15
            ),
            showarrow=False
                 ))
    fig.update_layout(annotations=annotations)
    fig.add_vline(0.5, line_color='red', line_dash='dash')
    # labels = {"F_pct": "Favorable", "D_pct": "Desfavorable"}

    #
    # for idx, val in enumerate(labels.items()):
    #     print(idx, val)
    #     if fig.data[idx]['name'] == val[0]:
    #         fig.data[idx]['name'] = val[1]

    plot(fig)

create_tipo_sexo_graph(sex_partition)

#%%

salidas_genero = pd.merge(salidas, claims[['codigo', 'genero']], on='codigo', how='left')
salidas_genero['monto'] = salidas_genero.monto_instruido_dop.fillna(0) + salidas_genero.monto_instruido_usd.fillna(0) * 56
grouper = pd.Grouper(key='fecha_cierre', freq=freq)
favorable = salidas_genero.favorabilidad == "F"
carta = salidas_genero.tipo_respuesta == "Carta Informativa"
reconsideracion = salidas_genero.reconsideracion.astype(bool)
filtro_m = salidas_genero.genero == 'Masculino'
filtro_f = salidas_genero.genero == 'Femenino'
hombres = salidas_genero[favorable & ~reconsideracion & ~carta & filtro_m]
mujeres = salidas_genero[favorable & ~reconsideracion & ~carta & filtro_f]

labels = []
for idx in pd.cut(hombres.monto, range(0,55001,5000)).value_counts().sort_index().index:
    if idx.left < 50000:
        labels.append(f"De ${idx.left+1:,.0f} a ${idx.right:,.0f}")
    else:
        labels.append(f"Más de ${idx.left+1:,.0f} ")

data_montos = pd.DataFrame([
pd.cut(hombres.monto.clip(1,51000), range(0,55001,5000)).value_counts().sort_index().rename('Masculino'),
pd.cut(mujeres.monto.clip(1,51000), range(0,55001,5000)).value_counts().sort_index().rename('Femenino')]).T
data_montos.index = labels

#%%

fig = px.bar(data_montos, y=['Masculino', 'Femenino'], barmode='group'
            ,template='presentation', text_auto=True, range_y=[0,data_montos.values.max()*1.1],
                 color_discrete_map=dict(Masculino=get_sb_colors()['blue sb dark'], Femenino=get_sb_colors()['sb gray']),
                 # opacity=0.8,
                 # orientation='h', range_x=[-0.02,1],
             )
fig.update_traces(textposition='outside')
fig.update_layout(font_family='Arial', xaxis_automargin=True, showlegend=False,
                  xaxis_showgrid=False, yaxis_zeroline=False, xaxis_zeroline=False, yaxis_showgrid=False, yaxis_visible=False,
                  xaxis_visible=True, yaxis_title=None, yaxis_tickfont_size=15, legend_orientation='h',
                  legend_title=None)
plot(fig)

#%%

salidas.monto

#%%
from sql_tools import query_reader

entradas_salidas
query = "SELECT * FROM RESULTADOS_RECLAMOS WHERE FECHA_CIERRE BETWEEN DATE '2024-07-01' AND DATE '2024-08-01'"
julio = query_reader(query, mode='all')
julio.fecha_cierre.dt.date.value_counts().sort_index()

#%%
if __name__ == "__main__":
    main()
