# Created on 13/9/2024 by jacevedo

import pandas as pd
import plotly.express as px
from plotly.offline import plot
import locale
from sql_tools import query_reader
from prousuario_tools import get_sb_colors
import numpy as np
#%%

education_order = {
 'Primaria': 0,
 'Ninguno': 1,
 'Secundaria': 2,
 'Técnico': 3,
 'Universitario': 4,
 'Maestría': 5,
 'Doctorado': 6
}

education_order_r = {
 0: 'Primaria',
 1: 'Ninguno',
 2: 'Secundaria',
 3: 'Técnico',
 4: 'Universitario',
 5: 'Maestría',
 6: 'Doctorado'
}

income_order = {
 'Ninguno': 0,
 'Desempleado': 1,
 'Empleado público': 2,
 'Empleado privado': 3,
 'Independiente': 4,
 'Pensionado': 5
}

income_order_r = {
 0: 'Ninguno',
 1: 'Desempleado',
 2: 'Empleado público',
 3: 'Empleado privado',
 4: 'Independiente',
 5: 'Pensionado'}

#%%

query = """
select 
    Name nombre
    , Email email
    , Gender genero
    , CreatedAt fecha_creacion
    , IdentificationCard cedula
    , Birthdate fecha_nac
    , Nationality nacionalidad
    , CivilStatus estado_civil
    , LoginsCount cantidad_logins
    , CASE 
        when EducationLevel = '' THEN 'Ninguno'
        Else EducationLevel 
    END nivel_educativo
        , CASE 
        when IncomeSource = '' THEN 'Ninguno'
        Else IncomeSource 
    END fuente_ingresos
    , MonthlyIncome ingresos
    , AnotherDebts otras_deudas
from UserInfo
where EmailVerified = 1
and UserIdentityVerificationStatus = 2
"""

df = query_reader(query, mode='all', creds='azure')

df['orden_educativo'] = df.nivel_educativo.map(education_order)
df['orden_fuente_ingresos'] = df.fuente_ingresos.map(income_order)
df.ingresos = df.ingresos.astype(float)
df.ingresos = abs(df.ingresos)
df.otras_deudas = abs(df.otras_deudas.astype(float))

filtro = df.fecha_nac.str.len() == 10
pd.to_datetime(df.loc[filtro].fecha_nac.str.replace('-', '/'), format='mixed')
#%%

def create_dist_chart(column, order=None):
    data = pd.DataFrame([
            df[column].value_counts().sort_index().rename('cantidad'),
            df[column].value_counts(normalize=True).sort_index().rename('porcentaje')
        ]).T
    data.index = data.index.map(order)
    fig = px.bar(data, template='plotly_white'
                 , text_auto=True, range_y=[0, data.cantidad.max()*1.2]
                 , color_discrete_sequence=[get_sb_colors()['blue sb dark']]
                 , custom_data='porcentaje'
                 )
    fig.update_traces(
        textposition='outside'
        , texttemplate='%{y:,.3s}<br><b>%{customdata[0]:.1%}</b>'
    )
    fig.update_layout(
        title=None,
        xaxis_title=None,
        yaxis_showgrid=False,
        yaxis_visible=False,
        showlegend=False
    )
    plot(fig)

#%%

create_dist_chart('orden_educativo', order=education_order_r)
create_dist_chart('orden_fuente_ingresos', order=income_order_r)

#%%

# Define the number of bins you want
number_of_bins = 10

# Create bin edges starting from 1 to the maximum value in your data


# Use value_counts with the custom bin edges

data = df[df.ingresos > 0].ingresos.copy()

min_value = 0
max_value = 200000
steps = 20000

data = pd.DataFrame([
    data.clip(1, upper=max_value+1).value_counts(
        bins=range(min_value, max_value+steps+1, steps)
    ).sort_index().rename('cantidad'),
    data.clip(1, upper=max_value+1).value_counts(
        bins=range(min_value, max_value+steps+1, steps), normalize=True
    ).sort_index().rename('porcentaje')
]).T
# [f"DOP {a[0]}-{a[1]}" for a in data.index]
#%%
labels = []
for idx in data.index:
    if idx.right == 20000:
        labels.append(f"${idx.right:,.0f} o menos")
    elif idx.left < 200000:
        labels.append(f"${idx.left+1:,.0f}-{idx.right:,.0f}")
    else:
        labels.append(f"Más de ${idx.left:,.0f} ")
data.index = labels
#%%

fig = px.bar(data, y='cantidad', template='plotly_white'
             , text_auto=True, range_y=[0, data.cantidad.max()*1.2]
             , color_discrete_sequence=[get_sb_colors()['blue sb dark']]
             , custom_data='porcentaje'
             )
fig.update_traces(
    textposition='outside'
    , texttemplate='%{y:,.3s}<br><b>%{customdata[0]:.1%}</b>'
    # , texttemplate='<b>%{y:,.3s}'
)
fig.update_layout(
    title=None,
    xaxis_title=None,
    yaxis_showgrid=False,
    yaxis_visible=False,
    showlegend=False
)
plot(fig)


#%%

query = """
select 
cedula
, genero
from IDV2
"""
usuarios = query_reader(query, mode='all')
usuarios
