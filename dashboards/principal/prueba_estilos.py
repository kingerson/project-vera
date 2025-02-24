"""
Creado el 11/12/2023 a las 12:27 p. m.

@author: jacevedo
"""
import dash
from dash import dcc, html
import plotly.express as px

EXTERNAL_STYLESHEETS = [
    '/assets/css/statistics_counter.min.css',
    '/assets/css/main.min.css'
]
app = dash.Dash(__name__,
                external_stylesheets=EXTERNAL_STYLESHEETS
                )

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H1('RD$370.2 Millones',
                          className='number')
                ], className="container")
            ], className="statistic_info_2"),
    ], className="statistic_counter")
], className='main_layout_reverse', style=dict(background='white'))

# <div class="statistic_info_2">
#         <div class="container">
#             <span id="credit-amount-mobile" class="number" hidden="" style="display: inline;">RD$370.2M</span>
#             <span id="credit-amount-desktop" class="number" hidden="" style="display: none;">RD$370.2 Millones</span>
#             <span class="description">Pesos instruidos a ser acreditados a usuarios reclamantes</span>
#         </div>
#     </div>

if __name__ == '__main__':
    app.run_server(debug=True, port=2020)
