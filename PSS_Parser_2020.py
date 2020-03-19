# -*- coding: utf-8 -*-
"""
Prueba experimental para parsear archivos de prestaciones
By Tincho

Requisitos de entrada
1. El archivo de prestaciones hay que separarlo en hojas con los subgrupos
2. La primer fila son los encabezados del archivo
3. Encabezados MINIMOS del Archivo de entrada (Todos en mayusculas):
    'LÍNEA DE CUIDADO'
    'TIPO DE PRESTACIÓN'
    'NOMBRE DE LA PRESTACIÓN'
    'CÓDIGO'
    'PRECIO'
4. Si el archivo incluye otros encabezados por el momento se ignoran
5. IMPORTANTE: hay que asegurarse que codigos y diagnosticos esten todos en la misma celda


TODO:
    1.if excel_data_df.head().contains('CODIGO') CONTROLAR QUE EXISTE EL ENCABEZADO CODIGO y que la primera
    line de la hoja sean los nombres de columna
    2.Pasar todos los encabezados a mayusculas
    3.Controlar Acentos. PUEDEN TENER ACENTOS, Menos CODIGO que debe venir sin ACENTO
    4.Eliminar los archivos si existen
    5.Parametrizar y crear una funcion que acepte como entrada el nombre del archivo, la hoja, y el nombre de salida

DESEABLE:
    Funcion para detectar si el archivo cumple con el formato

"""

import pandas as pd
import PSS_Parser_2020_utils as pss_utils

columnas_req = ('LÍNEA DE CUIDADO','TIPO DE PRESTACIÓN','NOMBRE DE LA PRESTACIÓN','CÓDIGO','PRECIO')
input_filepath = 'C:/Users/Tincho/Documents/PSS To Json/DatosExcel/Entrada/GrupoEmbarazo.xlsx'

try:
    
    xl = pd.ExcelFile(input_filepath)
    hojas = xl.sheet_names
    
    for hoja in hojas:
    
        #cargamos el archivo en un dataframe
        output_filepath ='C:/Users/Tincho/Documents/PSS To Json/DatosExcel/Salida/' + hoja + '_Limpio.xlsx'
        excel_data_df = pd.read_excel(input_filepath, sheet_name = hoja)
        
        
        #LIMPIAMOS CELDAS y COLUMNAS VACIAS
        
        excel_data_df = excel_data_df.loc[:, ~excel_data_df.columns.str.contains('^Unnamed')]
        
        col_archivo = tuple(excel_data_df.columns.values)    
        if set(columnas_req).issubset(col_archivo) == False:
            raise Exception ('Estructura de archivo incorrecta', hoja, columnas_req.difference(col_archivo))
        else:   
            #Removemos los acentos
            excel_data_df.rename(columns={ 'LÍNEA DE CUIDADO': 'LINEA DE CUIDADO',
                                           'TIPO DE PRESTACIÓN': 'TIPO DE PRESTACION',
                                           'NOMBRE DE LA PRESTACIÓN': 'NOMBRE DE LA PRESTACION',
                                           'CÓDIGO':'CODIGO',
                                           'PRECIO':'PRECIO'
                                         },   inplace=True
            )
            
            #Filtramos todos los diagnosticos que estan listados con separadores en una sola celda
            excel_data_df_diag = excel_data_df.loc[excel_data_df['CODIGO'].str.contains("-| |,")==True]  
            
            for i,row in excel_data_df_diag.iterrows():
                objeto_diagnostico = row["CODIGO"].replace('-',' ').replace(',',' ').replace('(',' ').replace('*',' ').replace(')',' ').strip().split(' ')
                objeto = objeto_diagnostico[0][:6]
                
                if len(objeto_diagnostico[0])>6:
                    objeto_diagnostico.append(objeto_diagnostico[0][6:])
                    
                objeto_diagnostico.pop(0)
                objeto_diagnostico = list(filter(None, objeto_diagnostico))
                
                for x,codigo in enumerate(objeto_diagnostico):
                    if codigo:
                        objeto_diagnostico[x] = objeto + codigo
                
                for y,codigo_concatenado in enumerate(objeto_diagnostico):
                                       
                    linea_de_cuidado = pss_utils.fill_cell_nonNan_Value("LINEA DE CUIDADO",i,row,excel_data_df)                   
                    tipo_prestacion = pss_utils.fill_cell_nonNan_Value("TIPO DE PRESTACION",i,row,excel_data_df)                   
                    
                    excel_data_df = excel_data_df.append( 
                               {'LINEA DE CUIDADO': linea_de_cuidado
                             , 'TIPO DE PRESTACION': tipo_prestacion
                             , 'NOMBRE DE LA PRESTACION':row["NOMBRE DE LA PRESTACION"]
                             , 'CODIGO':objeto_diagnostico[y],
                               'PRECIO':row["PRECIO"] }, ignore_index = True  )
                
                    breakpoint()                       
            #   Operacion de diferencia de conjuntos sobre codigos para eliminar los codigos con diagnosticos que estan 
            #   escritos como listas en una celda. De esta manera solo quedan en el archivo final los codigos con diagnosticos
            #   desglosados uno por fila
            excel_data_df = excel_data_df[ excel_data_df.CODIGO.isin(excel_data_df_diag.CODIGO) == False]
            #Eliminamos celdas vacias
            excel_data_df = excel_data_df.dropna(how='all')
            
            #Escribimos el archivo excel nuevo
            writer = pd.ExcelWriter(output_filepath, engine='xlsxwriter')
            excel_data_df.to_excel(writer,sheet_name=hoja)
            writer.save()
            writer.close()
            
except IOError:
        print('El archivo no se puede abrir o no existe:', input_filepath)
except Exception as e:
        print('Ha ocurrido un error: ', e)