import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

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
    st.title("Gráficos - Base Imponible por Provincia")
    st.markdown(f"Graficando valores para: **{st.session_state.td_element}** desde **{st.session_state.año_min_real}** hasta **{st.session_state.año_max_real}**.")

    df_graficos1 = st.session_state.df_final.copy()

#======================================================CONSTRUIMOS LAS PILLS PARA PODER CAMBIAR DE VALORES Y EJES TODO EL SHOW====================================
    MODOS = {
    "Pesos Corrientes": {
        "columnas": [
            "Base Imponible en millones",
            "Var_% Base Imponible",
            "Índice Base Imponible (Base 100)",
            "Ratio_Base_Imponible"
        ],
        "titulos": [
            "Base Imponible en millones de pesos corrientes",
            "Variación (%) - Nominal - Base imponible",
            "Índice Base 100 - Nominal - Base Imponible",
            "Base Imponible - Como % del total de la Base Imponible de la Provincia"
        ],
        "ejes_y": [
            "Millones de $",
            "Variación (%)",
            "Índice",
            "Participación en %"
        ]
    },
    "Pesos de 2025": {
        "columnas": [
            "Base Imponible TR en millones",
            "Var_% Base Real",
            "Índice Base Imponible Real (Base 100)",
            "Ratio_Base_Imponible"
        ],
        "titulos": [
            "Base Imponible en millones de pesos de 2025",
            "Variación (%) - Real - Base imponible",
            "Índice Base 100 - Real - Base Imponible",
            "Base Imponible - Como % del total de la Base Imponible de la Provincia"
        ],
        "ejes_y": [
            "Millones de $ de 2025",
            "Variación real (%)",
            "Índice Real",
            "Participación en %"
        ]
    },
       "Como % del total de la empresa": {
        "columnas": [
            "Pct_Base_Imponible",
            "Var_% Pct Base",
            "Índice % Base Imponible (Base 100)",
            "Ratio_Base_Imponible"
        ],
        "titulos": [
            "Base Imponible - Como % del total de la empresa",
            "Variación (%) - Participación en el total de la Base Imponible de la empresa",
            "Índice Base 100 - Porcentaje de participacion",
            "Base Imponible - Como % del total de la Base Imponible de la Provincia"
        ],
        "ejes_y": [
            "% del total de la empresa",
            "Variación (%)",
            "Índice base 100",
            "Participación en %"
        ]
    }
}


    modo = st.pills(
        label="Seleccionar Modo",
        options=["Pesos Corrientes", "Pesos de 2025", "Como % del total de la empresa"],
        format_func=lambda x: x,
        help="Elegí cómo visualizar los valores",
        default = "Pesos Corrientes"
    )
    if modo is None:
        st.warning("Por favor, seleccioná una opción para mostrar los gráficos.")
    else:
        config = MODOS[modo]

#============================================Paleta de colores de los gráficos========================
 #colors = px.colors.qualitative.Set1
    colors = px.colors.qualitative.D3 + px.colors.qualitative.Set1 + px.colors.qualitative.G10 
#====================================GRAFICO 1========================================================
    

    # Crear figura
    fig2 = px.line(
        df_graficos1,  # Asegura que el orden se respete
        x="Año",
        y=config["columnas"][0],
        color="Jurisdicción",
        markers=True,
        title=config["titulos"][0],
        color_discrete_sequence=colors,
    )


    if modo in ["Pesos Corrientes", "Pesos de 2025"]:
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
                title=config["ejes_y"][0],
                tickformat=',.0f',
                tickprefix='',
                ticksuffix=' M',
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
                text=config["titulos"][0],
                font=dict(size=20, color='black'),
            ),
        )
    elif modo == "Como % del total de la empresa":
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
                title=config["ejes_y"][0],
                tickformat='.0%',
                range=[0, 1],
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='gray',
                autorange=True
            ),
            height=600,
            font=dict(size=14, color="black"),
            template="plotly_white",
            hovermode="closest",
            title=dict(
                text=config["titulos"][0],
                font=dict(size=20, color='black'),
            ),
        )

    
    st.plotly_chart(fig2, use_container_width=True)
    
#==============================================GRAFICO 2==================================================================

    # Crear figura
    fig3 = px.line(
        df_graficos1,  # Asegura que el orden se respete
        x="Año",
        y=config["columnas"][1],
        color="Jurisdicción",
        markers=True,
        title=config["titulos"][1],
        color_discrete_sequence=colors,
    )

    fig3.update_traces(
        line=dict(width=4),
        marker=dict(size=10, symbol='circle')  # podés cambiar 'circle' por otros como 'square', 'diamond', etc.
    )
    fig3.update_layout(
        xaxis=dict(
            title="Año",
            type="linear",
            tickangle=0,
            dtick=1
        ),
        yaxis=dict(
            title=config["ejes_y"][1],
            tickformat=',.0f',
            ticksuffix=' %',
            #range=[0, 1],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray',
            autorange=True
        ),
        height=600,
        font=dict(size=14, color="black"),
        template="plotly_white",
        hovermode="closest",
        title=dict(
            text=config["titulos"][1],
            font=dict(size=20, color='black'),
        ),
    )


    st.plotly_chart(fig3, use_container_width=True)


#======================================================== GRAFICO 3 =============================================================
   # Crear figura
    fig4 = px.line(
        df_graficos1,  # Asegura que el orden se respete
        x="Año",
        y=config["columnas"][2],
        color="Jurisdicción",
        markers=True,
        title=config["titulos"][2],
        color_discrete_sequence=colors,
    )

    fig4.update_traces(
        line=dict(width=4),
        marker=dict(size=10, symbol='circle')  # podés cambiar 'circle' por otros como 'square', 'diamond', etc.
    )
    fig4.update_layout(
        xaxis=dict(
            title="Año",
            type="linear",
            tickangle=0,
            dtick=1
        ),
        yaxis=dict(
            title=config["ejes_y"][2],
            tickformat=',.0f',
            #ticksuffix=' %',
            #range=[0, 1],
            zeroline=False,
            zerolinewidth=2,
            zerolinecolor='gray',
            autorange=True
        ),
        shapes=[
                dict(
                    type="line",
                    xref="paper",  # usa todo el ancho del gráfico
                    yref="y",
                    x0=0,
                    x1=1,
                    y0=100,
                    y1=100,
                    line=dict(
                        color="gray",
                        width=2,
                        dash="solid"
                    )
                )
                ],  

        height=600,
        font=dict(size=14, color="black"),
        template="plotly_white",
        hovermode="closest",
        title=dict(
            text=config["titulos"][2],
            font=dict(size=20, color='black'),
        ),
    )


    st.plotly_chart(fig4, use_container_width=True)

#============================================================ GRAFICO 4 ====================================================
    # Crear figura
    fig5 = px.line(
        df_graficos1,  # Asegura que el orden se respete
        x="Año",
        y=config["columnas"][3],
        color="Jurisdicción",
        markers=True,
        title=config["titulos"][3],
        color_discrete_sequence=colors,
    )

    fig5.update_traces(
        line=dict(width=4),
        marker=dict(size=10, symbol='circle')  # podés cambiar 'circle' por otros como 'square', 'diamond', etc.
    )
    fig5.update_layout(
        xaxis=dict(
            title="Año",
            type="linear",
            tickangle=0,
            dtick=1
        ),
        yaxis=dict(
            title=config["ejes_y"][3],
            tickformat=',.1f',
            ticksuffix=' %',
            #range=[0, 1],
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
            text=config["titulos"][3],
            font=dict(size=20, color='black'),
        ),
    )


    st.plotly_chart(fig5, use_container_width=True)






