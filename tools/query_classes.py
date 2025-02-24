class ca02_conteo_historico:
    def __init__(self, entidad_inicial):
        self.query = f'''
        SELECT * 
        FROM
        (
            SELECT /*+NOPARALLEL */
                a.periodo
                , count(a.codinstrum) cantidad
            FROM 
                CA02 A
                , REGISTRO_ENTIDADES B
            WHERE
                A.entidad = b.codigoi
                AND b.nombre_corto = '{entidad_inicial}'
            GROUP BY
                A.periodo
        )'''

class codigo_entidad:
      def __init__(self, entidad):
        self.query = f'''
        SELECT codigoi
        FROM registro_entidades
        WHERE nombre_corto = '{entidad}'
        '''

class ca02_period_data:
    def __init__(self, period):
        self.query = f'''
        SELECT * 
        FROM (
            SELECT /*+NOPARALLEL */
                a.entidad codigo_entidad,
                b.razon_social razon_social,
                b.nombre_corto nombre_corto,
                e.descripcio tipo_entidad,
                a.tipcliente tipo_cliente,
                c.tipidenti tipo_documento,
                a.idcliente documento_persona,
                c.descrip tipo_persona,
                a.direccion,
                A.nombre,
                A.apellidos,
                a.estatus,
                a.montocapi monto,
                a.periodo,
                a.tipomoneda tipo_moneda,
                a.codinstrum codigo_instrumento,
                a.tipoinstru tipo_instrumento,
                d.descripcio descripcion_producto,
                a.fe_emision fecha_apertura,
                a.fe_ultmovi fecha_ultimo_movimiento
            FROM 
                ca02 a
                , registro_entidades b
                , tipodeu c
                , produservi d
                , nuevotipoentidad e
            WHERE
                a.entidad = b.codigoi
                AND a.tipcliente = c.tipo
                AND a.tipoinstru = TO_CHAR(d.codigo)
                AND b.tipo_entidad = e.codigo
                AND a.periodo = TO_DATE('{period}', 'yyyy/mm/dd')
            )'''

class ca02_abandonadas:
    def __init__(self):
        self.query = f'''
        SELECT * 
        FROM (
            SELECT /*+NOPARALLEL */
                a.entidad codigo_entidad,
                b.razon_social razon_social,
                b.nombre_corto nombre_corto,
                e.descripcio tipo_entidad,
                a.tipcliente tipo_cliente,
                c.tipidenti tipo_documento,
                a.idcliente documento_persona,
                c.descrip tipo_persona,
                a.direccion,
                A.nombre,
                A.apellidos,
                a.estatus,
                a.montocapi monto,
                a.periodo,
                substr(a.ctacapital, 8,1) tipo_moneda,
                a.codinstrum codigo_instrumento,
                a.tipoinstru tipo_instrumento,
                d.descripcio descripcion_producto,
                a.fe_emision fecha_apertura,
                a.fe_ultmovi fecha_ultimo_movimiento
            FROM 
                ca02 a
                , registro_entidades b
                , tipodeu c
                , produservi d
                , nuevotipoentidad e
            WHERE
                a.entidad = b.codigoi
                AND a.tipcliente = c.tipo
                AND a.tipoinstru = TO_CHAR(d.codigo)
                AND b.tipo_entidad = e.codigo
                AND A.estatus = 'A'
                AND a.periodo < TO_DATE('2021/06/30', 'yyyy/mm/dd')
            )'''

class lectura_pu01:
    def __init__(self, period):
        self.query = f'''
        SELECT * 
        FROM (
            SELECT /*+NOPARALLEL */
                a.entidad codigo_entidad,
                b.razon_social razon_social,
                b.nombre_corto nombre_corto,
                e.descripcio tipo_entidad,
                a.tipcliente tipo_cliente,
                c.tipidenti tipo_documento,
                a.idcliente documento_persona,
                c.descrip tipo_persona,
                a.direccion,
                a.nombre || ' ' || a.apellidos nombre_persona,
                a.estatus,
                a.montocapi monto,
                a.periodo,
                a.tipomoneda tipo_moneda,
                a.codinstrum codigo_instrumento,
                a.tipoinstru tipo_instrumento,
                d.descripcio descripcion_producto,
                a.fe_emision fecha_apertura,
                a.fe_ultmovi fecha_ultimo_movimiento
            FROM 
                ca02 a
                , registro_entidades b
                , tipodeu c
                , produservi d
                , nuevotipoentidad e
            WHERE
                a.entidad = b.codigoi
                AND a.tipcliente = c.tipo
                AND a.tipoinstru = TO_CHAR(d.codigo)
                AND b.tipo_entidad = e.codigo
                AND a.periodo = TO_DATE('{period}', 'yyyy/mm/dd')
            )'''
