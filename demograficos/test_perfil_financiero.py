"""
Creado el 22/8/2024 a las 1:03 PM

@author: jacevedo
"""
import pandas as pd
import requests as rs

base_url = 'http://sbs1srv358:9001/api/v1/'
detalles = 'detallesdeuda'
headers = {
    'accept': 'text/plain'
}
user_id = '001-1391792-6'
# url = 'http://sbs1srv358:9001/api/v1/report/getresume-creditconsult?identificationCard=001-1391792-6&month=1'

url = f'{base_url}/{detalles}/{user_id}/details/debt?year=2024&month=6&debtType=1'
response = rs.get(url, headers = headers)
response.status_code
data = response.json()
#%%

sum([f['feeAmount'] for f in data])

#%%

from sql_tools import query_reader, conn_creator
import pandas as pd
query = 'select * from USRPROUSUARIO.ID'
df = query_reader(query, mode='all')

#%%

def find_fee_debt(user_id):
    try:
        url = f'{base_url}/{detalles}/{user_id}/details/debt?year=2024&month=6&debtType=1'
        response = rs.get(url, headers = headers)
        result= sum([f['feeAmount'] for f in response.json()])
    except:
        result= None
    return result

#%%

df['fee_debt'] = None
batch_size = 10000

for x in range(0,len(df),batch_size):
    try:
        print(x, x+batch_size)
        df.loc[x:x+batch_size, 'score'] = df.loc[x:x+batch_size, 'cedula'].apply(find_fee_debt)
    except:
        print(f'it stopped at {x}')

#%%

# @custom_timer
def get_debt_details(user_id):
    tipos_deuda = [2,3,5]
    total_fee = 0
    # user_id = '001-1391792-6'
    for tipo in tipos_deuda:
        query = f"""
        begin
            declare @identification varchar(13) = '{user_id}'
            declare @debtType int = {tipo}
            declare @month    int = 5
            declare @year    int = 2024
            declare @result    varchar(25)
        exec
            @result = dbo.GetDebtDetails
            @identification, @debtType, @month, @year
        select @result as result
        end"""
    # query = f"EXEC GetDebtDetails @identification='{user_id+' '}', @debtType=1, @year=2024, @month=6"
        result = con.execute(query)
        # try:
        df = pd.DataFrame(data = result.fetchall(), columns = result.keys())
        fee = df.MONTOCUOTA.sum()
        # except:
        #     fee = 0
        total_fee += float(fee)
    return total_fee

#%%
from sql_tools import conn_creator


from general_tools import custom_timer
from timeit import default_timer as timer
#%%

#%%


tik = timer()
batch_size = 1000

for x in range(0,len(df),batch_size):
    tok = timer()
    try:
        print(x, x+batch_size)
        df.loc[x:x+batch_size, 'score'] = df.loc[x:x+batch_size, 'cedula'].apply(get_debt_details)
        print(f'{timer() - tik:.6f} segundos')
    except:
        print(f'it stopped at {x}')
        break
# lel = df.sample(10).cedula.apply(get_debt_details)
print(f'{timer() - tik:.6f} segundos')

#%%

con = conn_creator(creds='ms_sql')

con.close()

# lel = df.sample(100).cedula.apply(get_debt_details)

df['fee_debt'] = None
batch_size = 100


deudas = []
for user in df.cedula.sample(10):
    fee = get_debt_details(user)
    deudas.append(fee)



    tik = timer()

    # try:
    print(x, x+batch_size)
    df.loc[x:x+batch_size, 'fee_debt'] = df.loc[x:x+batch_size, 'cedula'].apply(get_debt_details)
    # except:
    #     print(f'it stopped at {x}')
    print(f'{timer() - tik:.6f} segundos')



#%%



# Connect to the database
con = conn_creator(creds='ms_sql')

# drop_table = """drop type if exists dbo.UserIDsType"""
#
# con.execute(drop_table)

create_type_table = """
CREATE TYPE UserIDsType AS TABLE (
    UserID varchar(15)
);"""

con.execute(create_type_table)

#%%

sql_command = """
DECLARE @UserIDs UserIDsType
INSERT INTO @UserIDs 
"""

for user_id in df.sample(10).cedula.values:
    sql_command += f"SELECT '{user_id}' UNION ALL "

sql_command = sql_command[:-11]

sql_command += "EXEC GetDebtDetails @UserIDs;"

# Execute the dynamic SQL
cursor = con.execute(sql_command)
results = cursor.fetchall()
results


#%%

con = conn_creator(creds='ms_sql')

# Start building the dynamic SQL command
sql_command = """
DECLARE @UserIDs UserIDsType;
"""

# id_list = ','.join([str(id) for id in df.sample(10).cedula.values])

