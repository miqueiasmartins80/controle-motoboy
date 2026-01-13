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
    st.info("Nenhum dado lançado ainda. Comece a registrar seus ganhos e gastos!")import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Controle do Motoca Pro", layout="centered")

st.title("🏍️ Diário do Motoca (Salvo na Nuvem)")

# URL da sua planilha (Cole o link da sua planilha aqui entre as aspas)
url_planilha = "COLE_AQUI_O_LINK_DA_SUA_PLANILHA"

# Conectando com a planilha
conn = st.connection("gsheets", type=GSheetsConnection)

# Lendo os dados já existentes
df = conn.read(spreadsheet=url_planilha, usecols=[0,1,2,3,4])
df = df.dropna(how="all")

# --- FORMULÁRIO ---
with st.expander("📝 Novo Lançamento", expanded=True):
    tipo = st.radio("O que é?", ["Entrada", "Saída"])
    col1, col2 = st.columns(2)
    with col1:
        if tipo == "Entrada":
            cat = st.selectbox("Origem", ["Entregas App", "Particular", "Gorjeta", "Outros"])
        else:
            cat = st.selectbox("Destino", ["Gasolina", "Óleo", "Peças", "Comida", "Outros"])
        valor = st.number_input("Valor R$", min_value=0.0)
    with col2:
        data = st.date_input("Data", datetime.now())
        obs = st.text_input("Detalhes")

    if st.button("✅ Salvar para Sempre"):
        novo_dado = pd.DataFrame([{
            "Data": data.strftime("%d/%m/%Y"),
            "Tipo": tipo,
            "Categoria": cat,
            "Valor": valor,
            "Obs": obs
        }])
        
        # Junta o novo dado com os antigos e salva
        df_atualizado = pd.concat([df, novo_dado], ignore_index=True)
        conn.update(spreadsheet=url_planilha, data=df_atualizado)
        st.success("Salvo na sua Planilha do Google!")
        st.cache_data.clear() # Limpa o cache para mostrar o novo dado

# --- RELATÓRIO ---
st.divider()
if not df.empty:
    ganhos = pd.to_numeric(df[df['Tipo'] == 'Entrada']['Valor']).sum()
    gastos = pd.to_numeric(df[df['Tipo'] == 'Saída']['Valor']).sum()
    
    c1, c2 = st.columns(2)
    c1.metric("Total Ganho", f"R$ {ganhos:.2f}")
    c2.metric("Total Gasto", f"R$ {gastos:.2f}", delta_color="inverse")
    
    st.dataframe(df)
