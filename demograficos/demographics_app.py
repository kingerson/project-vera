"""
Creado el 31/8/2024 a las 1:26 PM

@author: jacevedo
"""

from sql_tools import query_reader, send_to_oracle
from pandas.tseries.offsets import Week
from datetime import date
from prousuario_tools import get_sb_colors
colores = get_sb_colors()
#%%
# CANTIDAD DE USUARIOS
def get_cantidad_usuarios():
    query = """
    select count(UserId)
    from UserInfo
    where EmailVerified = 1 and UserIdentityVerificationStatus = 2
    """

    return query_reader(query, creds='azure', mode='all').iloc[0,0]

#%%
# CANTIDAD DE SUSCRITOS
def get_subscriptions():
    query = """
    select count(UserId)
    from UserInfo
    where EmailVerified = 1 and UserIdentityVerificationStatus = 2
    and SubscribedToNewsletter = 1
    """

    return query_reader(query, creds='azure', mode='all').iloc[0,0]

#%%

# USUARIOS CON INFORMACION DE PERFIL COMPLETADA

def get_education_income_profiles():
    query = """
    select
        EducationLevel nivel_educativo
        , IncomeSource fuente_ingesos
        , MonthlyIncome ingresos_mensuales
        , AnotherDebts otras_deudas
    from
        UserInfo
    where
        (EducationLevelText is not null or IncomeSourceText is not null)
    and MonthlyIncome > 0
    """

    return query_reader(query, creds='azure', mode='all')

#%%

# Segmentacion por genero

def get_gender_groups():
    query = """
    select genero, count(UserId) cantidad
    from (
        select
        case
            when Gender is null then ''
            when Gender = ',M' then 'M'
        else Gender
        end genero
            , UserId
        from
            UserInfo
        where EmailVerified = 1 and UserIdentityVerificationStatus = 2
        ) a
    group by genero
    """
    result = query_reader(query, creds='azure', mode='all')
    result['porcentaje'] = result.cantidad / result.cantidad.sum()
    return result.set_index('genero')


#%%

# Segmentacion por genero

def get_gender_groups():
    query = """
    select genero, count(UserId) cantidad
    from (
        select
        case
            when Gender is null then ''
            when Gender = ',M' then 'M'
        else Gender
        end genero
            , UserId
        from
            UserInfo
        where EmailVerified = 1 and UserIdentityVerificationStatus = 2
        ) a
    group by genero
    """
    result = query_reader(query, creds='azure', mode='all')
    result['porcentaje'] = result.cantidad / result.cantidad.sum()
    return result.set_index('genero')

#%%
#
# profiles = get_education_income_profiles()
# cantidad_usuarios = get_cantidad_usuarios()
# perfiles_completados = profiles.shape[0]
# perfiles_sin_completar = cantidad_usuarios - perfiles_completados
# por_genero = get_gender_groups()
# suscritos = get_subscriptions()
# #%%
#
# print(f"""
# Usuarios totales:                   {cantidad_usuarios:,}
# Usuarios con perfil completado:     {perfiles_completados:,} ({perfiles_completados/cantidad_usuarios:.1%})
# Usuarios sin perfil completado:     {perfiles_sin_completar:,} ({perfiles_sin_completar/cantidad_usuarios:.1%})
# Usuarios masculinos:                {por_genero.xs('M').cantidad:,.0f} ({por_genero.xs('M').porcentaje:.1%})
# Usuarios femeninos:                 {por_genero.xs('F').cantidad:,.0f} ({por_genero.xs('F').porcentaje:.1%})
# Usuarios suscritos al newsletter:   {suscritos:,} ({suscritos/cantidad_usuarios:.1%})
# """)
#
#
#%%

# COMPORTAMIENTO 2 SEMANAS
def get_dos_semanas():
    fecha_semanas = date.today() - Week(2)
    query = f"""
    select a.fecha fecha, registrados, verificados from
    (
    select cast(CreatedAt as Date) fecha, count(UserId) verificados
    from UserInfo
    where CreatedAt >= '{fecha_semanas.date()}'
    --where CreatedAt >= '2024-08-19'
    and EmailVerified = 1 and UserIdentityVerificationStatus = 2
    group by cast(CreatedAt as Date)
    ) a
    left join (
        select cast(CreatedAt as Date) fecha, count(UserId) registrados
    from UserInfo
    where CreatedAt >= '{fecha_semanas.date()}'
    --where CreatedAt >= '2024-08-19'
    group by cast(CreatedAt as Date)
    ) b on b.fecha = a.fecha
    """
    result = query_reader(query, creds='azure', mode='all')
    result['conversion'] = result.verificados / result.registrados
    result.columns = result.columns.str.title()
    return result

