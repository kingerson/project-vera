"""
Creado el 27/5/2022 a las 12:03 p. m.

@author: jacevedo
# """
import exporta_viafirma
import procesa_viafirma

print('inicio exportacion')
df = exporta_viafirma.main()
print('exporto firmas')
print(df.head().T)
print('inicia actualizacion base de datos')
procesa_viafirma.main(df)
print('termino actualizacion')