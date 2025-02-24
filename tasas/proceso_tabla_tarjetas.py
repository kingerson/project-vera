"""
Creado el 19/5/2022 a las 2:59 p. m.

@author: jacevedo
"""

import sql_tools


max_query = (
    " select "
    " max_fecha"
    ",entidad" 
    ",codigo"
    " from"
    "       ("
    "       select "
    "       to_date(ano || '-' || mes, 'YYYY-MM') max_fecha"
    "       ,entidad, codigo"
    "       ,ROW_NUMBER() OVER ("
    "           PARTITION BY entidad, codigo "
    "           ORDER BY to_date(ano || '-' || mes, 'YYYY-MM') DESC"
    "       ) dest_rank"
    "       from TC1B"
    "       where tipopago = 'TC'"
    ") "
    " where dest_rank = 1"
)

query = (
        "select"
        " LPAD(a.entidad, 3, '0') || '-' || LPAD(a.codigo, 6, '0') llave"
        ",a.nombre nombre_tarjeta"
        ",trim(c.descripcio) marca_tarjeta"
        ",trim(d.nombre_corto) entidad"
        ",trim(e.descripcio) tipo_tarjeta"
        ",a.clienteobj tipo_cliente "
        # ",a.tipopago tipo_pago"
        # ",b.max_fecha"
        " from TC1B a"
        # " right join ("
        # f"            {max_query}"
        # ") b on a.codigo = b.codigo and a.entidad = b.entidad"
        " inner join"
        "   ("
        "   select max(to_date(ano || '-' || mes, 'YYYY-MM')) max_date"
        "   from tc1b"
        " ) b on to_date(a.ano || '-' || a.mes, 'YYYY-MM') = b.max_date"
        # " and to_date(a.ano || '-' || a.mes, 'YYYY-MM') = b.max_fecha"
        " left join MARCATARJE c on c.codigo = a.marca"
        " left join registro_entidades d on a.entidad = d.codigoi"
        " left join  PRODUSERVI E ON A.TIPOPROD = E.CODIGO"
        " where a.tipopago = 'TC'"
)


def get_cards():
    try:
        tarjetas = sql_tools.query_reader(query, mode='all')
        clientes = {
            '101': "Cliente Normal",
            '102': "Cliente Preferencial",
            '201': "Empleado de la entidad",
            '301': "Relacionado de la entidad"
        }
        tarjetas['tipo_cliente'] = tarjetas['tipo_cliente'].map(clientes)
        return tarjetas
    except Exception as e:
        print(e)
