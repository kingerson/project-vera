"""
Creado el 12/8/2022 a las 9:07 a. m.

@author: jacevedo
"""
import pandas as pd
import scipy as sp
import plotly.express as px
from plotly.offline import plot
import locale

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')

import sql_tools

#%%

### REPORTE COMPLETO, puedes elegir cual version quieres usando el 'ano' y 'month' correspondiente.

orden_columnas = [
    'id_reclamo', 'id_reclamante', 'genero', 'tipo_persona', 'nacionalidad',
    'nombre_completo', 'entidad', 'razon', 'tipo_producto', 'canal',
    'tipo_reclamo', 'monto_reclamado', 'moneda', 'tasa_divisa',
    'fecha_apertura', 'fecha_respuesta', 'favorabilidad', 'respuesta',
    'status'
]

query = (
    " SELECT"
    "   TRIM(A.idreclamo) id_reclamo,"
    "   TRIM(A.idreclaman) id_reclamante,"
    "   TRIM(A.nombres) ||' '|| TRIM(A.apellidos) nombre_completo,"
    "   TRIM(A.descripcio) razon,"
    "   A.monto monto_reclamado,"
    "   A.moneda,"
    "   A.tasadia tasa_divisa,"
    "   A.fechapertu fecha_apertura,"
    "   A.fechareso fecha_respuesta,"
    "   A.resultado favorabilidad,"
    "   TRIM(A.solucion) respuesta,"
    "   A.ESTATUS status,"
    "   b.nombre_corto entidad,"
    "   TRIM(c.descripcio) tipo_reclamo,"
    "   d.genero genero,"
    "   d.persona tipo_persona,"
    "   d.residencia nacionalidad,"
    "   TRIM(E.descripcio) tipo_producto,"
    "   TRIM(f.descripcio) canal"
    " FROM"
    "   PUDRECLAMO A"
    " left join "
    "   REGISTRO_ENTIDADES B on A.ENTIDAD = B.CODIGOI"
    " left join"
    "   PATIPRECLA C on A.TIPRECLA = C.CODIGO"
    " left join"
    "   TIPODEU D on A.IDPERSONA = D.TIPO"
    " left join"
    "   PRODUSERVI E on A.TIPO = E.CODIGO"
    " left join"
    "   CANALDIST F on A.canaldis = F.COD_CANAL"
    " WHERE"
    "   ano = 2022"
    "   and mes = 6"
)

pu01 = sql_tools.query_reader(query, mode='all')
pu01 = pu01[orden_columnas]
pu01.head().T

#%%

query = (
    " SELECT"
    " canaldis,"
    " count(canaldis)"    
    " FROM"
    "   PUDRECLAMO"
    " WHERE"
    "   ano = 2022"
    "   and mes = 6"
    " group by canaldis"
)

canal = sql_tools.query_reader(query, mode='many', nrows=100)
canal


#%%

### REPORTE BASICO POR ENTIDAD

def get_reporte_basico(year, month):
    global query, reporte_basico, reporte_basico
    query_reporte_basico = (
        "select "
        "a.entidad,"
        "a.cantidad,"
        "c.cantidad_favorables "
        "from ( "
        "SELECT "
        "b.nombre_corto entidad,"
        "count(idreclamo) cantidad "
        "FROM "
        "PUDRECLAMO a "
        "LEFT JOIN "
        "REGISTRO_ENTIDADES B ON A.ENTIDAD = B.CODIGOI "
        "WHERE "
        f"ano = {year} "
        f"AND mes = {month} "
        "GROUP BY b.nombre_corto"
        ") a "
        "LEFT JOIN ( "
        "SELECT "
        "b.nombre_corto entidad,"
        "count(idreclamo) cantidad_favorables "
        "FROM "
        "PUDRECLAMO a "
        "LEFT JOIN "
        "REGISTRO_ENTIDADES B on A.ENTIDAD = B.CODIGOI "
        "WHERE "
        f"ano = {year} "
        f"AND mes = {month} "
        "and a.resultado = 'F' "
        "GROUP BY b.nombre_corto "
        ") c on a.entidad = c.entidad"

    )
    result = (
        sql_tools
            .query_reader(query, mode='many')
            .sort_values('cantidad', ascending=False,ignore_index=True)
    )
    result.cantidad_favorables = result.cantidad_favorables.fillna(0)
    result['share'] = result.cantidad / result.cantidad.sum()
    result['favorabilidad'] = result.cantidad_favorables / result.cantidad
    return result