#%%
# COMPORTAMIENTO 8 SEMANAS
def get_ocho_semanas():
    fecha_semanas = date.today() - Week(8)
    query = f"""
    select a.fecha semana, registrados, verificados from
    (
    select CAST(DATEADD(wk, DATEDIFF(wk,0,CreatedAt), 0) as DATE) fecha, count(UserId) verificados
    from UserInfo
    where CreatedAt >= '{fecha_semanas.date()}'
    --where CreatedAt >= '2024-08-19'
    and EmailVerified = 1 and UserIdentityVerificationStatus = 2
    group by CAST(DATEADD(wk, DATEDIFF(wk,0,CreatedAt), 0) as DATE)
    ) a
    left join (
        select CAST(DATEADD(wk, DATEDIFF(wk,0,CreatedAt), 0) as DATE) fecha, count(UserId) registrados
    from UserInfo
    where CreatedAt >= '{fecha_semanas.date()}'
    --where CreatedAt >= '2024-08-19'
    group by CAST(DATEADD(wk, DATEDIFF(wk,0,CreatedAt), 0) as DATE)
    --DATEPART(wk, CreatedAt)

    ) b on b.fecha = a.fecha
    """
    result = query_reader(query, creds='azure', mode='all')
    result['conversion'] = result.verificados / result.registrados
    result.columns = result.columns.str.title()
    return result.sort_values('Semana')
# #%%
# from general_tools import custom_timer
# from timeit import default_timer as timer
#
# @custom_timer
# def transfer_ids_to_oracle():
#     tik = timer()
#     from sqlalchemy.types import VARCHAR, DATE
#     from sqlalchemy import Column, String
#     query = """
#     select  IdentificationCard cedula, Name name, Email email, Gender genero, CreatedAt fecha_creacion
#     from UserInfo
#     where EmailVerified = 1 and UserIdentityVerificationStatus = 2 and CreatedAt < '2024-08-30'
#     """
#     result = query_reader(query, creds='azure', mode='all')
#     result.genero = result.genero.str.strip(',').str.upper().value_counts(dropna=False)
#     print(result.shape)
#     print(f'Se tardo {timer() - tik:.2f} segundos leyendo Azure')
#     tik = timer()
#     dtypes = {
#         'cedula': VARCHAR(14),
#         'name':VARCHAR(255),
#         'email':VARCHAR(255),
#         'genero':String(2),
#         'fecha_creacion':DATE()
#     }
#     send_to_oracle(result, 'IDV2', dtypes=dtypes)
#     print(f'Se tardo {timer() - tik:.2f} segundos enviando a Oracle')
#
# #%%
# transfer_ids_to_oracle()
#
# #%%
#
# dos_semanas = get_dos_semanas()
# ocho_semanas = get_ocho_semanas()
#
# import plotly.express as px
# from plotly.offline import plot
# import plotly.graph_objs as go
# from prousuario_tools import get_sb_colors
# colores = get_sb_colors()
# #%%
#
# fig = px.bar(dos_semanas, x='Fecha', y=['Registrados', 'Verificados'], barmode='group'
#              , template='plotly_white',
#              color_discrete_sequence=[colores['sb gray'], colores['blue sb dark']]
#              )
# fig.add_trace(
#     go.Scatter(x=dos_semanas.Fecha, y=dos_semanas.Conversion
#                , name='Conversión',
#                # mode='lines+text',
#                yaxis='y2'
#                ,line_color=colores['turquesa pro']
#                )
# )
# fig.update_layout(                  #
# yaxis = dict(
#        title="<b>Cantidad de usuarios",     showgrid=True
#
#         , ticklen=10, dtick=200, tickformat=',.0f'
#        ),
# yaxis2 = dict(title="<b>Porcentaje convertido", title_font_color=colores['turquesa pro']
#               ,    showgrid=True
#               ,side='right', overlaying='y'
#                 , range=[0,dos_semanas.Conversion.max()*1.1], dtick=0.4
#
#               )
# ,legend_orientation='h'
# , legend_y=1
#     , legend_title=None
#     # , legend_labels=[52]
# )
# # fig.for_each_trace(
# #     'name',
# #     selector={"name":{x:x.title() for x in dos_semanas.columns[1:]}}
# # )
# plot(fig)
#
#
# #%%
#
# fig = px.bar(ocho_semanas, x='Fecha', y=['Registrados', 'Verificados'], barmode='group'
#              , template='plotly_white',
#              color_discrete_sequence=[colores['sb gray'], colores['blue sb dark']]
#              )
# fig.add_trace(
#     go.Scatter(x=ocho_semanas.Fecha, y=ocho_semanas.Conversion
#                , name='Conversión',
#                # mode='lines+text',
#                yaxis='y2'
#                ,line_color=colores['turquesa pro']
#                )
# )
# fig.update_layout(                  #
# yaxis = dict(
#        title="<b>Cantidad de usuarios",     showgrid=True
#
#         , ticklen=10, tickformat=',.0f'
#        ),
# yaxis2 = dict(title="<b>Porcentaje convertido", title_font_color=colores['turquesa pro']
#               ,    showgrid=True
#               ,side='right', overlaying='y', tickformat=',.0%'
#                 , range=[0,ocho_semanas.Conversion.max()*1.1], dtick=0.1
#
#               )
# ,legend_orientation='h'
# , legend_y=1
#     , legend_title=None
#     # , legend_labels=[52]
# )
# fig.update_yaxes(showgrid=False)
# # fig.for_each_trace(
# #     'name',
# #     selector={"name":{x:x.title() for x in dos_semanas.columns[1:]}}
# # )
# plot(fig)
