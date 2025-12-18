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

st.title("🎯 Lotofácil – Inteligência Estatística (sem promessas)")
st.caption("Probabilidade empírica • filtros inteligentes • decisão assistida")

# ================= FUNÇÕES =================
def extrair_dezenas(df):
    cols = df.columns[-15:]
    return df[cols].values.tolist()

def frequencia_absoluta(jogos):
    cont = Counter()
    for j in jogos:
        cont.update(j)
    return cont

def score_por_numero(freq_abs, total_concursos):
    return {n: freq_abs.get(n, 0) / total_concursos for n in range(1, 26)}

def classificar_quentes_frios(score, n_quentes, n_frios):
    ranking = sorted(score.items(), key=lambda x: x[1], reverse=True)
    quentes = [n for n, _ in ranking[:n_quentes]]
    frios = [n for n, _ in ranking[-n_frios:]]
    return quentes, frios

def gerar_jogos(base, qtd, soma_min, soma_max, pares_min, pares_max):
    jogos = []
    tentativas = 0

    while len(jogos) < qtd and tentativas < qtd * 1000:
jogo = sorted(int(n) for n in np.random.choice(base_numeros, 15, replace=False))
        soma = sum(jogo)
        pares = sum(1 for n in jogo if n % 2 == 0)

        if soma_min <= soma <= soma_max and pares_min <= pares <= pares_max:
            jogos.append(jogo)

        tentativas += 1

    return jogos

def testar_historico(jogos, historico):
    resumo = []
    for i, jogo in enumerate(jogos, 1):
        acertos = [len(set(jogo) & set(s)) for s in historico]
        resumo.append({
            "Jogo": i,
            "Média de acertos": round(np.mean(acertos), 2),
            "Máx": max(acertos),
            "Min": min(acertos)
        })
    return pd.DataFrame(resumo)

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Configurações")

qtd_jogos = st.sidebar.slider("Quantidade de jogos", 1, 50, 10)
janela = st.sidebar.slider("Janela histórica (concursos)", 10, 100, 30)

soma_min = st.sidebar.slider("Soma mínima", 150, 300, 190)
soma_max = st.sidebar.slider("Soma máxima", 150, 300, 240)

pares_min = st.sidebar.slider("Pares mínimos", 4, 10, 6)
pares_max = st.sidebar.slider("Pares máximos", 4, 10, 9)

qtd_quentes = st.sidebar.slider("Qtd números quentes", 4, 10, 6)
qtd_frios = st.sidebar.slider("Qtd números frios", 4, 10, 6)

# ================= UPLOAD =================
st.subheader("📥 Importar resultados oficiais")
arquivo = st.file_uploader("Envie o CSV da Lotofácil", type=["csv"])

if arquivo:
    df = pd.read_csv(arquivo)
    jogos = extrair_dezenas(df)

    st.success(f"{len(jogos)} concursos carregados")
    st.dataframe(df.head())

    # ================= ANÁLISE =================
    freq = frequencia_absoluta(jogos)
    score = score_por_numero(freq, len(jogos))

    quentes, frios = classificar_quentes_frios(score, qtd_quentes, qtd_frios)
    base = sorted(set(quentes + frios))

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Números quentes")
        st.write(quentes)

    with col2:
        st.subheader("❄️ Números frios")
        st.write(frios)

    st.subheader("📊 Ranking probabilístico")
    df_score = pd.DataFrame({
        "Número": score.keys(),
        "Score": score.values()
    }).sort_values("Score", ascending=False)

    st.dataframe(df_score)

    # ================= GERAÇÃO =================
    st.divider()
    st.subheader("🎯 Geração estratégica de jogos")

    if len(base) < 15:
        st.error(
            f"Base insuficiente ({len(base)} números). "
            "Aumente quentes/frios até no mínimo 15."
        )
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
            st.success(f"{len(jogos_gerados)} jogos gerados")
            for i, j in enumerate(jogos_gerados, 1):
                st.write(f"Jogo {i}: {j}")
        else:
            st.warning("Nenhum jogo válido com esses filtros.")

        # ================= TESTE HISTÓRICO =================
        st.divider()
        st.subheader("🧪 Teste histórico automático")

        df_teste = testar_historico(jogos_gerados, jogos)
        st.dataframe(df_teste)

        st.caption("⚠️ Estatística aplicada. Sem promessas. Decisão assistida.")
