import streamlit as st
import pandas as pd
import random
from github import Github
from io import StringIO

# --- CONFIGURAÇÕES ---
REPO_NAME = "JuceliaNascimento/Math_challenge" # Seu repositório
ARQUIVO_DADOS = "dados.csv"
META_MAXIMA = 100.00
VALOR_POR_ACERTO = 0.10

st.set_page_config(page_title="Desafio da Sobrinha", page_icon="🎁")

# --- FUNÇÃO PARA FALAR COM O GITHUB ---
def gerenciar_dados(novo_saldo=None):
    # Conecta ao GitHub usando o Token (que vamos configurar já já)
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(REPO_NAME)
    except:
        st.error("Erro ao conectar no GitHub. Verifique o Token.")
        return 0.0

    # Tenta ler o arquivo
    try:
        contents = repo.get_contents(ARQUIVO_DADOS)
        csv_content = contents.decoded_content.decode()
        df = pd.read_csv(StringIO(csv_content))
        saldo_atual = float(df.iloc[0]["Saldo"])
        sha = contents.sha # Necessário para atualizar o arquivo
    except:
        # Se o arquivo não existe, cria um dataframe zerado
        saldo_atual = 0.0
        df = pd.DataFrame({"Nome": ["Sobrinha"], "Saldo": [0.0]})
        sha = None

    # Se for para atualizar (salvar novo valor)
    if novo_saldo is not None:
        df["Saldo"] = novo_saldo
        csv_data = df.to_csv(index=False)
        
        if sha:
            repo.update_file(ARQUIVO_DADOS, "Atualizando saldo", csv_data, sha)
        else:
            repo.create_file(ARQUIVO_DADOS, "Criando arquivo de saldo", csv_data)
        return novo_saldo
    
    return saldo_atual

# --- INTERFACE ---
st.title("🎁 Desafio de Matemática")

# Carrega saldo (sem atualizar)
if "saldo" not in st.session_state:
    st.session_state.saldo = gerenciar_dados()

saldo_visual = st.session_state.saldo
progresso = min(saldo_visual / META_MAXIMA, 1.0)

st.write(f"Acumulado: **R$ {saldo_visual:.2f}** / Meta: R$ {META_MAXIMA:.2f}")
st.progress(progresso)

if saldo_visual >= META_MAXIMA:
    st.balloons()
    st.success("PARABÉNS! Você completou o desafio! Mande um print para a tia.")
else:
    # Lógica do Jogo
    if "n1" not in st.session_state:
        st.session_state.n1 = random.randint(2, 9)
        st.session_state.n2 = random.randint(2, 9)
        st.session_state.op = random.choice(["x", "÷"])
        if st.session_state.op == "÷": # Ajuste para divisão exata
             st.session_state.n1 = st.session_state.n1 * st.session_state.n2

    n1, n2, op = st.session_state.n1, st.session_state.n2, st.session_state.op
    
    st.subheader(f"Quanto é {n1} {op} {n2}?")
    
    with st.form("conta"):
        resp = st.number_input("Resposta:", step=1)
        enviar = st.form_submit_button("Responder")
        
        if enviar:
            correto = False
            if op == "x" and resp == (n1 * n2): correto = True
            if op == "÷" and resp == (n1 / n2): correto = True
            
            if correto:
                novo_saldo = st.session_state.saldo + VALOR_POR_ACERTO
                if novo_saldo > META_MAXIMA: novo_saldo = META_MAXIMA
                
                # Salva no GitHub
                with st.spinner("Salvando seu prêmio..."):
                    gerenciar_dados(novo_saldo)
                
                st.session_state.saldo = novo_saldo
                st.success(f"Certa resposta! + R$ {VALOR_POR_ACERTO:.2f}")
                
                # Reinicia números
                del st.session_state["n1"]
                st.rerun()
            else:
                st.error("Tente de novo!")
