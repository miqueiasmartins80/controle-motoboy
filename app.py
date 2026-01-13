import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Relatório do Motoca", layout="centered")

# Título Centralizado
st.markdown("<h1 style='text-align: center;'>📊 Controle de Gasto</h1>", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DOS LINKS ---
# 1. Cole o link do seu FORMULÁRIO aqui embaixo entre as aspas
url_formulario = "https://forms.gle/cZm7A2bT7UVTbTcn8"

# 2. Link da sua PLANILHA (ID da sua planilha que já temos)
sheet_id = "1-SsKkyNLE8AnSMNMS22QXHeOeAUT9bzCzwoz7787JQg"
url_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

# Botão de Lançamento (Fica no topo para ser rápido)
st.link_button("➕ LANÇAR NOVO GAISTO/GANHO", url_formulario, use_container_width=True)

st.divider()

# --- CARREGAR DADOS ---
try:
    # Lendo o CSV da planilha (Google Sheets atualiza o CSV a cada 5 min aprox.)
    df = pd.read_csv(url_csv)
    
    if not df.empty:
        # Ajustando os nomes das colunas caso o Form mude (opcional)
        # Se o Form criar nomes grandes, o código tenta tratar:
        df.columns = ["Timestamp", "Data", "Tipo", "Categoria", "Valor", "Obs"]
        
        # Converte valor para número (remove R$ se você digitar)
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)

        # MÉTRICAS
        ganhos = df[df['Tipo'] == "Entrada"]['Valor'].sum()
        gastos = df[df['Tipo'] == "Saída"]['Valor'].sum()
        sobra = ganhos - gastos

        c1, c2, c3 = st.columns(3)
        c1.metric("Ganhei", f"R$ {ganhos:.2f}")
        c2.metric("Gastei", f"R$ {gastos:.2f}")
        c3.metric("Sobra", f"R$ {sobra:.2f}")

        # GRÁFICO
        st.subheader("Destino dos Gastos")
        df_gastos = df[df['Tipo'] == "Saída"]
        if not df_gastos.empty:
            st.bar_chart(df_gastos.groupby("Categoria")["Valor"].sum())

        st.write("### Histórico Recente")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("Planilha vazia. Clique no botão acima para lançar!")

except Exception as e:
    st.error("Dica: No Google Sheets, vá em Arquivo > Compartilhar > Publicar na Web e selecione CSV para o app ler os dados instantaneamente.")
