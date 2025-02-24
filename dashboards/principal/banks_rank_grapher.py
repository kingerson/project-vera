"""
Creado el 26/5/2022 a las 10:08 a. m.

@author: jacevedo
"""
import locale

from plotly.express import line
from prousuario_tools import get_bank_colors, get_category_colors
from plotly import colors
# from plotly.offline import plot

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')


def create_fig(mentions_count, color_col, colormap):
    fig = line(
        mentions_count,
        x='fecha_creacion',
        y='rank',
        text='cantidad',
        color=color_col,
        height=600,
        # width=1100,
        color_discrete_map=colormap,
        template='presentation'
        )
    return fig


def update_fig(fig, marker_size=45, font_size=23):
    fig.update_traces(
        mode='markers+text+lines',
        marker=dict(
            size=marker_size
            ),
        line=dict(dash='solid', width=2, shape='spline', simplify=True),
        hovertemplate='Cantidad: %{text}',
        textfont=dict(
            size=font_size,
            color="white"
        )
    )
    return fig


def update_fig_layout(mentions_count, fig):
    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 6)),
            ticktext=[f'{a}ª'for a in range(1, 6)],
            # autorange='reversed',
            range=[5.5, 0],
            automargin=True,
            title=None,
            zeroline=False,
        ),
        xaxis=dict(
            title=None,
            tickmode='auto',
            zeroline=False,
            tickfont_size=20,
            # tickvals=list(range(8)),
            # ticktext=list(range(8)),
            ticktext=list(mentions_count['fecha_creacion'].dt.strftime('%b %d').unique()),
            ),
        legend_title_text=None,
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        font=dict(
            family="Arial",
            size=30,
        ),
        legend=dict(
            font_size=20,
            itemsizing='trace',
            itemwidth=50,
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.01
        ),
        paper_bgcolor='#0D3048',
        plot_bgcolor='#0A2336',
        font_color='#F0F3F5',
    )
    return fig


def update_fig_axes(fig):
    fig.update_xaxes(
        dtick="W-MON",
        # dtick="D",
        tickformat="%b %d")
    return fig


def creates_banks_ranks(data, color_col='eif', freq=None):
    data = data.rename('cantidad').reset_index()
    colormap = get_bank_colors()
    titulo_leyenda = 'Entidades'
    if color_col == 'categoria':
        categorias = data.groupby('categoria')['cantidad'].sum().sort_values(ascending=False).index
        colormap = {a[0]: a[1] for a in zip(categorias, colors.qualitative.T10+colors.qualitative.Dark2)}
        titulo_leyenda = 'Categoría'
    data['rank'] = data.groupby(['fecha_creacion']).rank('first', ascending=False)['cantidad'].rename('rank')
    filtro_10 = data['rank'] <= 5
    data = data[filtro_10].reset_index(drop=True)
    fig = create_fig(data, color_col, colormap=colormap)
    if freq == 'D':
        fig = update_fig(fig, marker_size=35, font_size=18)
    else:
        fig = update_fig(fig)
    fig = update_fig_layout(data, fig)
    fig = update_fig_axes(fig)
    fig['layout']['legend']['title'] = titulo_leyenda
    fig['layout']['title'] = f'Por {titulo_leyenda}'
    return fig


