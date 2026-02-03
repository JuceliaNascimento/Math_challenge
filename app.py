import streamlit as st
import pandas as pd
import random
import time
from github import Github
from io import StringIO

# --- CONFIGURAÇÕES ---
REPO_NAME = "JuceliaNascimento/Math_challenge" # Seu repositório
ARQUIVO_DADOS = "dados.csv"
META_MAXIMA = 100.00
VALOR_POR_ACERTO = 0.10

# Configuração da página com um ícone divertido e layout largo
st.set_page_config(page_title="Desafio da Sobrinha", page_icon="🦄", layout="centered")

# --- FUNÇÃO PARA FALAR COM O GITHUB (Igual à anterior) ---
def gerenciar_dados(novo_saldo=None):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(REPO_NAME)
    except Exception as e:
        st.error(f"Erro na conexão com GitHub: {e}")
        return 0.0

    try:
        contents = repo.get_contents(ARQUIVO_DADOS)
        csv_content = contents.decoded_content.decode()
        df = pd.read_csv(StringIO(csv_content))
        saldo_atual = float(df.iloc[0]["Saldo"])
        sha = contents.sha
    except:
        saldo_atual = 0.0
        df = pd.DataFrame({"Nome": ["Sobrinha"], "Saldo": [0.0]})
        sha = None

    if novo_saldo is not None:
        df["Saldo"] = novo_saldo
        csv_data = df.to_csv(index=False)
        if sha:
            repo.update_file(ARQUIVO_DADOS, "Atualizando saldo", csv_data, sha)
        else:
            repo.create_file(ARQUIVO_DADOS, "Criando arquivo de saldo", csv_data)
        return novo_saldo
    
    return saldo_atual

# --- FUNÇÃO PARA VERIFICAR O CLIQUE NO BOTÃO ---
def verificar_jogada(resposta_escolhida):
    if resposta_escolhida == st.session_state.resposta_certa:
        # ACERTOU!
        novo_saldo = st.session_state.saldo + VALOR_POR_ACERTO
        if novo_saldo > META_MAXIMA: novo_saldo = META_MAXIMA
        
        # Salva no GitHub sem travar a tela inteira
        with st.spinner("🎉 Acertou! Guardando sua moedinha..."):
            gerenciar_dados(novo_saldo)
        
        st.session_state.saldo = novo_saldo
        st.toast(f"✨ BOA! + R$ {VALOR_POR_ACERTO:.2f} ✨", icon="💰")
        time.sleep(1) # Pausa rápida para celebrar
    else:
        # ERROU
        st.toast("Ah não, tente de novo! 🥺", icon="❌")
        time.sleep(0.5)

    # Limpa o estado para gerar nova pergunta
    del st.session_state["n1"]
    st.rerun()


# --- INTERFACE VISUAL ---

# Cabeçalho colorido
st.markdown("<h1 style='text-align: center; color: #FF69B4;'>🦄 Desafio Mágico de Matemática 🦄</h1>", unsafe_allow_html=True)
st.write("---")

# Carrega saldo inicial se necessário
if "saldo" not in st.session_state:
    st.session_state.saldo = gerenciar_dados()

saldo_visual = st.session_state.saldo
progresso = min(saldo_visual / META_MAXIMA, 1.0)

# Barra de progresso e saldo com visual de "game"
col_saldo, col_meta = st.columns(2)
with col_saldo:
    st.metric(label="💰 SEU COFRINHO", value=f"R$ {saldo_visual:.2f}")
with col_meta:
    st.write(f"🎯 **META: R$ {META_MAXIMA:.2f}**")
st.progress(progresso)

st.write("---")

# Verifica se já ganhou
if saldo_visual >= META_MAXIMA:
    st.balloons()
    st.markdown("<h2 style='text-align: center; color: green;'>🎉 PARABÉNS! VOCÊ ZEROU O JOGO! 🎉</h2>", unsafe_allow_html=True)
    st.write("<h3 style='text-align: center;'>Mande um print para a tia e cobre seu prêmio!</h3>", unsafe_allow_html=True)
    st.image("https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif") # Gif de celebração

else:
    # --- LÓGICA DA PERGUNTA E ALTERNATIVAS ---
    if "n1" not in st.session_state:
        # 1. Gera os números
        st.session_state.n1 = random.randint(2, 9)
        st.session_state.n2 = random.randint(2, 9)
        st.session_state.op = random.choice(["x", "÷"])
        
        # Ajuste para divisão exata e cálculo da resposta certa
        if st.session_state.op == "÷": 
             st.session_state.n1 = st.session_state.n1 * st.session_state.n2
             st.session_state.resposta_certa = int(st.session_state.n1 / st.session_state.n2)
        else:
             st.session_state.resposta_certa = st.session_state.n1 * st.session_state.n2
        
        # 2. Gera alternativas (distratores)
        opcoes = set([st.session_state.resposta_certa])
        while len(opcoes) < 4:
            # Gera um número próximo da resposta certa
            distrator = st.session_state.resposta_certa + random.randint(-5, 5)
            # Garante que é positivo e diferente da resposta certa
            if distrator > 0 and distrator != st.session_state.resposta_certa:
                opcoes.add(distrator)
        
        lista_opcoes = list(opcoes)
        random.shuffle(lista_opcoes)
        st.session_state.opcoes_atuais = lista_opcoes

    # Recupera os dados do estado
    n1, n2, op = st.session_state.n1, st.session_state.n2, st.session_state.op
    opcoes_na_tela = st.session_state.opcoes_atuais
    
    # Mostra a pergunta BEM GRANDE
    st.markdown(f"<h2 style='text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 15px;'>Quanto é {n1} {op} {n2}? 🤔</h2>", unsafe_allow_html=True)
    st.write("") # Espaço

    # Mostra os botões em 2 colunas (Grade 2x2)
    col1, col2 = st.columns(2)
    
    # Botões usam uma função "callback" (on_click) para verificar a resposta
    with col1:
        st.button(f"👉 **{opcoes_na_tela[0]}** 👈", use_container_width=True, on_click=verificar_jogada, args=(opcoes_na_tela[0],))
        st.write("") # Espacinho entre botões verticais
        st.button(f"👉 **{opcoes_na_tela[2]}** 👈", use_container_width=True, on_click=verificar_jogada, args=(opcoes_na_tela[2],))
        
    with col2:
        st.button(f"👉 **{opcoes_na_tela[1]}** 👈", use_container_width=True, on_click=verificar_jogada, args=(opcoes_na_tela[1],))
        st.write("")
        st.button(f"👉 **{opcoes_na_tela[3]}** 👈", use_container_width=True, on_click=verificar_jogada, args=(opcoes_na_tela[3],))
