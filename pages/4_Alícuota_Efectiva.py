import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(page_title="Declaraciones Juradas", page_icon="", layout="wide")
#Lo que mostras cuando no iniciaste sesion ni iciste el scrap
# Mostrar el botón de "Cerrar sesión" si está logueado
if st.session_state.get("logged_in", False):
    with st.sidebar:
        if st.button("Cerrar sesión"):
            st.session_state.logged_in = False
            st.session_state.scraping_hecho = False
            st.rerun()

# Estado: no inició sesión
if not st.session_state.get("logged_in", False):
    st.warning("Por favor, iniciar sesión desde Inicio.")
    st.warning("Además, debe realizar el scraping para obtener los datos.")

# Estado: sesión iniciada pero sin scraping
elif not st.session_state.get("scraping_hecho", False):
    st.success("Sesión iniciada correctamente.")
    st.warning("Aún no se realizó el scraping. Por favor, hazlo en Scraping.")

# Estado: sesión iniciada y scraping hecho
else:
    st.title("Gráficos - Alícuota Efectiva por Provincia")
    st.markdown(f"Graficando valores para: **{st.session_state.td_element}** desde **{st.session_state.año_min_real}** hasta **{st.session_state.año_max_real}**.")

    df_graficos3 = st.session_state.df_final.copy()

#======================================================CONSTRUIMOS LAS PILLS PARA PODER CAMBIAR DE VALORES Y EJES TODO EL SHOW====================================

#============================================Paleta de colores de los gráficos========================
 #colors = px.colors.qualitative.Set1
    colors = px.colors.qualitative.D3 + px.colors.qualitative.Set1 + px.colors.qualitative.G10 
