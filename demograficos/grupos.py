"""
Creado el 14/8/2024 a las 2:31 PM

@author: jacevedo
"""

import pandas as pd
from sql_tools import query_reader

#%%

query = """
select * from (
select name, email
    , count(distinct prestamos) cantidad_prestamos
      from ID
      inner join
           (select IDENTIFICACIONDEUDOR, CODIGOCREDITO || entidad || TIPOMONEDA prestamos
            from FINCOMUNES.RCC_RC01
            where ano = 2024 and CODIGOPRODUCTOSERVICIO in (181,182,183,184,185,186,187,188)) b on b.IDENTIFICACIONDEUDOR = cedula
      group by name, email
      )
"""
prestamos = query_reader(query, mode='all')

#%%


query = """
select name, email
    , count(distinct prestamos) cantidad_tarjetas
      from ID
      inner join
           (select IDENTIFICACIONDEUDOR, CODIGOCREDITO || entidad || TIPOMONEDACREDITO prestamos
            from FINCOMUNES.RCC_RC03
            where ano = 2024) b on b.IDENTIFICACIONDEUDOR = cedula
      group by name, email
"""
tarjetas = query_reader(query, mode='all')

mezcla = pd.merge(prestamos, tarjetas, on=['name','email'])

mezcla['total_creditos'] = mezcla.cantidad_tarjetas + mezcla.cantidad_prestamos

#%%
from general_tools import excel_formatter

RESULT_FILENAME = 'Usuarios por +4 créditos Ene-Jul 2024.xlsx'
with pd.ExcelWriter(RESULT_FILENAME) as writer:
    excel_formatter(writer, mezcla.loc[mezcla.total_creditos > 4], 'Usuarios')

#%%

query = """
select name, email, cedula from id
"""
usuarios =query_reader(query, mode='all')

#%%

sin_creditos = usuarios[~usuarios.email.isin(mezcla.email)]

#%%

query = """
select * from (
select name, email
    , count(distinct prestamos) cantidad_prestamos
      from ID
      inner join
           (select IDENTIFICACIONDEUDOR, CODIGOCREDITO || entidad || TIPOMONEDA prestamos
            from FINCOMUNES.RCC_RC01
            where ano = 2024 and CODIGOPRODUCTOSERVICIO in (181,182,183,184,185,186,187,188)) b on b.IDENTIFICACIONDEUDOR = cedula
      group by name, email
      )
"""
hipotecarios = query_reader(query, mode='all')

#%%

con_inactivas = usuarios[usuarios.cedula.isin(inactivas.documento_persona)]
cantidad_inactivas = inactivas[inactivas.documento_persona.isin(usuarios.cedula)].documento_persona.value_counts().rename('cantidad_cuentas').reset_index()
con_inactivas = pd.merge(con_inactivas, cantidad_inactivas, left_on='cedula', right_on='documento_persona', how='left')
con_inactivas

#%%

RESULT_FILENAME = 'Grupos demograficos.xlsx'
with pd.ExcelWriter(RESULT_FILENAME) as writer:
    excel_formatter(writer, mezcla.loc[mezcla.total_creditos > 4], 'Con mas 4 creditos')
    excel_formatter(writer, sin_creditos, 'Sin creditos')
    excel_formatter(writer, hipotecarios, 'Con creditos hipotecarios')
    excel_formatter(writer, con_inactivas, 'Cuentas inactivas-abandonadas')