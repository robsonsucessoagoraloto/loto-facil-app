import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

# ================= CONFIGURAÇÃO =================
st.set_page_config(
    page_title="Lotofácil Inteligente",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Lotofácil – Inteligência Estatística")
st.caption("Probabilidade empírica • filtros inteligentes • decisão assistida")

# ================= FUNÇÕES BASE =================
def extrair_dezenas(df):
    cols = df.columns[-15:]
    return df[cols].astype(int).values.tolist()

def frequencia_absoluta(jogos):
    cont = Counter()
    for j in jogos:
        cont.update(j)
    return cont

def score_por_numero(freq_abs, total):
    return {n: freq_abs.get(n, 0) / total for n in range(1, 26)}

def classificar_quentes_frios(score, n_quentes, n_frios):
    ranking = sorted(score.items(), key=lambda x: x[1], reverse=True)
    quentes = [n for n, _ in ranking[:n_quentes]]
    frios = [n for n, _ in ranking[-n_frios:]]
    return quentes, frios

# ================= GERAÇÃO =================
def gerar_jogos(base, qtd, soma_min, soma_max, pares_min, pares_max):
    jogos = []
    tentativas = 0

    while len(jogos) < qtd and tentativas < qtd * 1000:
        jogo = sorted(int(n) for n in np.random.choice(base, 15, replace=False))
        soma = sum(jogo)
        pares = sum(1 for n in jogo if n % 2 == 0)

        if soma_min <= soma <= soma_max and pares_min <= pares <= pares_max:
            jogos.append(jogo)

        tentativas += 1

    return jogos

# ================= TESTE HISTÓRICO =================
def testar_historico(jogo, historico):
    return [len(set(jogo) & set(s)) for s in historico]

# ================= SCORE DO JOGO =================
def score_jogo(jogo, historico, jogos_gerados):
    acertos = testar_historico(jogo, historico)
    media_acertos = np.mean(acertos)

    soma = sum(jogo)
    pares = sum(1 for n in jogo if n % 2 == 0)

    # penalidade por redundância
    similaridade = 0
    for outro in jogos_gerados:
        if outro != jogo:
            similaridade += len(set(jogo) & set(outro))

    score_final = (
        media_acertos * 10
        - abs(7 - pares)
        - similaridade * 0.02
    )

    return round(score_final, 2), round(media_acertos, 2)

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Configurações")

qtd_jogos = st.sidebar.slider("Quantidade de jogos", 1, 50, 10)

soma_min = st.sidebar.slider("Soma mínima", 150, 300, 190)
soma_max = st.sidebar.slider("Soma máxima", 150, 300, 240)

pares_min = st.sidebar.slider("Pares mínimos", 4, 10, 6)
pares_max = st.sidebar.slider("Pares máximos", 4, 10, 9)

qtd_quentes = st.sidebar.slider("Qtd números quentes", 4, 12, 6)
qtd_frios = st.sidebar.slider("Qtd números frios", 4, 12, 6)

# ================= UPLOAD =================
st.subheader("📥 Importar resultados oficiais")
arquivo = st.file_uploader("Envie o CSV da Lotofácil", type=["csv"])

if arquivo:
    df = pd.read_csv(arquivo)
    jogos_historicos = extrair_dezenas(df)

    st.success(f"{len(jogos_historicos)} concursos carregados")
    st.dataframe(df.head())

    # ================= ANÁLISE =================
    freq = frequencia_absoluta(jogos_historicos)
    score_numeros = score_por_numero(freq, len(jogos_historicos))

    quentes, frios = classificar_quentes_frios(
        score_numeros, qtd_quentes, qtd_frios
    )

    base = sorted(set(quentes + frios))

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Números quentes")
        st.write(quentes)

    with col2:
        st.subheader("❄️ Números frios")
        st.write(frios)

    # ================= RANKING NÚMEROS =================
    st.subheader("📊 Ranking probabilístico dos números")
    df_score = pd.DataFrame({
        "Número": score_numeros.keys(),
        "Score": score_numeros.values()
    }).sort_values("Score", ascending=False)

    st.dataframe(df_score)

    # ================= GERAÇÃO =================
    st.divider()
    st.subheader("🎯 Geração estratégica de jogos")

    if len(base) < 15:
        st.error("Base insuficiente. Aumente quentes/frios.")
    else:
        jogos_gerados = gerar_jogos(
            base,
            qtd_jogos,
            soma_min,
            soma_max,
            pares_min,
            pares_max
        )

        if jogos_gerados:
            resultados = []

            for jogo in jogos_gerados:
                score_final, media = score_jogo(
                    jogo, jogos_historicos, jogos_gerados
                )
                resultados.append({
                    "Jogo": jogo,
                    "Score do jogo": score_final,
                    "Média histórica de acertos": media
                })

            df_resultados = pd.DataFrame(resultados)
            df_resultados = df_resultados.sort_values(
                "Score do jogo", ascending=False
            )

            st.success("Jogos ranqueados por qualidade estatística")
            st.dataframe(df_resultados)

        else:
            st.warning("Nenhum jogo válido com esses filtros.")

    st.caption(
        "⚠️ Estatística aplicada. Sem promessas. "
        "IA probabilística e decisão assistida."
    )
