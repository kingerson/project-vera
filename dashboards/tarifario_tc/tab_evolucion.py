# Created on 13/9/2024 by jacevedo

import pandas as pd
import plotly.express as px
from plotly.offline import plot
import locale
from sql_tools import query_reader

mapa_tarjetas = {
 'TARJETA DE CREDITO PERSONAL PLATINO/PLATINUM (O SUPERIOR)': 'Platinum+',
 'TARJETA DE CREDITO PERSONAL CLASICA/STANDARD': 'Clásica',
 'TARJETA DE CREDITO PERSONAL ORO/GOLD': 'Oro',
 'PRÉSTAMOS A TRAVÉS DE LÍNEAS DE CRÉDITO PERSONALES (CRÉDITOS DIFERIDOS ETC.)': 'Línea de crédito',
 'TARJETA DE CREDITO EMPRESARIAL': 'Empresarial',
 'TARJETA DE CREDITO CORPORATIVA': 'Corporativa',
 'TARJETA DE CREDITO DISTRIBUCION/SUPLIDOR': 'Distribución',
 'TARJETA DE CREDITO EMPRESARIAL FLOTILLA': 'Empresarial Flota',
 'TARJETA DE CREDITO PERSONAL FLOTILLA': 'Personal Flota'
}

query = f"""
    select
        distinct lpad(a.entidad, 4, '0')
        -- a.marca||
        ||lpad(a.codigo, 6, '0')
        --||lpad(a.CLIENTEOBJ, 3, '0')||
                  ||CASE 
                  WHEN moneda = 'DOP' THEN '01'
                  WHEN moneda = 'USD' THEN '02'
                  end
                  unique_id
        , fecha
        , c.NOMBRE_CORTO eif
        , trim(b.DESCRIPCIO) marca
        , trim(e.DESCRIPCIO) producto
        , a.nombre nombre
        , d.DESCRIPCIO cliente
        , cargo
        , moneda
        , frecuencia
        --, formato_cargo
        , monto
        -- , porcentajes
        , porcentaje
        --, tasa_fija
        --, monto_fijo
        --, cargo_minimo
        --, cargo_maximo
        from fincomunes.tc1b a
        left join fincomunes.marcatarje b on a.marca = b.codigo
        left join fincomunes.REGISTRO_ENTIDADES c on c.CODIGOI = a.entidad
        left join CATEGORIAS_CLIENTES d on d.CODIGO = a.CLIENTEOBJ
        left join produservi e on e.CODIGO = a.tipoprod
        LEFT JOIN (
            SELECT
            ano||lpad(mes, 2, '0') fecha
            , e.CODIGO
            , i.conceptos cargo
            , e.monedaoper moneda
            , F.DESCRIPCION frecuencia
            , e.ENTIDAD entidad
            --, h.DESCRIPCIO formato_cargo
            ,CASE

                 WHEN h.DESCRIPCIO = 'Monto Fijo' THEN e.montofijo 
                 WHEN h.DESCRIPCIO = 'Escala de valores fijos' THEN e.LIMESCMAX
                 WHEN h.DESCRIPCIO = 'Porcentaje Limitado por monto fijo mínimo' THEN e.montofijo

            end monto
            ,e.porcentaje porcentaje
            --,CASE
              --          WHEN e.PORCENTAJE > 10 THEN e.PORCENTAJE/100/12
                --         WHEN h.DESCRIPCIO = 'Porcentaje' THEN e.PORCENTAJE/100
                  --       WHEN h.DESCRIPCIO = 'Porcentaje Limitado por monto fijo mínimo' THEN e.PORCENTAJE/100

            --end porcentajes
           -- , e.PORCENTAJE tasa_fija
           -- , e.montofijo monto_fijo
           -- , e.LIMESCMIN cargo_minimo
           -- , e.LIMESCMAX cargo_maximo
            FROM TC02 e
            left join t010 f on e.PERIODICID = f.codigo
            left join FORMATOS_COBRO h on e.formato = h.codigo
            left join MONITOREO.t_tabla_89 i on e.codigoconc = i.código
            where ano||lpad(mes, 2, '0') > '202307'
        ) g ON g.codigo||g.entidad = a.codigo||a.entidad
        where a.TIPOPAGO = 'TC' and CLIENTEOBJ in(101, 102)
        and a.ano||lpad(a.mes, 2, '0') = '202407' and NOMBRE_CORTO != 'ATLANTICO'
        and NOMBRE_CORTO IN ()
    """