#%%

### CANTIDAD POR ENTIDAD

def get_cantidad_por_entidad(reporte_basico):
    data = reporte_basico.nlargest(15, 'share')
    data.loc[15] = ['OTROS'] + list(reporte_basico.loc[15:, reporte_basico.columns[1:]].sum())
    fig = px.bar(data, x='entidad', y='share', custom_data=['cantidad'], text='share',
                 title='Distribucion reclamos - Q2 2022', template='presentation')
    fig.update_traces(
        hovertemplate='Entidad: %{x}<br>Cantidad de reclamos: %{customdata[0]:,}<extra></extra>',
        # texttemplate = '%{y:.1%}',
        texttemplate='<b>%{y:.1%}</b><br>%{customdata[0]:.0s}',
        textposition='outside',

    )
    fig.update_layout(
        yaxis_showticklabels=False,
        yaxis_title='Porcentaje de reclamos',
        xaxis_title='Entidad',
        yaxis_range=[0, .55],
        xaxis_automargin=True,
        font_family='Calibri',
        yaxis_showgrid=False
    )
    plot(fig)

#%%
def get_favorabilidad_por_entidad(reporte_basico):
    data = reporte_basico.sort_values('favorabilidad', ascending=False)
    # data.loc[15] = ['OTROS'] + list(reporte_basico.loc[15:, reporte_basico.columns[1:]].mean())
    fig = px.bar(data, x='entidad', y='favorabilidad', custom_data=['cantidad'], text='favorabilidad',
                 color='favorabilidad',
                 template='presentation', color_continuous_scale=px.colors.diverging.RdYlGn,
                 color_continuous_midpoint=0.5,
                 )
    fig.update(layout_coloraxis_showscale=False)
    fig.update_traces(
        hovertemplate='Entidad: %{x}<br>Porcentaje de favorables: %{customdata[0]:,}<extra></extra>',
        texttemplate='<b>%{y:.0%}</b><br>%{customdata[0]:.0s}',
        textposition='outside'

    )
    fig.update_layout(
        yaxis_showticklabels=False,
        yaxis_title='Porcentaje de favorables',
        xaxis_title='Entidad',
        yaxis_range=[0, 1],
        xaxis_tickangle=-45,
        xaxis_automargin=True,
        font_family='Calibri',
        font_size=15,
        yaxis_showgrid=False,
        showlegend=False,
        uniformtext_mode='show'
    )
    fig.add_hline(data.cantidad_favorables.sum() / data.cantidad.sum(), line_color='#0d3048', line_dash='dash',
                  annotation_text=f"Promedio de la industria: <b>{data.cantidad_favorables.sum() / data.cantidad.sum():,.0%}</b>",
                  annotation_position="top right", opacity=0.7, annotation_font_color='black'
                  )
    fig.add_hline(0.75, line_color='#0d3048', line_dash='dash',
                  annotation_text=f"Favorabilidad en ProUsuario: <b>{0.75:,.0%}</b>",
                  annotation_position="top right", opacity=0.7, annotation_font_color='black'
                  )
    plot(fig)

#%%

reporte_basico = get_reporte_basico(2022, 6)
get_cantidad_por_entidad(reporte_basico)
get_favorabilidad_por_entidad(reporte_basico)

#%%

### Cantidad vs Favorabilidad

fig = px.scatter(reporte_basico, x='share', y='favorabilidad',template='presentation',
                 range_y=[0,1],
                 range_x=[0,1],
                 # text='entidad'
                 )
plot(fig)

#%%

filtro_genero = pu01.genero.str.contains('Masculino|Femenino')
data = pu01[filtro_genero].genero.value_counts()

fig = px.pie(values=data, names=list(data.index), template='presentation',
             color_discrete_sequence=['#4c6978', '#f77245'])
fig.update_layout(
    font_family='Calibri',
    legend=dict(
        yanchor="bottom",
        y=-.4,
        xanchor="center",
        x=0.5
    )
)
plot(fig)


#%%

data = pu01.nacionalidad.value_counts()

fig = px.pie(values=data, names=list(data.index), template='presentation',
             color_discrete_sequence=['#4c6978', '#f77245'])
fig.update_layout(
    font_family='Calibri',
    legend=dict(
        yanchor="bottom",
        y=-.7,
        xanchor="center",
        x=0.5
    )
)
plot(fig)

#%%

### FAVORABILIDAD

