import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
from io import StringIO

# ======================================================
# CONFIGURAÇÃO
# ======================================================
st.set_page_config(
    page_title="Lotofácil – Inteligência Estatística",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Lotofácil – Inteligência Estatística")
st.caption("Probabilidade empírica • filtros • simulação • decisão assistida")

st.info(
    "⚠️ Este sistema NÃO promete prêmios.\n"
    "Ele elimina jogos ruins, aplica estatística real e "
    "auxilia decisões com base em dados históricos."
)

# ======================================================
# BASE ONLINE
# ======================================================
URL_BASE_ONLINE = (
URL_BASE_ONLINE = (
    "https://raw.githubusercontent.com/robsonsucessoagora/loto-facil-app/main/lotofacil_resultados.csv"
)
)

@st.cache_data(show_spinner=False)
def carregar_base_online():
    try:
        df = pd.read_csv(URL_BASE_ONLINE)
        df.columns = [c.lower() for c in df.columns]
        return df
    except Exception:
        return None

# ======================================================
# FUNÇÕES ESTATÍSTICAS
# ======================================================
def extrair_dezenas(df):
    cols = df.columns[-15:]
    return df[cols].astype(int).values.tolist()

def frequencia(jogos):
    c = Counter()
    for j in jogos:
        c.update(j)
    return c

def score_numeros(freq, total):
    return {n: freq.get(n, 0) / total for n in range(1, 26)}

def tendencia(jogos_curto, jogos_longo):
    f1 = frequencia(jogos_curto)
    f2 = frequencia(jogos_longo)
    return {n: f1.get(n, 0) - f2.get(n, 0) for n in range(1, 26)}

def classificar(score, n_quentes, n_frios):
    r = sorted(score.items(), key=lambda x: x[1], reverse=True)
    return [n for n,_ in r[:n_quentes]], [n for n,_ in r[-n_frios:]]

# ======================================================
# GERAÇÃO DE JOGOS
# ======================================================
def gerar_jogos(base, qtd, soma_min, soma_max, pares_min, pares_max):
    jogos = []
    tentativas = 0
    while len(jogos) < qtd and tentativas < qtd * 3000:
        jogo = sorted(np.random.choice(base, 15, replace=False))
        soma = sum(jogo)
        pares = sum(1 for n in jogo if n % 2 == 0)
        if soma_min <= soma <= soma_max and pares_min <= pares <= pares_max:
            if list(jogo) not in jogos:
                jogos.append(list(jogo))
        tentativas += 1
    return jogos

# ======================================================
# SCORE POR JOGO + SIMULAÇÃO
# ======================================================
def score_jogo(jogo, score_n):
    return round(sum(score_n[n] for n in jogo), 4)

def simular(jogos, historico):
    dados = []
    for i, jogo in enumerate(jogos, 1):
        acertos = [len(set(jogo) & set(s)) for s in historico]
        dados.append({
            "Jogo": i,
            "Score jogo": score_jogo(jogo, score_num),
            "Média acertos": round(np.mean(acertos), 2),
            "Máx": max(acertos),
            "Min": min(acertos)
        })
    return pd.DataFrame(dados)

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.header("⚙️ Configurações")

qtd_jogos = st.sidebar.slider("Quantidade de jogos", 5, 50, 20)
janela = st.sidebar.slider("Janela histórica", 100, 3000, 500)

soma_min = st.sidebar.slider("Soma mínima", 150, 300, 190)
soma_max = st.sidebar.slider("Soma máxima", 150, 300, 240)

pares_min = st.sidebar.slider("Pares mínimos", 4, 10, 6)
pares_max = st.sidebar.slider("Pares máximos", 4, 10, 9)

qtd_quentes = st.sidebar.slider("Qtd quentes", 4, 15, 8)
qtd_frios = st.sidebar.slider("Qtd frios", 4, 15, 7)

# ======================================================
# CARREGAMENTO DA BASE
# ======================================================
st.subheader("📥 Base de resultados")

df = carregar_base_online()

if df is None:
    st.warning("Base online indisponível. Envie CSV manual.")
    arq = st.file_uploader("Upload CSV", type=["csv"])
    if arq:
        df = pd.read_csv(arq)

if df is None:
    st.stop()

if len(df) < 100:
    st.warning("Base pequena. Resultados podem distorcer.")

st.success(f"{len(df)} concursos carregados")
st.dataframe(df.tail())

# ======================================================
# ANÁLISE
# ======================================================
jogos = extrair_dezenas(df)
freq = frequencia(jogos)
score_num = score_numeros(freq, len(jogos))

jogos_curto = jogos[-janela:]
tend = tendencia(jogos_curto, jogos)

quentes, frios = classificar(score_num, qtd_quentes, qtd_frios)

st.subheader("🔥 Quentes / ❄️ Frios")
st.write("Quentes:", quentes)
st.write("Frios:", frios)

# ======================================================
# ESTRATÉGIAS
# ======================================================
estrategias = {
    "A – Quentes": quentes + frios[:3],
    "B – Balanceada": quentes[:5] + frios[:5],
    "C – Frios": frios + quentes[:3]
}

resultados = []

st.subheader("🧪 Comparador de estratégias")

for nome, base in estrategias.items():
    if len(base) < 15:
        continue
    jogos_gen = gerar_jogos(base, qtd_jogos, soma_min, soma_max, pares_min, pares_max)
    df_sim = simular(jogos_gen, jogos_curto)
    media = df_sim["Média acertos"].mean()
    resultados.append({
        "Estratégia": nome,
        "Jogos gerados": len(jogos_gen),
        "Média geral acertos": round(media, 2)
    })
    with st.expander(f"Detalhes – {nome}"):
        st.dataframe(df_sim.sort_values("Score jogo", ascending=False))

df_comp = pd.DataFrame(resultados)
st.dataframe(df_comp)

# ======================================================
# EXPORTAÇÃO
# ======================================================
st.subheader("📤 Exportação")

csv_out = df_comp.to_csv(index=False)
st.download_button(
    "Baixar relatório (CSV)",
    csv_out,
    file_name="comparacao_estrategias_lotofacil.csv",
    mime="text/csv"
)