df = query_reader(query, mode='all')
df.producto = df.producto.map(mapa_tarjetas)

def create_figure(data, title=None):
    fig = px.line(data)
    fig.update_layout(
        title=title,
        xaxis_title=None
    )
    plot(fig)


#%%
lista_bancos = ['POPULAR', 'BANRESERVAS']
periodo = '202307'
cargo = 'Costo de Carta de Saldo'
cargo = 'Cargo por Emisión De Principal'
query = f"""
select
        distinct lpad(a.entidad, 4, '0')
        -- a.marca||
        ||lpad(a.codigo, 6, '0')
        --||lpad(a.CLIENTEOBJ, 3, '0')||
--                   ||CASE 
--                   WHEN a.moneda = 'DOP' THEN '01'
--                   WHEN a.moneda = 'USD' THEN '02'
--                   end
                  unique_id
        , fecha
        , c.NOMBRE_CORTO eif
        --, trim(b.DESCRIPCIO) marca
        , trim(e.DESCRIPCIO) producto
--          , a.nombre nombre
        , d.DESCRIPCIO cliente
        , cargo
        , monto
    from tc1b a
    left join fincomunes.CATEGORIAS_CLIENTES d on d.CODIGO = a.CLIENTEOBJ
    left join REGISTRO_ENTIDADES c on c.CODIGOI = a.entidad
    left join fincomunes.PRODUSERVI E on E.CODIGO = a.TIPOPROD
        LEFT JOIN (
            SELECT
            ano||lpad(mes, 2, '0') fecha
            , e.CODIGO
            , i.conceptos cargo
            , e.monedaoper moneda
            , F.DESCRIPCION frecuencia
            , e.ENTIDAD entidad
            --, h.DESCRIPCIO formato_cargo
            ,CASE

                 WHEN h.DESCRIPCIO = 'Monto Fijo' THEN e.montofijo 
                 WHEN h.DESCRIPCIO = 'Escala de valores fijos' THEN e.LIMESCMAX
                 WHEN h.DESCRIPCIO = 'Porcentaje Limitado por monto fijo mínimo' THEN e.montofijo

            end monto
            ,e.porcentaje porcentaje
            --,CASE
              --          WHEN e.PORCENTAJE > 10 THEN e.PORCENTAJE/100/12
                --         WHEN h.DESCRIPCIO = 'Porcentaje' THEN e.PORCENTAJE/100
                  --       WHEN h.DESCRIPCIO = 'Porcentaje Limitado por monto fijo mínimo' THEN e.PORCENTAJE/100

            --end porcentajes
           -- , e.PORCENTAJE tasa_fija
           -- , e.montofijo monto_fijo
           -- , e.LIMESCMIN cargo_minimo
           -- , e.LIMESCMAX cargo_maximo
            FROM TC02 e
            left join t010 f on e.PERIODICID = f.codigo
            left join FORMATOS_COBRO h on e.formato = h.codigo
            left join MONITOREO.t_tabla_89 i on e.codigoconc = i.código
            where ano||lpad(mes, 2, '0') > '{periodo}'
        ) g ON g.codigo||g.entidad = a.codigo||a.entidad
-- where c.nombre_corto in ('{"', '".join(lista_bancos)}')
where
 cargo = '{cargo}' and d.codigo = 101
and trim(e.DESCRIPCIO) = 'TARJETA DE CREDITO PERSONAL CLASICA/STANDARD'
"""
lel = query_reader(query, mode='all')
evo = lel.groupby(['eif', 'fecha', 'cargo', 'producto'])['monto'].mean().reset_index()
#%%

# evo.loc[:, 'monto'] += np.random.normal(0, 1, size=len(evo))
evo = lel.groupby(['eif', 'fecha', 'cargo', 'producto'])['monto'].mean().reset_index()
if evo[evo.eif == 'BHD'].monto.mean() == evo[evo.eif == 'BANRESERVAS'].monto.mean():
    evo.loc[evo.eif == 'BHD', 'monto'] *= 1.01
fig = px.line(evo, x='fecha', y='monto', color='eif')
fig.update_layout(
    title=evo.cargo.unique()[0],
    xaxis_title=None
)
plot(fig)