query = (
    " SELECT"
    "   b.nombre_corto entidad,"
    "   a.resultado favorabilidad,"
    "   count(idreclamo) cantidad"
    " FROM"
    "   PUDRECLAMO a"
    " left join "
    "   REGISTRO_ENTIDADES B on A.ENTIDAD = B.CODIGOI"
    " WHERE"
    "   ano = 2022"
    "   and mes = 6"
    " group by b.nombre_corto, a.resultado"
)

favorabilidad = sql_tools.query_reader(query, mode='all').sort_values('cantidad', ascending=False,ignore_index=True)
favorabilidad.insert(2, 'share', favorabilidad.cantidad / favorabilidad.cantidad.sum())
favorabilidad

#%%

fav_total = favorabilidad.groupby('favorabilidad').sum().cantidad.iloc[:2]
fav_total / fav_total.sum()

#%%
pu01.tasa_divisa = pu01.tasa_divisa.astype(float)
filtro_moneda = pu01.moneda != 'DOP'
pu01['monto_pesos'] = pu01.monto_reclamado.copy()
pu01.loc[filtro_moneda, 'monto_pesos'] = pu01.loc[filtro_moneda, 'monto_reclamado'] + pu01.loc[filtro_moneda, 'tasa_divisa']



#%%

### TIEMPO RESPUESTA

pu01.fecha_apertura
pu01.fecha_respuesta = pd.to_datetime(pu01.fecha_respuesta, errors='coerce', format='%d/%m/%Y')

con_respuesta = ~pu01.fecha_respuesta.isna()

(pu01.fecha_respuesta[con_respuesta] - pu01.fecha_apertura[con_respuesta]).dt.days.describe()


#%%

fig = px.histogram(pu01.monto_pesos)
plot(fig)

#%%

pu01.fecha_respuesta.str.get(3).value_counts()

#%%

17438
18758

#%%

filtro_popular = pu01.entidad == 'POPULAR'
pu01[filtro_popular].tipo_reclamo.value_counts(dropna=False)

#%%

def get_favorabilidad_historica(n_reports):
    query = (
        " SELECT"
        "   a.resultado favorabilidad,"
        "   a.ano || '-' || lpad(a.mes, 2, '0') yearmonth,"
        "   count(idreclamo) cantidad"
        " FROM"
        "   PUDRECLAMO a"
        " WHERE"
        "   ano >= 2012"
        " and a.resultado in ('F', 'D')"
        " group by a.resultado, a.ano, a.mes"
    )
    favorabilidad = sql_tools.query_reader(query, mode='all').sort_values('yearmonth', ascending=False,
                                                                          ignore_index=True)
    favorabilidad.insert(2, 'share', favorabilidad.cantidad / favorabilidad.cantidad.sum())
    return favorabilidad.tail(n_reports)


historico = get_favorabilidad_historica(20)
historico

