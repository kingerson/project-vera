"""
Creado el 19/5/2022 a las 8:40 p. m.

@author: jacevedo
"""

import sql_tools


tarjetas_max_query = (
    " select "
    " max_fecha"
    ",llave"
    " from"
    "       ("
    "       select "
    "       to_date(ano || '-' || mes, 'YYYY-MM') max_fecha"
    "       ,entidad || codigo llave"
    "       ,ROW_NUMBER() OVER ("
    "           PARTITION BY entidad || codigo "
    "           ORDER BY to_date(ano || '-' || mes, 'YYYY-MM') DESC"
    "       ) dest_rank"
    "       from TC1B"
    "       where tipopago = 'TC'"
    "       and ano <> 0"
    ") "
    " where dest_rank = 1"
)

tasa_max_query = (
    " select "
    " max_fecha"
    ",llave"
    " from"
    "       ("
    "       select "
    "       to_date(ano || '-' || mes, 'YYYY-MM') max_fecha"
    "       ,codigo || entidad llave"
    "       ,ROW_NUMBER() OVER ("
    "           PARTITION BY codigo || entidad"
    "           ORDER BY to_date(ano || '-' || mes, 'YYYY-MM') DESC"
    "       ) dest_rank"
    "       from tc02"
    "       where ano <> 0"
    ") "
    " where dest_rank = 1"
)

query = (
    "select"
    " a.codigo"
    ",a.nombre"
    ",a.entidad"
    ",c.concepto"
    ",c.formato"
    ",c.moneda_operacion"
    ",c.moneda_pago"
    ",c.frecuencia"
    ",c.porcentaje"
    ",c.montofijo"
    ",c.valor_minimo_cargo"
    ",c.valor_maximo_cargo"
    " from ("
    "       select *"
    "       from TC1B a"
    "       right join ("
    f"       {tarjetas_max_query}"
    "       ) b on b.llave =  a.codigo || a.entidad"
    ") a"
    " left join ("
    "      select"
    "      a.codigo codigo_extra"
    "      ,trim(c.descripcio) concepto"
    "      ,a.formato"
    "      ,trim(a.monedaoper) moneda_operacion"
    "      ,trim(a.monedacob) moneda_pago"
    "      ,a.periodicid frecuencia"
    "      ,a.porcentaje"
    "      ,a.montofijo"
    "      ,a.limescmin valor_minimo_cargo"
    "      ,a.limescmax valor_maximo_cargo"
    "      ,a.entidad"
    "      ,b.max_fecha"
    "       from tc02 a"
    "       inner join"
    "             ("
    f"              {tasa_max_query}"
    "       ) b on "
    "           b.llave =  a.codigo || a.entidad"
    "           and to_date(a.ano || '-' || a.mes, 'YYYY-MM') = max_fecha"
    "       left join CONINCOCA c on a.CODIGOCONC = c.CODIGO"
    ") c on "
    "       a.codigo = c.codigo_extra"
    "       and a.entidad = c.entidad"
    "       and c.max_fecha = to_date(a.ano || '-' || a.mes, 'YYYY-MM')"
    "       where ano <> 0"
)

tarjeta_max_query = (
    " select "
    " max_fecha"
    ",llave"
    " from"
    "       ("
    "       select "
    "       to_date(ano || '-' || mes, 'YYYY-MM') max_fecha"
    "       ,codigo || entidad llave"
    "       ,ROW_NUMBER() OVER ("
    "           PARTITION BY codigo || entidad "
    "           ORDER BY to_date(ano || '-' || mes, 'YYYY-MM') DESC"
    "       ) dest_rank"
    "       from TC1B"
    "       where tipopago = 'TC'"
    ") "
    " where dest_rank = 1"
)

max_query = (
    " select "
    " max_fecha"
    ",llave"
    " from"
    "       ("
    "       select "
    "       to_date(ano || '-' || mes, 'YYYY-MM') max_fecha"
    "       ,codigo || entidad llave"
    "       ,ROW_NUMBER() OVER (PARTITION BY codigo || entidad ORDER BY to_date(ano || '-' || mes, 'YYYY-MM') DESC) dest_rank"
    "       from tc02"
    ") "
    " where dest_rank = 1"
)

query = (
    "select"
    " a.codigo"
    ",a.nombre"
    ",a.entidad"
    ",c.concepto"
    ",c.formato"
    ",c.moneda_operacion"
    ",c.moneda_pago"
    ",c.frecuencia"
    ",c.porcentaje"
    ",c.montofijo"
    ",c.valor_minimo_cargo"
    ",c.valor_maximo_cargo"
    " from ("
    "       select *"
    "       from TC1B a"
    "       right join ("
    f"       {tarjeta_max_query}"
    "       ) b on b.llave =  a.codigo || a.entidad"
    ") a"
    " left join ("
    "      select"
    "       a.codigo codigo_extra"
    "      ,trim(c.descripcio) concepto"
    "      ,a.formato"
    "      ,trim(a.monedaoper) moneda_operacion"
    "      ,trim(a.monedacob) moneda_pago"
    "      ,a.periodicid frecuencia"
    "      ,a.porcentaje"
    "      ,a.montofijo"
    "      ,a.limescmin valor_minimo_cargo"
    "      ,a.limescmax valor_maximo_cargo"
    "      ,a.entidad"
    "       ,b.max_fecha"
    "       from tc02 a"
    "       right join"
    "         ("
    f"          {max_query}"
    "       ) b on b.llave =  a.codigo || a.entidad and to_date(a.ano || '-' || a.mes, 'YYYY-MM') = max_fecha"
    "       left join CONINCOCA c on a.CODIGOCONC = c.CODIGO"
    ") c on "
    "       a.codigo = c.codigo_extra"
    "       and a.entidad = c.entidad"
    "       and c.max_fecha = to_date(a.ano || '-' || a.mes, 'YYYY-MM')"
)

def get_fees(mode='all'):
    try:
        tasas = sql_tools.query_reader(query, mode=mode, nrows=1000)
        return tasas
    except Exception as e:
        print(e)

#
# query = ('''select max(to_date(ano || '-' || mes, 'YYYY-MM')) max_fecha, entidad, codigo from tc02'''
#          # "       inner join"
#          #     "         ("
#          #     "             select max(to_date(ano || '-' || mes, 'YYYY-MM')) max_fecha"
#          #     "             from tc02"
#          #     "       ) b on to_date(a.ano || '-' || a.mes, 'YYYY-MM') = max_fecha"
#          "group by entidad and codigo"
#
#          " having entidad = 5 and codigo = 954"
#          )
# tarjetas = sql_tools.query_reader(query, mode='many')
# tarjetas