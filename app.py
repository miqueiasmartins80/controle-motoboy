import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Controle do Motoca", layout="centered")

st.title("🏍️ Meu Controle de Moto")

# --- CONEXÃO COM A SUA PLANILHA ---
url_planilha = "https://docs.google.com/spreadsheets/d/1-SsKkyNLE8AnSMNMS22QXHeOeAUT9bzCzwoz7787JQg/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Tenta ler a planilha
    df = conn.read(spreadsheet=url_planilha)
    # Remove linhas totalmente vazias
    df = df.dropna(how="all")
except Exception as e:
    st.error("Aguardando conexão com a planilha...")
    df = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Valor", "Obs"])

# --- FORMULÁRIO DE LANÇAMENTO ---
with st.expander("📝 Novo Lançamento", expanded=True):
    tipo = st.radio("O que é?", ["Entrada", "Saída"])
    col1, col2 = st.columns(2)
    with col1:
        if tipo == "Entrada":
            cat = st.selectbox("Origem", ["Entregas App", "Particular", "Gorjeta", "Outros"])
        else:
            cat = st.selectbox("Destino", ["Gasolina", "Troca de Óleo", "Pneu/Relação", "Mecânico", "Almoço/Lanche", "Prestação"])
            
        valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
    
    with col2:
        data = st.date_input("Data", datetime.now())
        obs = st.text_input("Detalhes (Ex: Posto Ipiranga)")

    if st.button("✅ Salvar para Sempre"):
        # Cria a nova linha
        novo_registro = pd.DataFrame([{
            "Data": data.strftime("%d/%m/%Y"),
            "Tipo": tipo,
            "Categoria": cat,
            "Valor": valor,
            "Obs": obs
        }])
        
        # Junta com o que já existe e salva na planilha
        df_atualizado = pd.concat([df, novo_registro], ignore_index=True)
        conn.update(spreadsheet=url_planilha, data=df_atualizado)
        
        st.success("Boa! Gravado na planilha.")
        st.cache_data.clear() # Limpa a memória pra mostrar o dado novo
        st.rerun()

# --- RELATÓRIOS ---
st.divider()
st.header("📊 Resumo Financeiro")

if not df.empty:
    # Garante que a coluna Valor seja tratada como número
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
    
    ganhos = df[df['Tipo'] == "Entrada"]['Valor'].sum()
    gastos = df[df['Tipo'] == "Saída"]['Valor'].sum()
    saldo = ganhos - gastos

    c1, c2, c3 = st.columns(3)
    c1.metric("Ganhei", f"R$ {ganhos:.2f}")
    c2.metric("Gastei", f"R$ {gastos:.2f}")
    c3.metric("Sobra", f"R$ {saldo:.2f}")

    # Gráfico de Gastos
    st.subheader("Onde está indo o dinheiro?")
    df_gastos = df[df['Tipo'] == "Saída"]
    if not df_gastos.empty:
        st.bar_chart(df_gastos.groupby("Categoria")["Valor"].sum())
    
    st.write("### Histórico de Lançamentos")
    st.dataframe(df.sort_index(