#%%
data = favorabilidad.sort_values('yearmonth')
total_decisiones = data.groupby('yearmonth').sum().cantidad.rename('total')
data = pd.merge(data, total_decisiones, left_on='yearmonth', right_index=True)
data['share'] = data.cantidad / data.total
data = data.where(data['favorabilidad'] == 'F').dropna().reset_index(drop=True)
data = data.tail(20).reset_index(drop=True)
#
# def plot_favorabilidad_historica(data, col):
#     fig = px.line(data, x='yearmonth', color='favorabilidad', y=col,
#                   template='presentation', color_discrete_sequence=['red', 'green'],
#                   labels={'favorabilidad': "Favorabilidad"}
#                   )
#     fig.update_traces(
#         opacity=0.5
#     )
#     fig.update_layout(
#         yaxis_showgrid=False,
#         xaxis_showgrid=False,
#         font_family='Calibri',
#         yaxis_title='Distribución de las respuestas',
#         xaxis_title=None,
#         xaxis_tickformat='%Y-%m',
#         xaxis_tickmode='array',
#         xaxis_tickvals=data.yearmonth,
#         xaxis_tickangle=-45
#     )
#     if col == 'share':
#         fig = add_percentage_formatting(col, data, fig)
#     else:
#         fig = add_formatting(col, data, fig)
#     return fig
#
#
# def add_percentage_formatting(col, data, fig):
#     fig.update_layout(
#         yaxis_tickformat=',.0%'
#     )
#     filtro_f = data.favorabilidad == 'F'
#     fig.add_hline(data[filtro_f][col].mean(), line_dash='dash', line_color='green', opacity=1,
#                   annotation_text=f"Promedio favorable: {data[filtro_f][col].mean():,.0%}",
#                   annotation_position="top left", annotation_bgcolor="white",
#                   annotation_font_color='black'
#                   # annotation_bgcolor_opacity=0.5
#                 )
#     fig.update_annotations(opacity=0.7)
#     filtro_d = data.favorabilidad == 'D'
#     fig.add_hline(data[filtro_d][col].mean(), line_dash='dash', line_color='red', opacity=1,
#                   annotation_text=f"Promedio desfavorables: {data[filtro_d][col].mean():,.0%}",
#                   annotation_position="top left", annotation_bgcolor="white",
#                   annotation_font_color='black'
#                   # annotation_bgcolor_opacity=0.5
#                   )
#     fig.update_annotations(opacity=0.7)
#     return fig
#
# def add_formatting(col, data, fig):
#     filtro_f = data.favorabilidad == 'F'
#     fig.add_hline(data[filtro_f][col].mean(), line_dash='dash', line_color='green', opacity=1,
#                   annotation_text=f"Promedio favorable: {data[filtro_f][col].mean():,.2f}",
#                   annotation_position="top left", annotation_bgcolor="white")
#     filtro_d = data.favorabilidad == 'D'
#     fig.add_hline(data[filtro_d][col].mean(), line_dash='dash', line_color='red', opacity=1,
#                   annotation_text=f"Promedio desfavorables: {data[filtro_d][col].mean():,.2f}",
#                   annotation_position="top left", annotation_bgcolor="white")
#
#
# # plot_favorabilidad_historica(data, 'cantidad')
# fig = plot_favorabilidad_historica(data, 'share')

#%%

fig = px.line(data, x='yearmonth', y='share',
              template='presentation', color_discrete_sequence=['green'],
              labels={'favorabilidad': "Favorabilidad"},
              range_y=[data.share.min()-data.share.std()*2,data.share.max()+data.share.std()*2]
              )
fig.update_traces(
    opacity=0.5
)
fig.update_layout(
    yaxis_showgrid=False,
    xaxis_showgrid=False,
    font_family='Calibri',
    yaxis_title='Nivel de favorabilidad',
    xaxis_title=None,
    xaxis_tickformat='%Y-%m',
    yaxis_tickformat=',.0%',
    xaxis_tickmode='array',
    xaxis_tickvals=data.yearmonth,
    xaxis_tickangle=-45
)

fig.add_hline(data.share.mean(), line_dash='dash', line_color='green', opacity=1,
              annotation_text=f"Promedio favorable: {data.share.mean():,.0%}",
              annotation_position="top left", annotation_bgcolor="white",
              annotation_font_color='black'
              )
fig.update_annotations(opacity=0.7)

res = sp.stats.linregress(data.index, data.share.values)
fig.add_trace(
    px.line(
        y=res.intercept + res.slope*data.index,
        x=data.yearmonth,
        color_discrete_sequence=['#f77245'],
        line_shape='spline',
        # opacity=0.7
    )['data'][0],
)
fig.add_annotation(
    text=f'Valor R de tendencia: {res.rvalue:.2f}',
    x=data.yearmonth.iloc[-2], y=data.share.values[-1]
)
plot(fig)


#%%

query = 'select * from RESULTADOS_RECLAMOS'
df = sql_tools.query_reader(query, mode='all')
filtro = df.fecha_cierre.between('2021-01-01', '2021-07-01')
semestre = df[filtro]

cerrada = semestre.status_cierre == 'C'
favorable = semestre.favorabilidad == 'F'
semestre.activa = semestre.activa.map({1:True, 0:False})


#%%

query = (
    " SELECT"
    "   a.ano || '-' || lpad(a.mes, 2, '0') yearmonth,"
    "   count(idreclamo) cantidad"
    " FROM"
    "   PUDRECLAMO a"
    # " left join "
    # "   REGISTRO_ENTIDADES B on A.ENTIDAD = B.CODIGOI"
    " WHERE"
    "   ano >= 2012"
    # "   and mes = 6"
    " group by a.ano, a.mes"
)

cantidad_reclamos = sql_tools.query_reader(query, mode='all').sort_values('cantidad', ascending=False,ignore_index=True)
cantidad_reclamos = cantidad_reclamos.sort_values('yearmonth', ignore_index=True)
cantidad_reclamos.yearmonth = pd.to_datetime(cantidad_reclamos.yearmonth, format='%Y-%m')

