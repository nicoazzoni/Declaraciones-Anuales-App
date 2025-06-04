import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np

#Configuracion de la pestaña del chrome
st.set_page_config(page_title="Declaraciones Juradas", page_icon="", layout="wide")

#Que mostras cuando todavia no inicias sesion
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Por favor, iniciar sesión desde Inicio.")
    st.stop()

#=================================Botón de Cerrar Sesion=====================================================
with st.sidebar:
    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.scraping_hecho = False
        st.rerun()
#===========================================================================================================
# Inicializamos variables si no existen
if "scraping_hecho" not in st.session_state:
    st.session_state.scraping_hecho = False
if "td_element" not in st.session_state:
    st.session_state.td_element = None
if "cuit" not in st.session_state:
    st.session_state.cuit = ""
if "año_inicio" not in st.session_state:
    st.session_state.año_inicio = 2000
if "año_final" not in st.session_state:
    st.session_state.año_final = 2025
#=============================================================================================================
# Mostrar inputs solo si no se hizo scraping
if not st.session_state.scraping_hecho:
    st.title("Scraping Declaraciones Juradas Anuales COMARB")
    with st.form("scraping_form"):
        cuit = st.text_input("Ingresar el CUIT", value=st.session_state.cuit)
    
        col1, col2 = st.columns(2)
        with col1:
            año_inicio = st.number_input("Desde:", min_value=2000, max_value=2025, value=st.session_state.año_inicio)
        with col2:
            año_final = st.number_input("Hasta:", min_value=2000, max_value=2025, value=st.session_state.año_final)
    
        scraping_button = st.form_submit_button("Ejecutar scraping")

        if scraping_button:

            #===== Barra de progreso
            progress_placeholder = st.empty()  # Placeholder para la barra
            status_text = st.empty()
            status_text.text(f"Buscando declaraciones juradas...")
            progress_bar = progress_placeholder.progress(0)
            #==============================
            
            st.session_state.cuit = cuit
            st.session_state.año_inicio = año_inicio
            st.session_state.año_final = año_final

            s = st.session_state.session  # Reutilizamos la sesión iniciada

            secure_url = f"https://dgrgw.comarb.gob.ar/dgr/sfrDdjjAnual.do?method=buscarAnuales&cuit={cuit}&anioDesdeStr={año_inicio}&anioHastaStr={año_final}"

            r = s.get(secure_url)
            soup = BeautifulSoup(r.text, "html.parser")
    #=======================================================Obtenemos el nombre de la empresa====================================        
            td_element = soup.find_all('td', class_='hdrData')[2].text.strip()
            st.session_state.td_element = td_element
    #=======================================================Hacemos el scrap de verdad ==========================================
            t_trans = soup.find('table', id='transaccion')
    
            if not t_trans:
                st.error("No se encontró la tabla de transacciones. Verifica los datos ingresados.")
            else:
                encabezado = t_trans.find("thead")
                encabezado2 = encabezado.find_all("a")
                titulos_encabezado = [titulo.text for titulo in encabezado2]
                titulos_encabezado.insert(0, "N_Transaccion")
        
                df = pd.DataFrame(columns=titulos_encabezado)
        
                column_data = t_trans.find_all("tr")
                for row in column_data[1:]:
                    row_data = row.find_all("td")
                    individual_row_data = []
                    for data in row_data:
                        link = data.find("a")
                        if link and link.has_attr("href"):
                            individual_row_data.append(link["href"])
                        else:
                            individual_row_data.append(data.text)
                    df.loc[len(df)] = individual_row_data
        
                df["N_Transaccion"] = df["N_Transaccion"].str.extract(r"transaccionAfip=(\d+)")
                df_copiado = df.copy()
                df_filtrado = df_copiado[df_copiado["Banco / Sucursal"] == "993 - Afip"]
                df_filtrado[['Fecha_Presen', 'N']] = df_filtrado['Anticipo'].str.split(' - ', expand=True)
                df_filtrado['N'] = pd.to_numeric(df_filtrado['N'])
                df_final1 = df_filtrado.loc[df_filtrado.groupby('Fecha_Presen')['N'].idxmax()]
                diccionario = df_final1[['N_Transaccion', 'Fecha_Presen']].to_dict(orient='records')

                #==================Armando el contador de pasos para la progress bar
                
                total_pasos = len(df_final1)
                progress_bar = progress_placeholder.progress(1/(total_pasos+1))
                status_text.text(f"Buscando declaraciones juradas...")
                #================================
                
                nombres_columnas = ["Jurisdicción","Coeficiente","Base Imponible","Impuesto Determinado","Retenciones","Percepciones","Saldo Final a Favor del Contribuyente","Año"]
                df_vacio = pd.DataFrame(columns=nombres_columnas)

                for i, item in enumerate(diccionario, start=1):   # Para cada numero de transaccion del diccionario
                    trans = item["N_Transaccion"]
                    fecha = item["Fecha_Presen"]
                    secure_url_2 = f"https://dgrgw.comarb.gob.ar/dgr/sfrDdjjAnual.do?transaccionAfip={trans}&method=detalleAnual"
                
                    z = s.get(secure_url_2) #Nos metemos al link
                    soup_2 = BeautifulSoup(z.text, "html")   #Generamos el codigo html
                    tablas = soup_2.find_all('table', id='elem')
                    tabla_jur = tablas[1]  # Tercera tabla (índice 2)
                    tabla_jur2 = tabla_jur.find('tbody')
                    tabla_jur3 = tabla_jur2.find_all("tr")
                
                    for row in tabla_jur3:
                            row_data_2 = row.find_all("td")
                            individual_row_data_2 = [data.text for data in row_data_2]  #Genera la info
                            individual_row_data_2.append(fecha)            #Anexa columna con la fecha
                            
                            length = len(df_vacio)
                            df_vacio.loc[length] = individual_row_data_2   #Ahora si, mete la inserta la informacion en el DataFrame
                    #=======Barra de progreso    
                    progreso = int((i+1) / (total_pasos+1) * 100)
                    progress_bar.progress(progreso)
                    status_text.text(f"Procesando {i} de {total_pasos} declaraciones juradas...")
                    #===========================
                
                df_vacio[['N_Jur', 'Jurisdicción']] = df_vacio['Jurisdicción'].str.split(' - ', n=1, expand=True)
                cols_a_convertir = [
                    "Coeficiente",
                    'Base Imponible',
                    'Impuesto Determinado',
                    'Retenciones',
                    'Percepciones',
                    'Saldo Final a Favor del Contribuyente'
                ]
                
                for col in cols_a_convertir:
                    df_vacio[col] = df_vacio[col] \
                        .str.replace("$", "", regex=False) \
                        .str.replace(".", "", regex=False) \
                        .str.replace(",", ".", regex=False) \
                        .astype(float)
                df_vacio['Año'] = df_vacio['Año'].astype(int)
                df_vacio['N_Jur'] = df_vacio['N_Jur'].astype(int)
                df_vacio
                #===========ACA DEBERIA CAMBIAR LA BARRA DE PROGRESO POR LO MENOS EL TEXTO===================================
                status_text.text(f"Realizando cálculos...")




                
                #======================Realizamos los calculos para llegar al dataframe final==========================================================================
                #Traemos el archivo de IPC para pasar todo a terminos reales

                ruta1 = 'data/IPC Nacional Anual.xlsx'
                
                tabla_IPC = pd.read_excel(ruta1)  # Asegurate de tener openpyxl instalado
                tabla_IPC.head()

                #Traemos el archivo de Comarb Data para traer Base Imponible e Impuesto Determinado Totales por Provincia.

                ruta2 = 'data/Datos - Comarb Data.xlsx'
                
                tabla_BI = pd.read_excel(ruta2, sheet_name="Base_Imponible")  # Asegurate de tener openpyxl instalado
                tabla_ID = pd.read_excel(ruta2, sheet_name="Impuesto_Determinado")
                tabla_BI.head()
                tabla_ID.head()

                #Ahora si realizamos las columnas nuevas
                
                df_final = df_vacio.copy()

                # Hacemos la realcion entre la tabla de ipc y la original

                df_final = df_final.merge(tabla_IPC, on='Año', how='left')
                
                # Paso 1: obtener IPC para 2025
                ipc_2025 = tabla_IPC.loc[tabla_IPC['Año'] == 2025, 'IPC Anual'].values[0]
                
                # Paso 2: calcular nuevo valor
                df_final['Base Imponible en Terminos Reales'] = df_final.apply(
                    lambda row: row['Base Imponible'] * ipc_2025 / row['IPC Anual'], axis=1
                )
                # Paso 3: calcular nuevo valor 
                df_final['Impuesto Determinado en Terminos Reales'] = df_final.apply(
                    lambda row: row['Impuesto Determinado'] * ipc_2025 / row['IPC Anual'], axis=1
                )

                df_final[['Total Base Anual', 'Total Impuesto Anual']] = (
                df_final.groupby('Año')[['Base Imponible', 'Impuesto Determinado']].transform('sum')
            )
            
                df_final['Pct_Base_Imponible'] = df_final['Base Imponible'] / df_final['Total Base Anual']
                df_final['Pct_Impuesto_Determinado'] = df_final['Impuesto Determinado'] / df_final['Total Impuesto Anual']

                df_final['Var_% Base Imponible'] = (
                    df_final.groupby('Jurisdicción')['Base Imponible'].pct_change() * 100
                )
                
                df_final['Var_% Base Real'] = (
                    df_final.groupby('Jurisdicción')['Base Imponible en Terminos Reales'].pct_change() * 100
                )
                
                df_final['Var_% Pct Base'] = (
                    df_final.groupby('Jurisdicción')['Pct_Base_Imponible'].pct_change() * 100
                )
                
                df_final['Var_% Impuesto Determinado'] = (
                    df_final.groupby('Jurisdicción')['Impuesto Determinado'].pct_change() * 100
                )
                
                df_final['Var_% Impuesto Real'] = (
                    df_final.groupby('Jurisdicción')['Impuesto Determinado en Terminos Reales'].pct_change() * 100
                )
                
                df_final['Var_% Pct Impuesto'] = (
                    df_final.groupby('Jurisdicción')['Pct_Impuesto_Determinado'].pct_change() * 100
                )
                # ==================================================CALCULO DE LOS INDICES==================================            
                #===========prueba nueva=========================
                #Indice de Base Imponible
                df_final["Índice Base Imponible (Base 100)"] = np.nan

                for jurisdiccion, grupo in df_final.groupby("Jurisdicción"):
                    grupo = grupo.sort_values("Año")
                    año_base1 = grupo["Año"].min()
                    valor_base1 = grupo.loc[grupo["Año"] == año_base1, "Base Imponible"].values[0]
                    df_final.loc[grupo.index, "Índice Base Imponible (Base 100)"]=grupo["Base Imponible"]/valor_base1*100

                #Base Imponible en Terminos Reales
                df_final["Índice Base Imponible Real (Base 100)"] = np.nan

                for jurisdiccion, grupo in df_final.groupby("Jurisdicción"):
                    grupo = grupo.sort_values("Año")
                    año_base1 = grupo["Año"].min()
                    valor_base1 = grupo.loc[grupo["Año"] == año_base1, "Base Imponible en Terminos Reales"].values[0]
                    df_final.loc[grupo.index, "Índice Base Imponible Real (Base 100)"]=grupo["Base Imponible en Terminos Reales"]/valor_base1*100

                # % Base Imponible
                df_final["Índice % Base Imponible (Base 100)"] = np.nan

                for jurisdiccion, grupo in df_final.groupby("Jurisdicción"):
                    grupo = grupo.sort_values("Año")
                    año_base1 = grupo["Año"].min()
                    valor_base1 = grupo.loc[grupo["Año"] == año_base1, "Pct_Base_Imponible"].values[0]
                    df_final.loc[grupo.index, "Índice % Base Imponible (Base 100)"]=grupo["Pct_Base_Imponible"]/valor_base1*100

                # Impuesto Determinado
                df_final["Índice Impuesto Determinado (Base 100)"] = np.nan

                for jurisdiccion, grupo in df_final.groupby("Jurisdicción"):
                    grupo = grupo.sort_values("Año")
                    año_base1 = grupo["Año"].min()
                    valor_base1 = grupo.loc[grupo["Año"] == año_base1, "Impuesto Determinado"].values[0]
                    df_final.loc[grupo.index, "Índice Impuesto Determinado (Base 100)"]=grupo["Impuesto Determinado"]/valor_base1*100

                # Impuesto Determinado en Terminos Reales
                df_final["Índice Impuesto Real (Base 100)"] = np.nan

                for jurisdiccion, grupo in df_final.groupby("Jurisdicción"):
                    grupo = grupo.sort_values("Año")
                    año_base1 = grupo["Año"].min()
                    valor_base1 = grupo.loc[grupo["Año"] == año_base1, "Impuesto Determinado en Terminos Reales"].values[0]
                    df_final.loc[grupo.index, "Índice Impuesto Real (Base 100)"]=grupo["Impuesto Determinado en Terminos Reales"]/valor_base1*100

                #Vacio
                df_final["Índice % Impuesto Determinado (Base 100)"] = np.nan

                for jurisdiccion, grupo in df_final.groupby("Jurisdicción"):
                    grupo = grupo.sort_values("Año")
                    año_base1 = grupo["Año"].min()
                    valor_base1 = grupo.loc[grupo["Año"] == año_base1, "Pct_Impuesto_Determinado"].values[0]
                    df_final.loc[grupo.index, "Índice % Impuesto Determinado (Base 100)"]=grupo["Pct_Impuesto_Determinado"]/valor_base1*100

                #=============================================================================================================
                
                df_final['N_Jur - Año'] = df_final['N_Jur'].astype(str) + ' - ' + df_final['Año'].astype(str)

                df_final = df_final.merge(tabla_BI, on='N_Jur - Año', how='left')
                df_final = df_final.merge(tabla_ID, on='N_Jur - Año', how='left')
                
                df_final['Ratio_Base_Imponible'] = (df_final['Base Imponible'] / df_final['Base Imponible Comarb'])*100
                df_final['Ratio_Impuesto_Determinado'] = (df_final['Impuesto Determinado'] / df_final['Impuesto Determinado Comarb'])*100

                
                df_final["Alicuota Efectiva"] = (df_final["Impuesto Determinado"] / df_final["Base Imponible"])*100
                df_final["Año_str"] = df_final["Año"].astype(str)
                
                df_final["Base Imponible en millones"] = df_final["Base Imponible"] / 1000000
                df_final["Impuesto Determinado en millones"] = df_final["Impuesto Determinado"] / 1000000

                df_final["Base Imponible TR en millones"] = df_final["Base Imponible en Terminos Reales"] / 1000000
                df_final["Impuesto Determinado TR en millones"] = df_final["Impuesto Determinado en Terminos Reales"] / 1000000

                
                df_final["Retenciones en millones"] = df_final["Retenciones"] / 1000000
                df_final["Percepciones en millones"] = df_final["Percepciones"] / 1000000
                df_final["Saldo a Favor en millones"] = df_final["Saldo Final a Favor del Contribuyente"] / 1000000

                # Los pasamos a terminos reales
                df_final['Retenciones TR en millones'] = df_final.apply(
                    lambda row: row['Retenciones en millones'] * ipc_2025 / row['IPC Anual'], axis=1
                )
                # Los pasamos a terminos reales
                df_final['Percepciones TR en millones'] = df_final.apply(
                    lambda row: row['Percepciones en millones'] * ipc_2025 / row['IPC Anual'], axis=1
                )
                # Los pasamos a terminos reales
                df_final['Saldo a Favor TR en millones'] = df_final.apply(
                    lambda row: row['Saldo a Favor en millones'] * ipc_2025 / row['IPC Anual'], axis=1
                )

                df_final["Retenciones como % de ID"] = (df_final["Retenciones"] / df_final["Impuesto Determinado"])
                df_final["Percepciones como % de ID"] = (df_final["Percepciones"] / df_final["Impuesto Determinado"])
                df_final["Saldo como % de ID"] = (df_final["Saldo Final a Favor del Contribuyente"] / df_final["Impuesto Determinado"])

                
                #======================Desaparece la barra de progreso
                progress_bar.progress(1)
                progress_placeholder.empty()
                status_text.empty()
                #==================================================
                # Guardar en session_state para que no desaparezca al cambiar de página
                st.session_state.scraping_hecho = True
                st.session_state.df_scrap = df_vacio
                st.session_state.df_final = df_final
                # Calcular el año mínimo y máximo realmente disponibles en los datos scrapings
                año_min_real = int(st.session_state.df_scrap['Año'].min())
                año_max_real = int(st.session_state.df_scrap['Año'].max())
                
                # Guardarlos en session_state para usarlos en otras páginas
                st.session_state.año_min_real = año_min_real
                st.session_state.año_max_real = año_max_real
    #========================================Metes un rerun para que se actualice todo=========            
            st.rerun()

#========================================================================================================================
# Mostrar resultado si ya se hizo scraping
if st.session_state.scraping_hecho:
    if st.button("🔁 Realizar un nuevo scraping"):
            st.session_state.scraping_hecho = False
            st.rerun()
        
    st.title("Scrap realizado con los siguientes datos:")
    st.markdown(f"CUIT: **{st.session_state.cuit}**")
    st.markdown(f"Contribuyente: **{st.session_state.td_element}**")
    st.markdown(f"Desde el año: **{st.session_state.año_min_real}**")
    st.markdown(f"Hasta el año: **{st.session_state.año_max_real}**")

    st.dataframe(st.session_state.df_scrap)




