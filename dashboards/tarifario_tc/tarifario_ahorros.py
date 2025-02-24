import pandas as pd
from sql_tools import query_reader
#%%

query = """
-- TARIFARIO directo cuentas de ahorro
select
    distinct lpad(a.entidad, 4, '0')||lpad(a.codigo, 6, '0')||codigo_moneda unique_id
    , fecha
    , c.NOMBRE_CORTO eif
    , trim(b.DESCRIPCIO) marca
    , trim(e.DESCRIPCIO) producto
    , a.nombre nombre
    , d.DESCRIPCIO cliente
    , cargo
    , formato_cargo
    , frecuencia
    , monto_fijo
    , minimo
    , maximo
    , porcentaje
from fincomunes.tc1b a
left join fincomunes.marcatarje b on a.marca = b.codigo
left join fincomunes.REGISTRO_ENTIDADES c on c.CODIGOI = a.entidad
left join CATEGORIAS_CLIENTES d on d.CODIGO = a.CLIENTEOBJ
left join produservi e on e.CODIGO = a.tipoprod
LEFT JOIN (
    SELECT
     e.entidad
    , e.codigo
    , ano||lpad(mes, 2, '0') fecha
    , i.conceptos cargo
    , h.DESCRIPCIO formato_cargo
    , F.DESCRIPCION frecuencia
    , e.monedaoper moneda
    , e.montofijo monto_fijo
    , e.LIMESCMIN minimo
    , e.LIMESCMAX maximo
    ,e.porcentaje porcentaje
    , CASE
              WHEN monedaoper = 'DOP' THEN '01'
              WHEN monedaoper = 'USD' THEN '02'
    end codigo_moneda
    FROM TC02 e
    left join t010 f on e.PERIODICID = f.codigo
    left join FORMATOS_COBRO h on e.formato = h.codigo
    left join MONITOREO.t_tabla_89 i on e.codigoconc = i.código
    where ano||lpad(mes, 2, '0') = '202407'
) g ON g.codigo||g.entidad = a.codigo||a.entidad
where a.ano||lpad(a.mes, 2, '0') = '202404' and NOMBRE_CORTO != 'ATLANTICO'
and e.DESCRIPCIO like '%AHORRO%' and moneda = 'DOP'
"""

df = query_reader(query, mode='all')
df.T
df.eif.unique()

#%%

['unique_id', 'fecha', 'eif', 'marca', 'producto', 'nombre', 'cliente',
       'cargo', 'moneda', 'formato_cargo', 'frecuencia', 'monto_fijo',
       'minimo', 'maximo', 'porcentaje']

#%%

index_cols = ['unique_id', 'fecha', 'eif', 'marca', 'producto', 'nombre', 'cliente']
val_cols = ['monto_fijo', 'minimo', 'maximo', 'porcentaje']
df.pivot_table(index=index_cols, columns='cargo', values='monto_fijo')