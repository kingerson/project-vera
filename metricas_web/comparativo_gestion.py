"""
Creado el 26/2/2024 a las 3:57 PM

@author: jacevedo
"""

import plotly.graph_objects as go
import  plotly.subplots as sp
from plotly.offline import plot
from prousuario_tools import get_sb_colors
colores = get_sb_colors()

#%%
# Create subplots with 1 row and 2 columns
def agrega_trace(fig, data, total, col, title, dimension, formato='porciento'):
    formatos = {
        'porciento': '<b>%{y:.0%}<b>',
        'dinero': '<b>$%{y:.1f}<b>',
        'cantidad': '<b>%{y:.1f}<b>',
        # 'miles': '<b>%{y:.0f}<br><sub>miles</sub><b>',
        'miles': '<b>%{y:,.0f}<br><b>',
    }
    total_titles = {
        1:f'Total de casos<br>recibidos<br><b>{total}',
        2:f'Favorabilidad<br>general<br><b>{total:.0%}',
        3:f'Monto total<br>dispuesto a acreditar<br><b>${total/1000000:,.1f} M',
        4:f'Monto promedio general<br>dispuesto a acreditar<br><b>${total:,.2f}'
    }
    labels = ['Ago.2016<br>Ago.2020', 'Ago.2020<br>Ago.2024']
    print(title)
    text=data
    # print(title)
    if title == 'Monto total<br> a acreditar':
        text=[data, data/total]
    if title == 'Contactos<br>recibidos':
        labels = ['Ago.2016<br>Ago.2020', 'Ago.2020<br>Jul.2024']
    fig.add_trace(go.Bar(x=labels, y=data, text=text, textangle = 0,
                         texttemplate=formatos[formato],
                         # bargap=0.30, bargroupgap=0.0
                         ), row=1, col=col)
    fig['layout'][f'yaxis{col}']['range'] = [0,max(data)*1.1]
    fig['layout'][f'yaxis{col}']['range'] = [0,max(data)*1.1]
    fig.add_annotation(dict(
        yref='paper', x=-0.65, y=0.95, xref=f'x{col}',
        text=dimension, textangle=-90, align='left',
        font=dict(
            family='Calibri',
            size=18
        ),
        showarrow=False
             ))
    fig.add_annotation(dict(
        yref='paper', x=1.1, y=1.25, xref=f'x{col}',
        text=f"+{(data[1] / data[0])-1:.0%}", textangle=0, align='right',
        font=dict(
            family='Calibri',
            size=50,
            color=colores['turquesa pro']
        ),
        showarrow=False
    ))
    # # print(fig.layout.annotations[col - 1]['x'] - 0.10625)
    # # print(fig.layout.annotations[col - 1]['x'])
    # # print(col)
    # if col == 1:
    #     xpos = f'x domain'
    # else:
    #     xpos = f'x{col} domain'
    # print(xpos)
    # fig.update_annotations(x=fig.layout.annotations[col-1]['x']-0.10625, xref=xpos)
    # #                        )
titles=[
    'Contactos<br>recibidos',
    'Reclamaciones<br>recibidas',
    'Favorabilidad',
    'Monto dispuesto<br> a acreditar',
]

fig = sp.make_subplots(rows=1, cols=4, subplot_titles=titles)
agrega_trace(fig, [83700/1000,323600/1000 ] , 2, 1, titles[0] , 'miles','cantidad')

agrega_trace(fig, [6237, 19019], 3, 2, titles[1], '', 'miles')
agrega_trace(fig, [0.5, 0.68], 3,3, titles[2], '%','porciento')
agrega_trace(fig, [79895263.58/1000000, 483054907.22/1000000], 3, 4, titles[2], 'millones de pesos', 'dinero')
fig.update_layout(
    showlegend=False, template='presentation', font_family='Arial', font_size=25,
    width=1400, height=600, uniformtext_minsize=34, uniformtext_mode='show',
    # xaxis_tickfont_size=8,

   # margin={'autoexpand': True}
    # margin={'g': 10, 't': 10}
    margin={'b': 150},
barmode='group', bargap=0

)
fig.add_vline(-.5)
fig.update_annotations(selector={"y": 1.0}, font_size=20, y=1.1, align='left')
for i in range(0,4):
#     fig.layout.annotations[i].x
    if i == 0:
        xref = 'x'
    else:
        xref = f'x{i+1}'
    fig.layout.annotations[i].x = -0.1
    fig.layout.annotations[i].xref = xref
#     fig.layout.annotations[i].x = fig.layout.annotations[i].x-0.04625
#     fig.layout.annotations[i].x = fig.layout.annotations[i].x*0.5
# for idx, x in enumerate(range(1,9,2)):
#     xpos = x / 8 * 0.9
#     print(xpos)
#     if idx == 0:
#         ref = f'x domain'
#     else:
#         ref = f'x{idx+1} domain'
#     print(ref)
#     fig.update_annotations(selector={"y": 1.1}, x=xpos, xref=ref)

# fig.for_each_trace(layout_barmode='group', layout_bargap=0)
# for i in range(1, 4):
#         fig.update_xaxes(row=1, col=i, showticklabels=False)
#         fig.update_yaxes(row=1, col=i, showticklabels=False)
#         fig.update_layout(barmode='group', bargap=0)
# fig.update_annotations(selector={"y":1.0}, font_size=25, y=1.1)
fig.update_yaxes(visible=False, automargin=True)
fig.update_xaxes(tickfont=dict(size=15), visible=True)
# fig.update_layout(xaxis_visible=False)
fig.update_traces(
                  marker_color=[colores['sb gray'], colores['blue sb dark']],
                  marker_cornerradius=5, textposition='inside')
# fig.update_layout(showlegend=True)
plot(fig)