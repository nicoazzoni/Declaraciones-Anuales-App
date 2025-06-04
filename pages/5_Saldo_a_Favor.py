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
    st.title("Gráficos - Saldo a Favor por Provincia")
    st.markdown(f"Graficando valores para: **{st.session_state.td_element}** desde **{st.session_state.año_min_real}** hasta **{st.session_state.año_max_real}**.")

    df_graficos4 = st.session_state.df_final.copy()

#======================================================CONSTRUIMOS LAS PILLS PARA PODER CAMBIAR DE VALORES Y EJES TODO EL SHOW====================================
    MODOS = {
    "Pesos Corrientes": {
        "columnas": [
            "Retenciones en millones",
            "Percepciones en millones",
            "Saldo a Favor en millones"
        ],
        "titulos": [
            "Retenciones en millones de pesos corrientes",
            "Percepciones en millones de pesos corrientes",
            "Saldo a Favor en millones de pesos corrientes"
        ],
        "ejes_y": [
            "Millones de $",
            "Millones de $",
            "Millones de $"
        ]
    },
    "Pesos de 2025": {
        "columnas": [
            "Retenciones TR en millones",
            "Percepciones TR en millones",
            "Saldo a Favor TR en millones"
        ],
        "titulos": [
            "Retenciones en millones de pesos de 2025",
            "Percepciones en millones de pesos de 2025",
            "Saldo a Favor en millones de pesos de 2025"
        ],
        "ejes_y": [
            "Millones de $ constantes",
            "Millones de $ constantes",
            "Millones de $ constantes"
        ]
    },
       "Como % del Impuesto Determinado": {
        "columnas": [
            "Retenciones como % de ID",
            "Percepciones como % de ID",
            "Saldo como % de ID"
        ],
        "titulos": [
            "Retenciones como % del Impuesto Determinado",
            "Percepciones como % del Impuesto Determinado",
            "Saldo a Favor como % del Impuesto Determinado"
        ],
        "ejes_y": [
            "Años de Impuesto Determinado",
            "Años de Impuesto Determinado",
            "Años de Impuesto Determinado"
        ]
    }
}


    modo = st.pills(
        label="Seleccionar Modo",
        options=["Pesos Corrientes", "Pesos de 2025", "Como % del Impuesto Determinado"],
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
        df_graficos4,  # Asegura que el orden se respete
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
    elif modo == "Como % del Impuesto Determinado":
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
                tickformat='.2f',
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
    
#====================================GRAFICO 2========================================================
    # Crear figura
    fig3 = px.line(
        df_graficos4,  # Asegura que el orden se respete
        x="Año",
        y=config["columnas"][1],
        color="Jurisdicción",
        markers=True,
        title=config["titulos"][1],
        color_discrete_sequence=colors,
    )


    if modo in ["Pesos Corrientes", "Pesos de 2025"]:
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
                text=config["titulos"][1],
                font=dict(size=20, color='black'),
            ),
        )
    elif modo == "Como % del Impuesto Determinado":
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
                tickformat='.2f',
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
                text=config["titulos"][1],
                font=dict(size=20, color='black'),
            ),
        )

    
    st.plotly_chart(fig3, use_container_width=True)

#====================================GRAFICO 2========================================================
    # Crear figura
    fig4 = px.line(
        df_graficos4,  # Asegura que el orden se respete
        x="Año",
        y=config["columnas"][2],
        color="Jurisdicción",
        markers=True,
        title=config["titulos"][2],
        color_discrete_sequence=colors,
    )


    if modo in ["Pesos Corrientes", "Pesos de 2025"]:
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
                text=config["titulos"][2],
                font=dict(size=20, color='black'),
            ),
        )
    elif modo == "Como % del Impuesto Determinado":
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
                tickformat='.2f',
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
                text=config["titulos"][2],
                font=dict(size=20, color='black'),
            ),
        )

    
    st.plotly_chart(fig4, use_container_width=True)





