import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
from collections import Counter

# ---------------- CONFIGURAÇÃO ----------------
st.set_page_config(
    page_title="Lotofácil Inteligente",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Lotofácil – Inteligência Estatística (sem promessas)")
st.caption("Probabilidade empírica • filtros inteligentes • decisão assistida")

# ---------------- FUNÇÕES BASE ----------------
def extrair_dezenas(df):
    cols = df.columns[-15:]
    return df[cols].values.tolist()

def frequencia_absoluta(jogos):
    cont = Counter()
    for j in jogos:
        cont.update(j)
    return cont

def score_por_numero(freq_abs, total_concursos):
    score = {}
    for n in range(1, 26):
        score[n] = freq_abs.get(n, 0) / total_concursos
    return score

def tendencia(jogos_ultimos, jogos_total):
    freq_ult = frequencia_absoluta(jogos_ultimos)
    freq_tot = frequencia_absoluta(jogos_total)
    tendencia = {}
    for n in range(1, 26):
        tendencia[n] = freq_ult.get(n, 0) - freq_tot.get(n, 0)
    return tendencia

def classificar_quentes_frios(score, n_quentes=8, n_frios=8):
    ranking = sorted(score.items(), key=lambda x: x[1], reverse=True)
    quentes = [n for n, _ in ranking[:n_quentes]]
    frios = [n for n, _ in ranking[-n_frios:]]
    return quentes, frios

def gerar_jogos(base_numeros, qtd_jogos, soma_min, soma_max, pares_min, pares_max):
    jogos_validos = []
    tentativas = 0
    while len(jogos_validos) < qtd_jogos and tentativas < qtd_jogos * 500:
        jogo = sorted(np.random.choice(base_numeros, 15, replace=False))
        soma = sum(jogo)
        pares = sum(1 for n in jogo if n % 2 == 0)

        if soma_min <= soma <= soma_max and pares_min <= pares <= pares_max:
            jogos_validos.append(jogo)
        tentativas += 1
    return jogos_validos

def testar_historico(jogos, historico):
    resultados = []
    for jogo in jogos:
        acertos = []
        for sorteio in historico:
            acertos.append(len(set(jogo) & set(sorteio)))
        resultados.append(acertos)
    return resultados

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Configurações")

qtd_jogos = st.sidebar.slider("Quantidade de jogos", 1, 50, 10)
janela = st.sidebar.slider("Janela de análise (concursos)", 10, 100, 30)

soma_min = st.sidebar.slider("Soma mínima", 150, 300, 190)
soma_max = st.sidebar.slider("Soma máxima", 150, 300, 240)

pares_min = st.sidebar.slider("Pares mínimos", 4, 10, 6)
pares_max = st.sidebar.slider("Pares máximos", 4, 10, 9)

qtd_quentes = st.sidebar.slider("Qtd números quentes", 4, 10, 6)
qtd_frios = st.sidebar.slider("Qtd números frios", 4, 10, 6)

# ---------------- UPLOAD CSV ----------------
st.subheader("📥 Importar resultados")
arquivo = st.file_uploader("Envie o CSV dos resultados oficiais", type=["csv"])

if arquivo:
    df = pd.read_csv(arquivo)
    jogos = extrair_dezenas(df)
    total_concursos = len(jogos)

    st.success(f"{total_concursos} concursos carregados")
    st.dataframe(df.head())

    # ---------------- ANÁLISE ----------------
    freq_abs = frequencia_absoluta(jogos)
    score = score_por_numero(freq_abs, total_concursos)
    jogos_ultimos = jogos[:janela]

    tend = tendencia(jogos_ultimos, jogos)
    quentes, frios = classificar_quentes_frios(score, qtd_quentes, qtd_frios)

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Números quentes")
        st.write(sorted(quentes))

    with col2:
        st.subheader("❄️ Números frios")
        st.write(sorted(frios))

    st.subheader("📊 Ranking probabilístico")
    df_score = pd.DataFrame({
        "Número": list(score.keys()),
        "Score": list(score.values()),
        "Tendência": [tend[n] for n in score.keys()]
    }).sort_values("Score", ascending=False)

    st.dataframe(df_score)

    # ---------------- GERAÇÃO ----------------
    st.divider()
    st.subheader("🎯 Geração estratégica de jogos")

    base = list(set(quentes + frios))
    jogos_gerados = gerar_jogos(
        base,
        qtd_jogos,
        soma_min,
        soma_max,
        pares_min,
        pares_max
    )

    if jogos_gerados:
        st.success(f"{len(jogos_gerados)} jogos gerados")
        for i, j in enumerate(jogos_gerados, 1):
            st.write(f"Jogo {i}: {j}")
    else:
        st.warning("Nenhum jogo válido com esses filtros.")

    # ---------------- TESTE HISTÓRICO ----------------
    st.divider()
    st.subheader("🧪 Teste histórico automático")

    resultados = testar_historico(jogos_gerados, jogos)

    resumo = []
    for idx, acertos in enumerate(resultados):
        resumo.append({
            "Jogo": idx + 1,
            "Média de acertos": np.mean(acertos),
            "Máx": max(acertos),
            "Min": min(acertos)
        })

    df_resumo = pd.DataFrame(resumo)
    st.dataframe(df_resumo)

    st.caption("⚠️ Sem promessas. Apenas estatística aplicada.")
