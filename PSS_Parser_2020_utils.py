# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 19:42:14 2020
args:
column_name -> nombre de la columna de la cual se quiere recuperar el valor de la celda
index -> indice de la fila de la cual se quiere recuperar el valor de la celda
row -> fila del dataframe
df -> dataframe que contiene todos los datos

La funcion recupera el valor de la celda y lo devuelve. Si la celda es null, 
recupera el valor de la celda anterior en el df y devuelve hacia atrás el primer 
valor que no sea nulo.

@author: Tincho
"""

def fill_cell_nonNan_Value(column_name,index,row,df):
    import pandas as pd
    cell_value = 'NOVALUE'
    columnas = set(df.columns.values)
    try:
        if column_name in columnas:
            cell_value = row[column_name]
            while(cell_value == '' or pd.isnull(cell_value) ):
                cell_value = df.loc[index-1,column_name]
                index -= 1
        else:
            raise Exception ("Nombre de columna ", column_name ," no esta entre las columnas del parametro row")
    except Exception as e:
        print (e)
    finally:
        return cell_value