# Add INSERT statements for each user ID to the command
for user_id in df.sample(10).cedula.values:
    sql_command += f"INSERT INTO @UserIDs (UserID) VALUES ({user_id});\n"
    #sql_command += f"INSERT INTO @UserIDs (UserID) VALUES ({id_list});\n"

# Add the EXEC statement to run the stored procedure
sql_command += "EXEC GetUserDetails @UserIDs go;"

# Execute the dynamic SQL
cursor = con.execute(sql_command)
# results = cursor.fetchall()
#
# # Print results
# for row in results:
#     print(row)
#
# # Clean up
# cursor.close()
# con.close()

#%%

query = "select * from UserIDsType"
query_reader(query)


#%%
import pandas as pd

#%%
con = conn_creator(creds='ms_sql')
# DataFrame to store results
results_df = pd.DataFrame()

# Iterate over the Series and execute the stored procedure for each user
fees = []
tipos_deuda = [2,3,5]

for user_id in df.cedula.values:
    total_fee = 0
    for tipo in tipos_deuda:
        query = f"""
        begin
            declare @identification varchar(15) = '{user_id} '
            declare @debtType int = {tipo}
            declare @month    int = 5
            declare @year    int = 2024
            declare @result    varchar(25)
        exec
            @result = dbo.GetDebtDetails
            @identification, @debtType, @month, @year
        select @result as result
        end"""
        # query = f"EXEC GetDebtDetails @identification='{user_id+' '}', @debtType=1, @year=2024, @month=6"
        result = con.execute(query)
        try:
            debt = pd.DataFrame(data=result.fetchall(), columns=result.keys())
            fee = debt.MONTOCUOTA.sum()
        except:
            fee = 0
        total_fee += float(fee)
    fees.append(total_fee)


# con.close()
fees

#%%

for user_id in df.cedula.values:
    total_fee = 0
    for tipo in tipos_deuda:
        query = f"""
        begin
            declare @identification varchar(15) = '{user_id} '
            declare @debtType int = {tipo}
            declare @month    int = 5
            declare @year    int = 2024
            declare @result    varchar(25)
        exec
            @result = dbo.GetDebtDetails
            @identification, @debtType, @month, @year
        select @result as result
        end"""
        # query = f"EXEC GetDebtDetails @identification='{user_id+' '}', @debtType=1, @year=2024, @month=6"
        result = con.execute(query)
        try:
            debt = pd.DataFrame(data=result.fetchall(), columns=result.keys())
            fee = debt.MONTOCUOTA.sum()
        except:
            fee = 0
        total_fee += float(fee)
    fees.append(total_fee)

#%%

query = """
SELECT  'T' as 'TIPOCREDITO',t.IDCREDITO,e.ABRINT as 'Nombre_Entidad',e.nomint as 'Nombre_Entidad_largo',e.codigoi as 'Codigo_entidad',t.IDPERSONA,t.FACILIDADCREDITICIA,t.CALIFICACION,t.MONTOCUOTA
			,t.CAPITAL,(t.CAPITAL + t.RENDIMIENTOS) as TotalDeuda, (t.CAPITAL0_30+t.RENDIMIENTOS0_30) AS VIGENTES,t.CONSUMOMES as ConsumoMes,
			t.FECHAAPROBADO, t.MAYORDIAATRASO,CASE t.TIPOMONEDA WHEN 'N' THEN 'NACIONAL' WHEN 'E' THEN 'EXTRANJERA' END AS TIPOMONEDA,t.TIPOMONEDA as TIPOMONEDASIGLA,
			t.MONTOAPROBADO as 'LIMITE_CREDITO',T.RENDIMIENTOS,
			(t.CAPITAL31_90+t.CAPITALMAS_90+t.RENDIMIENTOS31_90+t.RENDIMIENTOSMAS_90) AS VENCIDOS, t.FECHAACTIVACION as 'FechaActivacion',
			CASE t.FINANCIA WHEN 'N' THEN 'NO' WHEN 'S' THEN 'SI' END AS FINANCIA,t.TASADEINTERES,
			CASE t.COBRANZA WHEN 'N' THEN 'NO' WHEN 'S' THEN 'SI' END AS COBRANZA,
			BALANCE_CORTE, FECHA_VENCIMIENTO, INTERESES_CORTE, COMISION_CARGO_CORTE
			FROM CR_HISTORIA_CREDITOS_TARJETA  t
			--join sdmaint e on t.ENTIDAD = e.codigoi
			join sdmaint e on t.ENTIDAD = e.codigoi
			--where t.TIPOCREDITO = 'T' and t.IDPERSONA = '001-1391792-6' and t.ANO*100+t.mes = '202406' 
		    where ((CONTINGENCIA > 0) OR (CAPITAL+RENDIMIENTOS>=500) OR ((CONTINGENCIA > 0) AND ((CAPITAL=0) AND (RENDIMIENTOS=0))))
"""

