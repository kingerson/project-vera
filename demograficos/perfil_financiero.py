"""
Creado el 25/8/2024 a las 2:03 PM

@author: jacevedo
"""

import pandas as pd
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objs as go
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.preprocessing import StandardScaler


#%%

df = pd.read_pickle('sumacuotas_app_20240824.pickle')
df.suma_cuotas =df.suma_cuotas.fillna(0).astype(float)
df.consumos_12m =df.consumos_12m.fillna(0).astype(float)

filtro_a = df['consumos_12m'] <=100
filtro_b = df['suma_cuotas'] <=100
con_deuda = df[~(filtro_a & filtro_b)].copy()
# con_deuda = df.copy()
#%%

# Assume 'data' is your original dataset
scaler = StandardScaler()
con_deuda['suma_cuotas_scaled'] = scaler.fit_transform(con_deuda[['suma_cuotas']].clip(upper=500000))
con_deuda['consumos_12m_scaled'] = scaler.fit_transform(con_deuda[['consumos_12m']].clip(upper=500000))

#%%

km = KMeans(n_clusters=10, init='k-means++', random_state=0)

# filtro_a = con_deuda['consumos_12m'] <=100
# filtro_b = con_deuda['suma_cuotas'] <=100
# con_deuda = con_deuda[~(filtro_a | filtro_b)]
# con_deuda = con_deuda_scaled.copy()
# con_deuda.consumos_12m = con_deuda.consumos_12m.clip(upper=1000000)
# con_deuda.suma_cuotas = con_deuda.suma_cuotas.clip(upper=1000000)
result = km.fit(con_deuda[['suma_cuotas_scaled', 'consumos_12m_scaled']])

con_deuda['labels'] = pd.Series(result.labels_).astype(str).values
centroids = result.cluster_centers_


#%%

n_clusters = 10
batch_size = len(con_deuda)//n_clusters

minikm = MiniBatchKMeans(n_clusters=n_clusters, batch_size=batch_size, random_state=9)

# filtro_a = con_deuda['consumos_12m'] <=100
# filtro_b = con_deuda['suma_cuotas'] <=100
# con_deuda = con_deuda[~(filtro_a | filtro_b)]
# con_deuda = con_deuda_scaled.copy()
# con_deuda.consumos_12m = con_deuda.consumos_12m.clip(upper=1000000)
# con_deuda.suma_cuotas = con_deuda.suma_cuotas.clip(upper=1000000)
result = minikm.fit(con_deuda[['suma_cuotas_scaled', 'consumos_12m_scaled']].values)

con_deuda['labels'] = pd.Series(result.labels_).astype(str).values
centroids = result.cluster_centers_

#%%

colormap = {x:y for x, y in zip(
    pd.Series(con_deuda['labels']).sort_values().unique()
    , px.colors.qualitative.T10[:len(con_deuda)]
    )
}

fig = px.scatter(x=con_deuda['suma_cuotas'].clip(upper=500000), y=con_deuda['consumos_12m'].clip(upper=500000),
              # color=labels, color_discrete_map={x:y for x, y in zip(pd.Series(labels).unique(), px.colors.qualitative.T10[:len(labels)])}
              color=con_deuda['labels']
                 # , color_discrete_sequence=px.colors.qualitative.T10
            ,color_discrete_map=colormap
                # ,log_x=True, log_y=True
                 ,template='presentation'
                ,width=1000,height=800
              )
# fig.add_trace(go.Scatter(x=centroids[:, 0], y=centroids[:, 1], fillcolor='red', line=dict(width=0)))

# fig.add_shape(x0=0, x1=df['suma_cuotas'].max(), y0=0, y1=df['consumos_12m'].max(), type='line')
fig.update_layout(xaxis_title='Suma Cuotas en DOP', yaxis_title='Consumo Promedio 12 Meses en DOP')
plot(fig)

#%%

for label in con_deuda['labels'].unique():
    filtro = con_deuda.labels == label
    print(label)
    print('-' * 20)
    print('suma_cuotas')
    print(f"Min: {con_deuda[filtro]['suma_cuotas'].min():,.2f}")
    print(f"Max: {con_deuda[filtro]['suma_cuotas'].max():,.2f}")
    print('-'*20)
    print('consumos_12m')
    print(f"Min: {con_deuda[filtro]['consumos_12m'].min():,.2f}")
    print(f"Max: {con_deuda[filtro]['consumos_12m'].max():,.2f}")
    print('='*20)


#%%

# Elbow method

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Assuming 'data' is your dataset
wcss = []
for i in range(2, 15):  # testing 1 to 10 clusters
    kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
    kmeans.fit(con_deuda[['suma_cuotas_scaled', 'consumos_12m_scaled']])
    wcss.append(kmeans.inertia_)

plt.plot(range(2, 15), wcss)
plt.title('The Elbow Method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')  # Within cluster sum of squares
plt.show()

#%%
data = con_deuda[['suma_cuotas_scaled', 'consumos_12m_scaled']]
from sklearn.metrics import silhouette_score

silhouette_scores = []
for i in range(2, 15):  # silhouette score is only applicable for 2 or more clusters
    kmeans = KMeans(n_clusters=i, random_state=0)
    kmeans.fit(data)
    score = silhouette_score(data, kmeans.labels_)
    silhouette_scores.append(score)

plt.plot(range(2, 15), silhouette_scores)
plt.title('Silhouette Scores vs Number of clusters')
plt.xlabel('Number of clusters')
plt.ylabel('Silhouette Score')
plt.show()


#%%

for label in con_deuda['labels'].sort_values().unique():
    filtro = con_deuda.labels == label
    print(f"Grupo {int(label)+1}")
    print('-' * 20)
    print(f"{con_deuda[filtro]['suma_cuotas'].size:,} registros")
    print(f"Cuotas promedio: ${con_deuda[filtro]['suma_cuotas'].mean():,.2f}")
    print(f"Consumos promedio: ${con_deuda[filtro]['consumos_12m'].mean():,.2f}")
    print('=' * 20)

#%%

colormap = {x:y for x, y in zip(
    pd.Series(con_deuda['labels']).sort_values().unique()
    , px.colors.qualitative.T10[:len(con_deuda)]
    )
}
for label in con_deuda['labels'].sort_values().unique():
    filtro = con_deuda.labels == label
    data = con_deuda[filtro]
    fig = px.scatter(x=data['suma_cuotas_scaled'], y=data['consumos_12m_scaled'],
                  # color=labels, color_discrete_map={x:y for x, y in zip(pd.Series(labels).unique(), px.colors.qualitative.T10[:len(labels)])}
                  color=data['labels']
                     , title=f'Grupo {label}'
                     # , color_discrete_sequence=px.colors.qualitative.T10
                ,color_discrete_map=colormap
                    # ,log_x=True, log_y=True
                     ,template='plotly_white'
                    ,width=1000,height=800
                  )
    # fig.add_trace(go.Scatter(x=centroids[:, 0], y=centroids[:, 1], fillcolor='red', line=dict(width=0)))

    # fig.add_shape(x0=0, x1=df['suma_cuotas'].max(), y0=0, y1=df['consumos_12m'].max(), type='line')
    fig.update_layout(xaxis_title='Suma Cuotas', yaxis_title='Consumo Promedio 12 Meses')
    plot(fig)