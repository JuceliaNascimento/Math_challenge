import streamlit as st
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
VALOR_POR_ACERTO = 0.10
META_MAXIMA = 100.00
NOME_SOBRINHA = "Sua Sobrinha"  # Personalize aqui

st.set_page_config(page_title="Desafio de Aniversário", page_icon="🎂")

# --- FUNÇÕES DE BANCO DE DADOS (Google Sheets) ---
def get_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lê a planilha. Se estiver vazia ou der erro, retorna dataframe inicial
    try:
        df = conn.read(worksheet="Dados", usecols=[0, 1], ttl=0)
        if df.empty:
            return pd.DataFrame({"Nome": [NOME_SOBRINHA], "Saldo": [0.0]})
        return df
    except:
        return pd.DataFrame({"Nome": [NOME_SOBRINHA], "Saldo": [0.0]})

def update_saldo(novo_valor):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = pd.DataFrame({"Nome": [NOME_SOBRINHA], "Saldo": [novo_valor]})
    conn.update(worksheet="Dados", data=df)

# --- INTERFACE ---
st.title(f"🎂 Parabéns, {NOME_SOBRINHA}!")
st.write("Acerte as contas para ganhar seu presente. Cada acerto vale **R$ 0,10**!")

# Carregar Saldo
df = get_data()
saldo_atual = float(df.iloc[0]["Saldo"])

# Barra de Progresso
progresso = min(saldo_atual / META_MAXIMA, 1.0)
st.progress(progresso)
st.metric(label="Seu Presente Acumulado", value=f"R$ {saldo_atual:.2f}", delta=f"Meta: R$ {META_MAXIMA:.2f}")

if saldo_atual >= META_MAXIMA:
    st.balloons()
    st.success(f"PARABÉNS! Você atingiu o valor máximo de R$ {META_MAXIMA:.2f}! Tire um print e mande para o tio.")
else:
    # --- LÓGICA DO JOGO ---
    if "num1" not in st.session_state:
        st.session_state.num1 = random.randint(2, 9)
        st.session_state.num2 = random.randint(2, 9)
        st.session_state.operacao = random.choice(["*", "/"])
        # Ajuste para divisão exata
        if st.session_state.operacao == "/":
            st.session_state.num1 = st.session_state.num1 * st.session_state.num2

    n1 = st.session_state.num1
    n2 = st.session_state.num2
    op_simbolo = "x" if st.session_state.operacao == "*" else "÷"

    st.subheader(f"Quanto é {n1} {op_simbolo} {n2}?")

    with st.form("math_form"):
        resposta = st.number_input("Sua resposta:", step=1)
        enviar = st.form_submit_button("Responder")

        if enviar:
            correto = False
            if st.session_state.operacao == "*" and resposta == (n1 * n2):
                correto = True
            elif st.session_state.operacao == "/" and resposta == (n1 / n2):
                correto = True
            
            if correto:
                novo_saldo = saldo_atual + VALOR_POR_ACERTO
                if novo_saldo > META_MAXIMA: novo_saldo = META_MAXIMA
                
                update_saldo(novo_saldo) # Salva no Google Sheets
                st.success("Resposta Certa! 💰 + R$ 0,10")
                st.balloons()
                
                # Resetar para próxima pergunta
                del st.session_state["num1"] 
                st.rerun()
            else:
                st.error("Ops! Tente novamente.")