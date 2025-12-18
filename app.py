import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

# ================= CONFIGURAÇÃO =================
st.set_page_config(
    page_title="Lotofácil – Inteligência Estatística",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Lotofácil – Inteligência Estatística")
st.caption("Probabilidade empírica • filtros inteligentes • decisão assistida")
st.divider()

# ================= BASE AUTOMÁTICA =================
@st.cache_data(ttl=60*60*24)
def carregar_base_online():
    url = "https://raw.githubusercontent.com/robsonsucessoagoraloto/base-lotofacil/main/lotofacil.csv"
    df = pd.read_csv(url)
    return df

# ================= FUNÇÕES =================
def extrair_dezenas(df):
    cols = df.columns[-15:]
    return df[cols].values.tolist()

def frequencia_absoluta(jogos):
    cont = Counter()
    for j in jogos:
        cont.update(j)
    return cont

def score_por_numero(freq, total):
    return {n: freq.get(n, 0) / total for n in range(1, 26)}

def classificar_quentes_frios(score, q_quentes, q_frios):
    ranking = sorted(score.items(), key=lambda x: x[1], reverse=True)
    quentes = [n for n, _ in ranking[:q_quentes]]
    frios = [n for n, _ in ranking[-q_frios:]]
    return quentes, frios

def gerar_jogos(base, qtd, soma_min, soma_max, pares_min, pares_max):
    jogos = []
    tentativas = 0

    while len(jogos) < qtd and tentativas < qtd * 1000:
        jogo = sorted(int(n) for n in np.random.choice(base, 15, replace=False))
        soma = sum(jogo)
        pares = sum(1 for n in jogo if n % 2 == 0)

        if soma_min <= soma <= soma_max and pares_min <= pares <= pares_max:
            if jogo not in jogos:
                jogos.append(jogo)

        tentativas += 1

    return jogos

def simular_jogo(jogo, historico):
    acertos = [len(set(jogo) & set(s)) for s in historico]
    return {
        "Média acertos": round(np.mean(acertos), 2),
        "Máx": max(acertos),
        "Min": min(acertos)
    }

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Configurações")

fonte = st.sidebar.radio(
    "Fonte de dados",
    ["Automática (recomendada)", "Upload manual"]
)

janela = st.sidebar.selectbox(
    "Janela histórica",
    {
        "Curto prazo (50)": 50,
        "Médio prazo (200)": 200,
        "Longo prazo (todos)": None
    }
)

qtd_jogos = st.sidebar.slider("Quantidade de jogos", 5, 50, 20)
soma_min = st.sidebar.slider("Soma mínima", 150, 300, 190)
soma_max = st.sidebar.slider("Soma máxima", 150, 300, 240)
pares_min = st.sidebar.slider("Pares mínimos", 4, 10, 6)
pares_max = st.sidebar.slider("Pares máximos", 4, 10, 9)
q_quentes = st.sidebar.slider("Qtd números quentes", 5, 12, 8)
q_frios = st.sidebar.slider("Qtd números frios", 5, 12, 8)

# ================= CARREGAMENTO =================
if fonte == "Automática (recomendada)":
    df = carregar_base_online()
    st.success(f"Base automática carregada ({len(df)} concursos)")
else:
    arquivo = st.file_uploader("Envie CSV manual", type=["csv"])
    if not arquivo:
        st.stop()
    df = pd.read_csv(arquivo)

jogos = extrair_dezenas(df)

if janela:
    jogos = jogos[:janela]

# ================= ANÁLISE =================
freq = frequencia_absoluta(jogos)
score = score_por_numero(freq, len(jogos))
quentes, frios = classificar_quentes_frios(score, q_quentes, q_frios)

st.subheader("🔥 Números quentes / ❄️ Números frios")
col1, col2 = st.columns(2)
with col1:
    st.write(sorted(quentes))
with col2:
    st.write(sorted(frios))

df_score = pd.DataFrame({
    "Número": score.keys(),
    "Score": score.values()
}).sort_values("Score", ascending=False)

st.subheader("📊 Ranking probabilístico dos números")
st.dataframe(df_score)

# ================= COMPARADOR DE ESTRATÉGIAS =================
st.divider()
st.subheader("⚔️ Comparador de estratégias")

estrategias = {
    "A – Mais quentes": quentes + frios[:5],
    "B – Balanceada": quentes[:5] + frios[:5],
    "C – Mais frios": frios + quentes[:5]
}

resultado_estrategias = []

for nome, base in estrategias.items():
    if len(set(base)) < 15:
        continue

    jogos_gerados = gerar_jogos(
        list(set(base)),
        qtd_jogos,
        soma_min,
        soma_max,
        pares_min,
        pares_max
    )

    medias = []
    for j in jogos_gerados:
        sim = simular_jogo(j, jogos)
        medias.append(sim["Média acertos"])

    resultado_estrategias.append({
        "Estratégia": nome,
        "Jogos válidos": len(jogos_gerados),
        "Média geral de acertos": round(np.mean(medias), 2) if medias else 0
    })

df_comp = pd.DataFrame(resultado_estrategias)
st.dataframe(df_comp)

# ================= GERAÇÃO FINAL =================
st.divider()
st.subheader("🎯 Geração estratégica de jogos (decisão assistida)")

base_final = sorted(set(quentes + frios))

if len(base_final) < 15:
    st.error("Base insuficiente. Ajuste quentes/frios.")
    st.stop()

jogos_finais = gerar_jogos(
    base_final,
    qtd_jogos,
    soma_min,
    soma_max,
    pares_min,
    pares_max
)

resumo = []
for i, jogo in enumerate(jogos_finais, 1):
    sim = simular_jogo(jogo, jogos)
    resumo.append({
        "Jogo": i,
        "Números": jogo,
        **sim
    })

df_final = pd.DataFrame(resumo).sort_values("Média acertos", ascending=False)
st.dataframe(df_final)

st.caption("⚠️ Estatística aplicada. Sem promessas. IA probabilística e decisão assistida.")
