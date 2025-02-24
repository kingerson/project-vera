"""
Creado el 2/12/2022 a las 8:53 a. m.

@author: jacevedo
"""
import torch
import pandas as pd
import reclamos_reading
from datetime import date, timedelta

#%%
def standardizer(x):
    '''Funcion para estandarizar valores'''
    x_mean = x.mean()
    x_std = x.std()
    return (x - x_mean)/x_std, x_mean, x_std

#%%

def parse_data(df):
    '''Aplica transformaciones básicas'''
    df.eif = df.eif.str.lower()
    df.categoria = df.categoria.str.lower()
    df.reconsideracion = df.reconsideracion.astype(bool)
    df.respuesta_crm = df.respuesta_crm.str.lower()
    df.categoria_producto = df.categoria_producto.str.lower()
    df['monetaria'] = (df.monto_reclamado_dop.isna() & df.monto_reclamado_usd.isna())
    df['monto_reclamado_total'] = df.monto_reclamado_dop.fillna(0) + (df.monto_reclamado_usd.fillna(0) * 54)
    df['monto_estandar'], monto_mean, monto_std = standardizer(df.monto_reclamado_total.clip(upper=100000))
    df = df.loc[~df.reconsideracion, columns].copy()
    df['monetaria'] = df['monetaria'].astype(int)
    df = df.sample(frac=1)
    df = df.dropna(axis=0).copy()
    return df

def create_inputs(df):
    cols = features + ['monto_estandar']
    inputs = pd.get_dummies(df[features])
    inputs['monto_estandar'] = df['monto_estandar']
    inputs = inputs.reindex(columnas_features, axis=1).fillna(0)
    return inputs

def create_tensor(inputs):
    x = torch.tensor(list(inputs.values), dtype=torch.float, device=device)
    return x

def load_and_apply(x):
    model = torch.load('modelo_neural_duracion_reclamos.pt')
    pred = model(x)
    pred = (pred * duracion_std + duracion_mean)
    pred = pred.cpu().detach().numpy().round(0)
    return pred

#%%
def main():
    yesterday = date.today() - timedelta(1)
    df = reclamos_reading.main(yesterday.strftime('%Y-%m-%d'), date.today())
    df = parse_data(df)
    inputs = create_inputs(df)
    x = create_tensor(inputs)
    df['duracion_estimada'] = [f'{int(x)} días' for x in load_and_apply(x)]
    df.eif = df.eif.str.title()
    df.categoria = df.categoria.str.title()
    df.categoria_producto = df.categoria_producto.str.title()
    return df


#%%

features = ['eif', 'categoria', 'categoria_producto', 'monetaria']
quants = ['monto_estandar']
columns = ['codigo'] + features + quants
device = 'cuda:0'
duracion_std = 21.381679734133225
duracion_mean = 42.35021097046413

columnas_features = ['monetaria', 'eif_activo', 'eif_ademi', 'eif_adopem', 'eif_agricola',
       'eif_alaver', 'eif_apap', 'eif_atlantico', 'eif_bancamerica',
       'eif_banco bacc', 'eif_banesco', 'eif_banreservas', 'eif_bdi',
       'eif_bhd', 'eif_blh', 'eif_bonao', 'eif_caribe', 'eif_cibao',
       'eif_cofaci', 'eif_confisa', 'eif_data credito', 'eif_duarte',
       'eif_fihogar', 'eif_la nacional', 'eif_mocana', 'eif_monumental',
       'eif_motor credito', 'eif_norpresa', 'eif_optima', 'eif_peravia',
       'eif_popular', 'eif_promerica', 'eif_reidco', 'eif_remvimenca',
       'eif_romana', 'eif_santa cruz', 'eif_scotiabank', 'eif_trans union',
       'eif_vimenca', 'categoria_0.15%', 'categoria_beneficios',
       'categoria_bloqueos', 'categoria_buró de crédito', 'categoria_cajeros',
       'categoria_cancelaciones', 'categoria_cargos', 'categoria_consumos',
       'categoria_depositos', 'categoria_devolución', 'categoria_débitos',
       'categoria_error intereses', 'categoria_estados de cuenta',
       'categoria_otros', 'categoria_pagos',
       'categoria_producto no autorizado', 'categoria_préstamos',
       'categoria_publicidad engañosa', 'categoria_retiros',
       'categoria_transacciones', 'categoria_transferencias',
       'categoria_producto_c. ahorro', 'categoria_producto_c. corriente',
       'categoria_producto_c. nómina', 'categoria_producto_cert. financiero',
       'categoria_producto_cert. inversión', 'categoria_producto_cheque',
       'categoria_producto_otro', 'categoria_producto_p. comercial',
       'categoria_producto_p. hipotecario', 'categoria_producto_p. personal',
       'categoria_producto_p. vehicular', 'categoria_producto_pago impuestos',
       'categoria_producto_remesa', 'categoria_producto_t. crédito',
       'categoria_producto_t. débito', 'categoria_producto_transferencia',
       'monto_estandar']