#%%
data = cantidad_reclamos.tail(20).reset_index(drop=True)
fig = px.bar(data, x='yearmonth', y='cantidad', template='presentation')
fig.update_traces(
    marker_color='#0d3048'
)
fig.update_layout(
    font_family='Calibri',
    yaxis_title='Cantidad de reclamos',
    xaxis_tickformat='%Y-%m',
    xaxis_tickmode='array',
    xaxis_tickvals=data.yearmonth
)
promedio = data.cantidad.mean()
fig.add_hline(promedio, line_color='#0cccc6',
              annotation_font_color='black',
              annotation_text=f"Promedio de reclamos: {promedio:,}",
              annotation_position="top left",
              annotation_bgcolor="white",
              line_dash="dash"
              )
fig.update_annotations(opacity=0.7)
# fig.add_trace(
#     px.line(
#         y=data.cantidad.rolling(window=3, min_periods=1, win_type='gaussian', center=True).mean(std=3),
#         x=data.yearmonth,
#         color_discrete_sequence=['#f77245'],
#         line_shape='spline'
#         # opacity=0.7
#     )['data'][0],
# )
res = sp.stats.linregress(data.index, data.cantidad.values)
fig.add_trace(
    px.line(
        y=res.intercept + res.slope*data.index,
        x=data.yearmonth,
        color_discrete_sequence=['#f77245'],
        line_shape='spline',
        # opacity=0.7
    )['data'][0],
)
fig.add_annotation(
    text=f'Valor R de tendencia: {res.rvalue:.2f}',
    x=data.yearmonth.iloc[-2], y=data.cantidad.values[-1]
)

plot(fig)


#%%

#%%

query = (
    "SELECT "
    " c.yearmonth,"
    " c.pendientes,"
    " d.cantidad cantidad"
    " FROM ("
        " SELECT"
        "   a.ano || '-' || lpad(a.mes, 2, '0') yearmonth,"
        "   count(idreclamo) pendientes"
        " FROM"
        "   PUDRECLAMO a"
        " WHERE"
        "   ano >= 2012"    
        " and a.resultado = 'P'"
        " group by a.ano, a.mes"
    ") c "
    "LEFT JOIN ("
        " SELECT"
        "   a.ano || '-' || lpad(a.mes, 2, '0') yearmonth,"
        "   count(idreclamo) cantidad"
        " FROM"
        "   PUDRECLAMO a"
        " WHERE"
        "   ano >= 2012"
        " group by a.ano, a.mes"
    ") d on c.yearmonth = d.yearmonth"
)

pendientes = sql_tools.query_reader(query, mode='many')

    # .sort_values('cantidad', ascending=False,ignore_index=True)
pendientes = pendientes.sort_values('yearmonth', ignore_index=True)
# pendientes.yearmonth = pd.to_datetime(pendientes.yearmonth, format='%Y-%m')


pendientes['tasa_pendientes'] = pendientes.pendientes / pendientes.cantidad

#%%
data = pendientes.tail(20)
fig = px.bar(
    data, x='yearmonth', y='pendientes', template='presentation', custom_data=['tasa_pendientes'],
    range_y=[0, data.pendientes.max()*1.2]
)
fig.update_traces(
    marker_color='#0d3048',
    hovertemplate = 'Entidad: %{x}<br>Cantidad de reclamos: %{customdata[0]:,}<extra></extra>',
    # texttemplate = '%{y:.1%}',
    texttemplate = '<b>%{y:.2s}</b><br>%{customdata[0]:.1%}',
    textposition = 'outside',

)
fig.update_layout(
    font_family='Calibri',
    yaxis_title='Cantidad de reclamos pendientes',
    xaxis_tickformat='%Y-%m',
    xaxis_tickmode='array',
    xaxis_tickvals=data.yearmonth,
    xaxis_title=None,
    xaxis_tickangle=-45,
    yaxis_showgrid=False,
    showlegend=False,
    uniformtext_mode='show'
)
promedio = data.pendientes.mean()
fig.add_hline(promedio, line_color='#0cccc6',
              # annotation_font_color='black',
              # annotation_text=f"Promedio de pendientes: {promedio:,.0f}",
              # annotation_position="top left",
              # annotation_bgcolor="white",
              line_dash="dash"
              )
fig.update_annotations(opacity=0.7)
plot(fig)