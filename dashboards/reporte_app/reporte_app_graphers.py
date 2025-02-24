"""
Creado el 2/9/2024 a las 1:55 PM

@author: jacevedo
"""


import plotly.express as px
from plotly.offline import plot
import plotly.graph_objs as go
from prousuario_tools import get_sb_colors
colores = get_sb_colors()
#%%

def graph_users_datebars(data):
    fig = px.bar(data, x='Fecha', y=['Registrados', 'Verificados'], barmode='group'
                 , template='plotly_white',
                 color_discrete_sequence=[colores['sb gray'], colores['blue sb dark']]
                 )
    fig.add_trace(
        go.Scatter(x=data.Fecha, y=data.Conversion
                   , name='Conversión',
                   # mode='lines+text',
                   yaxis='y2'
                   ,line_color=colores['turquesa pro']
                   )
    )
    fig.update_layout(                  #
    yaxis = dict(
           title="<b>Cantidad de usuarios",     showgrid=True

            , ticklen=10, dtick=200, tickformat=',.0f'
           ),
    yaxis2 = dict(title="<b>Porcentaje convertido", title_font_color=colores['turquesa pro']
                  ,    showgrid=True
                  ,side='right', overlaying='y'
                    , range=[0,data.Conversion.max()*1.1], dtick=0.4

                  )
    ,legend_orientation='h'
    , legend_y=1
        , legend_title=None
        # , legend_labels=[52]
    )
    return fig