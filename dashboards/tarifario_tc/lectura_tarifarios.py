"""
Creado el 4/9/2024 a las 3:44 PM

@author: jacevedo
"""

from sql_tools import query_reader
import pandas as pd


mapa_tarjetas = {
 'TARJETA DE CREDITO PERSONAL PLATINO/PLATINUM (O SUPERIOR)': 'Platinum o superior',
 'TARJETA DE CREDITO PERSONAL CLASICA/STANDARD': 'Clásica/Standard',
 'TARJETA DE CREDITO PERSONAL ORO/GOLD': 'Oro/Gold',
 'PRÉSTAMOS A TRAVÉS DE LÍNEAS DE CRÉDITO PERSONALES (CRÉDITOS DIFERIDOS ETC.)': 'Línea de crédito',
 'TARJETA DE CREDITO EMPRESARIAL': 'Empresarial',
 'TARJETA DE CREDITO CORPORATIVA': 'Corporativa',
 'TARJETA DE CREDITO DISTRIBUCION/SUPLIDOR': 'Distribución',
 'TARJETA DE CREDITO EMPRESARIAL FLOTILLA': 'Empresarial Flota',
 'TARJETA DE CREDITO PERSONAL FLOTILLA': 'Personal Flota'
}

mapa_nombres = {
 'Cl¿Sica Local': 'Clásica Local',
 'Supercr¿Dito Cl¿Sica': 'Supercrédito Clásica',
 'Pagatodo Cl¿Sica': 'Pagatodo Clásica',
 'Petroleo Caribe¿O': 'Petroleo Caribeño',
 'Tarjeta American Caribeño Membership Rewards': 'American Express® Membership Rewards®',
 'Tarjeta American Express¿ Gold Membership Rewards¿': 'American Express® Gold Membership Rewards®',
 'Tarjeta Casa De Campo American Express¿ Platinum Membership Rewards¿': 'Casa De Campo American Express® Platinum Membership Rewards®',
 'Supercr¿Dito Gold': 'Supercrédito Gold',
 'Benacerh Cl¿Sica Internacional': 'Benacerh Clásica Internacional',
 'Tarjetas De Cr¿Dito Personales De Alto L¿Mite Platino Infinity Etc.': 'TC Personales De Alto Límite Platino Infinity Etc.',
 'American Express ¿ Business Membership Rewards ¿': 'American Express® Business Membership Rewards®',
 'Gold Casa De Espa¿A': 'Gold Casa De España',
 'Tarjetas De Cr¿Dito Personales De Mediano L¿Mite Oro Gold': 'TC Personales De Mediano Límite Oro Gold',
 'Tarjeta De Cr¿Dito Carrefour American Express¿': 'Carrefour American Express®',
 'American Express ¿ Business Distribucion Virtual': 'American Express® Business Distribucion Virtual',
 'Tarjeta De Cr¿Dito American Express¿ Membership Rewards¿': 'American Express® Membership Rewards®',
 'The Platinum Card¿ American Express¿ Membership Rewards¿': 'The Platinum Card® American Express® Membership Rewards®',
 'Manuel Arsenio Ure¿A': 'Manuel Arsenio Ureña',
 'Tarjeta De Cr¿Dito Suma Ccn American Express¿': 'Suma CCN American Express®',
 'American Express ¿ Business Gasolina': 'American Express® Business Gasolina',
 'Tarjetas De Cr¿Dito Personales De Peque¿O L¿Mite Cl¿Sica Standard': 'TC Personales De Pequeño Límite Clásica Standard',
 'Tarjeta American Express¿ Membership Rewards': 'American Express® Membership Rewards®'
}
def old():
    query = """
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
        left join fincomunes.CATEGORIAS_CLIENTES d on d.CODIGO = a.CLIENTEOBJ
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
            where ano||lpad(mes, 2, '0') = '202407'
        ) g ON g.codigo||g.entidad = a.codigo||a.entidad
        where a.TIPOPAGO = 'TC' and CLIENTEOBJ in(101, 102)
        and a.ano||lpad(a.mes, 2, '0') = '202407' and NOMBRE_CORTO != 'ATLANTICO'

    """
    df = query_reader(query, mode='all')
    df.producto = df.producto.map(mapa_tarjetas)
    return df

def new():
    query = """
    select
    distinct lpad(a.entidad, 4, '0')||lpad(a.codigo, 6, '0')||codigo_moneda unique_id
    , fecha
    , c.NOMBRE_CORTO eif
    , trim(b.DESCRIPCIO) marca
    , trim(e.DESCRIPCIO) producto
    , a.nombre nombre
    , trim(d.DESCRIPCIO) cliente
    , cargo
    , moneda
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
    where ano||lpad(mes, 2, '0') = '202407' and e.formato NOT IN ('P2', 'P3', 'F2', 'E1')
) g ON g.codigo||g.entidad = a.codigo||a.entidad
where a.TIPOPAGO = 'TC' and CLIENTEOBJ in(101, 102)
and a.ano||lpad(a.mes, 2, '0') = '202407' and NOMBRE_CORTO != 'ATLANTICO'
    """
    df = query_reader(query, mode='all')
    # columns = ['eif', 'marca', 'producto', 'nombre', 'moneda', 'formato_cargo', 'frecuencia', 'cargo']
    columns = ['eif', 'marca', 'producto', 'nombre', 'moneda', 'formato_cargo', 'cargo']
    # columns = ['eif', 'marca', 'producto', 'nombre', 'moneda', 'cargo']
    grupo_porcentaje = df.groupby(columns)['porcentaje'].max()
    grupo_monto = df.groupby(columns)['monto_fijo'].max()
    grupo_minimo = df.groupby(columns)['minimo'].max()
    grupo_maximo = df.groupby(columns)['maximo'].max()

    df = pd.concat([grupo_porcentaje, grupo_monto, grupo_minimo, grupo_maximo], axis=1).reset_index()
    df['producto_fixed'] = df.producto.map(mapa_tarjetas)
    df['nombre_fixed'] = df.nombre.str.title()
    df['nombre_fixed'] = df['nombre_fixed'].replace(mapa_nombres)
    df['marca_fixed'] = df.marca.str.replace('Marca Propia (Exclusiva de la Entidad)', 'Marca Propia')
    return df