#====================================GRAFICO 1========================================================
    # Crear figura
    fig2 = px.line(
        df_graficos3,  # Asegura que el orden se respete
        x="Año",
        y="Alicuota Efectiva",
        color="Jurisdicción",
        markers=True,
        title="Alícuota Efectiva por Provincia",
        color_discrete_sequence=colors,
    )

    fig2.update_traces(
        line=dict(width=4),
        marker=dict(size=10, symbol='circle')  # podés cambiar 'circle' por otros como 'square', 'diamond', etc.
    )
    fig2.update_layout(
        xaxis=dict(
            title="Año",
            type="linear",
            tickangle=0,
            dtick=1
        ),
        yaxis=dict(
            title="Alícuota Efectiva en %",
            tickformat=',.2f',
            tickprefix='',
            ticksuffix='%',
            zeroline=False,
            zerolinewidth=2,
            zerolinecolor='gray',
            autorange=True
        ),
        height=600,
        font=dict(size=14, color="black"),
        template="plotly_white",
        hovermode="closest",
        title=dict(
            text="Alícuota Efectiva por Provincia",
            font=dict(size=20, color='black'),
        ),
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    

#====================================GRAFICO 2========================================================
    # Selección de año con selectbox
    años_disponibles = sorted(df_graficos3['Año'].unique())
    año_seleccionado = st.selectbox("Seleccioná un año", años_disponibles, index=len(años_disponibles)-1)

    # Filtrar por año y ordenar de mayor a menor
    df_filtrado = df_graficos3[df_graficos3["Año"] == año_seleccionado]
    df_filtrado = df_filtrado.sort_values(by="Alicuota Efectiva", ascending=False)
    
    # Crear gráfico de barras sin bordes, mismo color azul
    fig_barras = px.bar(
        df_filtrado,
        x="Jurisdicción",
        y="Alicuota Efectiva",
        title=f"Alícuota Efectiva por Provincia - {año_seleccionado}",
        color_discrete_sequence=['#1f77b4']  # Azul
    )
    
    # Quitar bordes (no hace falta definir líneas)
    fig_barras.update_traces(marker_line_width=0)
    
    # Aplicar estética
    fig_barras.update_layout(
        yaxis=dict(
            title="Alícuota Efectiva en %",
            tickformat=',.2f',
            ticksuffix='%',
            zeroline=False
        ),
        xaxis=dict(title="",tickangle=-90),
        height=500,
        font=dict(size=14, color="black"),
        template="plotly_white",
        hovermode="closest",
        title=dict(
            font=dict(size=20, color='black'),
        ),
        showlegend=False  # Oculta la leyenda, ya que todo es un solo color
    )
    
    # Mostrar gráfico en Streamlit
    st.plotly_chart(fig_barras, use_container_width=True)

#=========================GRAFICO 3=============================================

    
    # Suponiendo que df_graficos3 ya está cargado
    df = df_graficos3.copy()
    
    # Aseguramos que los datos estén ordenados
    df.sort_values(by=["Jurisdicción", "Año"], inplace=True)
    
    # Lista de años y jurisdicciones
    años = sorted(df["Año"].unique())
    jurisdicciones = df["Jurisdicción"].unique()
    
    # Definimos la paleta de colores combinada
    colors = px.colors.qualitative.D3 + px.colors.qualitative.Set1 + px.colors.qualitative.G10
    
    # Asignamos un color único por jurisdicción, iterando y haciendo módulo por si hay más jurisdicciones que colores
    color_map = {j: colors[i % len(colors)] for i, j in enumerate(jurisdicciones)}
    
    # Crear figura
    fig = go.Figure()
    
    # Año inicial (primer frame)
    año_inicial = años[0]
    df_inicial = df[df["Año"] == año_inicial]
    
    for j in jurisdicciones:
        row = df_inicial[df_inicial["Jurisdicción"] == j]
        fig.add_trace(go.Scatter(
            x=row["Pct_Base_Imponible"],
            y=row["Alicuota Efectiva"],
            mode="markers+lines",
            name=j,
            marker=dict(size=10, color=color_map[j]),
            line=dict(width=2, color=color_map[j]),
            showlegend=True,
            text=[j] * len(row),
            hoverinfo='skip',
            hoverlabel=dict(namelength=-1),
            hovertemplate=(
                "Alicuota: %{y:.2f}%<br>" +
                "Participación: %{x:.2f}<br>" +
                f"Año: {año_inicial}"
            )
        ))
    
    # Crear frames (uno por año)
    frames = []
    for año in años:
        df_año = df[df["Año"] <= año]  # incluye el rastro
        data = []
    
        for j in jurisdicciones:
            df_j = df_año[df_año["Jurisdicción"] == j]
            customdata = np.array(df_j[["Año"]])
            data.append(go.Scatter(
                x=df_j["Pct_Base_Imponible"],
                y=df_j["Alicuota Efectiva"],
                mode="lines+markers",
                #name=j,
                marker=dict(size=10, color=color_map[j]),
                line=dict(width=2, color=color_map[j]),
                showlegend=True,
                hoverinfo='skip',
                hoverlabel=dict(namelength=-1),
                text=[j] * len(df_j),
                customdata = customdata,
                hovertemplate=(
                    "Alicuota: %{y:.2f}%<br>" +
                    "Participación: %{x:.2f}<br>" +
                    "Año: %{customdata[0]}"
                )
            ))
    
        frames.append(go.Frame(data=data, name=str(año)))
    
    # Asignar frames
    fig.frames = frames
    
    # Layout
    fig.update_layout(
        title="Relación - Participación de la Base Imponible en el total de la empresa y Alícuota Efectiva",
        xaxis_title="Base Imponible como % del total de la empresa",
        yaxis_title="Alicuota Efectiva",
        width=650,
        height=600,
        xaxis=dict(range=[
            df["Pct_Base_Imponible"].min() * 0.8,
            df["Pct_Base_Imponible"].max() * 1.1
        ]),
        yaxis=dict(range=[
            df["Alicuota Efectiva"].min() * 0.9,
            df["Alicuota Efectiva"].max() * 1.1
        ]),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None, {"frame": {"duration": 700, "redraw": True},
                                       "fromcurrent": True}])]
        )]
    )
    
    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)


