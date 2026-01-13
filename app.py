import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Controle do Motoca", layout="centered")

st.title("🚀 Controle Financeiro - Motoboy")

# Simulação de banco de dados (em um app real, usaríamos SQL ou Google Sheets)
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Valor", "Descrição"])

# --- FORMULÁRIO DE LANÇAMENTO ---
with st.expander("➕ Lançar Novo Movimento", expanded=True):
    tipo = st.radio("Tipo", ["Entrada (Ganho)", "Saída (Gasto)"])
    col1, col2 = st.columns(2)
    with col1:
        categoria = st.selectbox("Categoria", ["Entrega", "Gasolina", "Manutenção", "Alimentação", "Outros"])
        valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
    with col2:
        data = st.date_input("Data", datetime.now())
        desc = st.text_input("Descrição (Ex: Troca de óleo)")

    if st.button("Salvar Lançamento"):
        novo_dado = pd.DataFrame([[data, tipo, categoria, valor, desc]], 
                                 columns=["Data", "Tipo", "Categoria", "Valor", "Descrição"])
        st.session_state.dados = pd.concat([st.session_state.dados, novo_dado], ignore_index=True)
        st.success("Lançado com sucesso!")

# --- RELATÓRIOS ---
st.divider()
st.header("📊 Resumo Financeiro")

df = st.session_state.dados
if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'])
    
    # Cálculos rápidos
    total_ganho = df[df['Tipo'] == "Entrada (Ganho)"]['Valor'].sum()
    total_gasto = df[df['Tipo'] == "Saída (Gasto)"]['Valor'].sum()
    saldo = total_ganho - total_gasto

    c1, c2, c3 = st.columns(3)
    c1.metric("Ganhos", f"R$ {total_ganho:.2f}")
    c2.metric("Gastos", f"R$ {total_gasto:.2f}", delta_color="inverse")
    c3.metric("Saldo Líquido", f"R$ {saldo:.2f}")

    # Gráfico simples de gastos por categoria
    st.subheader("Destino dos Gastos")
    gastos = df[df['Tipo'] == "Saída (Gasto)"]
    if not gastos.empty:
        st.bar_chart(gastos.groupby("Categoria")["Valor"].sum())
    
    st.dataframe(df.sort_values(by="Data", ascending=False))
else:
    st.info("Nenhum dado lançado ainda. Comece a registrar seus ganhos e gastos!")