creditos = query_reader(query, mode='all', creds='ms_sql')

#%%

query = """
select a.cedula, avg(CONSUMOSMES) from USRPROUSUARIO.ID a
left join FINCOMUNES.RCC_RC03 b on b.IDENTIFICACIONDEUDOR = a.CEDULA
where b.ano*100+b.mes between 202307 and 202406
group by a.cedula, b.ano*100+b.mes
"""

tarjetas = query_reader(query, mode='all')
tarjetas

#%%

from sql_tools import query_reader
query = """
select
    EducationLevel nivel_educativo
    , IncomeSource fuente_ingesos
    , MonthlyIncome ingresos_mensuales
    , AnotherDebts otras_deudas
from
    UserInfo
where
    (EducationLevelText is not null or IncomeSourceText is not null)
and MonthlyIncome > 0
"""

result = query_reader(query, creds='azure', mode='all')

#%%


query = """
select cedula, sum(consumos)/count(fecha) consumo_mensual
from (
select IDENTIFICACIONDEUDOR cedula
,CONSUMOSMES consumos
,b.ano||b.mes fecha
from IDV2 a
left join FINCOMUNES.rcc_rc03 b on b.IDENTIFICACIONDEUDOR = a.CEDULA
where ano = 2024
)
group by cedula
"""
df = query_reader(query, mode='all')
tarjetas = df.copy()

#%%

query = """
select cedula, sum(monto_cuota)/count(fecha) cuota_mensual
from (
select IDENTIFICACIONDEUDOR cedula
,MONTOCUOTA monto_cuota
,b.ano||b.mes fecha
from IDV2 a
left join FINCOMUNES.rcc_rc01 b on b.IDENTIFICACIONDEUDOR = a.CEDULA
where ano = 2024
)
group by cedula
"""
cuotas = query_reader(query, mode='all')
cuotas

#%%

query = """
select 
cedula
, genero
from IDV2
"""
usuarios = query_reader(query, mode='all')
usuarios

#%%

data = pd.merge(usuarios, tarjetas, on='cedula', how='left')
data = pd.merge(data, cuotas, on='cedula', how='left')
data

#%%

data = pd.merge(df, tarjetas, on='cedula', how='left')
data = pd.merge(data, cuotas, on='cedula', how='left')
data

#%%

data['deuda_mensual_promedio'] = data.otras_deudas.fillna(0) + data.consumo_mensual.fillna(0) + data.cuota_mensual.fillna(0)
data.deuda_mensual_promedio = data.deuda_mensual_promedio.astype(float).round(2)
data.deuda_mensual_promedio
data['nivel_deuda'] = abs(data.deuda_mensual_promedio) / (abs(data.ingresos)+1)
data.nivel_deuda = data.nivel_deuda.round(4)
data.nivel_deuda.dropna().describe()
data.nivel_deuda.clip(upper=10).value_counts(bins=range(0,101,10)).sort_index()
#%%
max_val = 100000
step = 10000
data.nivel_deuda.clip(upper=max_val).value_counts(bins=10).sort_index()
#%%

(data.ingresos > 1000000).value_counts()
(abs(data.ingresos) < 1000).value_counts()
data[abs(data.ingresos) < 1000].ingresos.abs().describe(percentiles=[0.25,0.5,0.7,0.8,0.9,0.95,0.99,0.999])
(data.deuda_mensual_promedio > 1000000).value_counts()

#%%
from sklearn.cluster import KMeans
clusters = 10
km = KMeans(n_clusters=clusters, random_state=0)


#%%

# results = km.fit_transform(data[['nivel_deuda']])
results = km.fit_predict(data[['nivel_deuda']])
pd.DataFrame(results).sum().apply(lambda x: f'{x:,.2f}')
pd.DataFrame(results).count().apply(lambda x: f'{x:,.2f}')
#%%
data['grupo'] = pd.Series(results).astype(str)

#%%

import plotly.express as px
from plotly.offline import plot
#%%
# fig_data = abs(data[['deuda_mensual_promedio', 'ingresos']].clip(upper=1000000))
# fig_data = abs(data[['deuda_mensual_promedio', 'ingresos']])
fig_data = data.loc[abs(data['deuda_mensual_promedio']<=1000000) & abs(data['ingresos']<=1000000)].copy()
fig_data['deuda_mensual_promedio'] = abs(fig_data['deuda_mensual_promedio'])
fig_data['ingresos'] = abs(fig_data['ingresos'])
fig = px.scatter(fig_data, x='ingresos',
                 y='deuda_mensual_promedio', template='presentation'
                 , color_discrete_map='T10')
plot(fig)

