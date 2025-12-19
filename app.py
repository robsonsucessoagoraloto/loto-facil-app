import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

# ======================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================
st.set_page_config(
    page_title="Lotofácil – Inteligência Estatística",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Lotofácil – Inteligência Estatística")
st.caption("Probabilidade empírica • filtros inteligentes • decisão assistida")

# ======================================================
# BASE ONLINE (CSV AUTOMÁTICO – GITHUB RAW)
# ======================================================
URL_BASE_ONLINE = "https://raw.githubusercontent.com/robsonsucessoagoraloto/aplicativo-loto-facil/main/lotofacil_resultados.csv"

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

def frequencia_absoluta(jogos):
    cont = Counter()
    for j in jogos:
        cont.update(j)
    return cont

def score_por_numero(freq, total):
    return {n: freq.get(n, 0) / total for n in range(1, 26)}

def classificar_quentes_frios(score, n_quentes, n_frios):
    ranking = sorted(score.items(), key=lambda x: x[1], reverse=True)
    quentes = [n for n, _ in ranking[:n_quentes]]
    frios = [n for n, _ in ranking[-n_frios:]]
    return quentes, frios

def gerar_jogos(base, qtd, soma_min, soma_max, pares_min, pares_max):
    jogos = []
    tentativas = 0

    while len(jogos) < qtd and tentativas < qtd * 2000:
        jogo = sorted(int(n) for n in np.random.choice(base, 15, replace=False))
        soma = sum(jogo)
        pares = sum(1 for n in jogo if n % 2 == 0)

        if soma_min <= soma <= soma_max and pares_min <= pares <= pares_max:
            if jogo not in jogos:
                jogos.append(jogo)

        tentativas += 1

    return jogos

def testar_historico(jogos, historico):
    dados = []
    for i, jogo in enumerate(jogos, 1):
        acertos = [len(set(jogo) & set(s)) for s in historico]
        dados.append({
            "Jogo": i,
            "Média de acertos": round(np.mean(acertos), 2),
            "Máx": max(acertos),
            "Min": min(acertos)
        })
    return pd.DataFrame(dados)

def simular_bolao(bolao, historico):
    acertos = [len(set(bolao) & set(s)) for s in historico]
    return {
        "Média": round(np.mean(acertos), 2),
        "Máx": max(acertos),
        "Min": min(acertos),
        "Distribuição": Counter(acertos)
    }

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.header("⚙️ Configurações")

qtd_jogos = st.sidebar.slider("Quantidade de jogos", 1, 50, 20)
janela = st.sidebar.slider("Janela histórica (concursos)", 50, 3000, 300)

soma_min = st.sidebar.slider("Soma mínima", 150, 300, 190)
soma_max = st.sidebar.slider("Soma máxima", 150, 300, 240)

pares_min = st.sidebar.slider("Pares mínimos", 4, 10, 6)
pares_max = st.sidebar.slider("Pares máximos", 4, 10, 9)

qtd_quentes = st.sidebar.slider("Qtd números quentes", 4, 15, 8)
qtd_frios = st.sidebar.slider("Qtd números frios", 4, 15, 7)

# ======================================================
# CARREGAMENTO DA BASE
# ======================================================
st.subheader("📥 Base de resultados")

df = carregar_base_online()

if df is not None:
    st.success(f"Base online carregada ({len(df)} concursos)")
else:
    st.info("Base online indisponível. Envie um CSV manualmente.")
    arquivo = st.file_uploader("Upload CSV", type=["csv"])
    if arquivo:
        df = pd.read_csv(arquivo)
        df.columns = [c.lower() for c in df.columns]

if df is None:
    st.stop()

st.dataframe(df.tail())

# ======================================================
# ANÁLISE GLOBAL
# ======================================================
jogos = extrair_dezenas(df)
freq = frequencia_absoluta(jogos)
score = score_por_numero(freq, len(jogos))

quentes, frios = classificar_quentes_frios(score, qtd_quentes, qtd_frios)
base = sorted(set(quentes + frios))

st.divider()
st.subheader("📊 Ranking probabilístico")

df_score = pd.DataFrame({
    "Número": list(score.keys()),
    "Score": list(score.values())
}).sort_values("Score", ascending=False)

st.dataframe(df_score)

# ======================================================
# GERAÇÃO DE JOGOS
# ======================================================
st.divider()
st.subheader("🎯 Geração estratégica")

if len(base) < 15:
    st.warning("Base insuficiente. Ajuste quentes/frios.")
else:
    jogos_gerados = gerar_jogos(
        base,
        qtd_jogos,
        soma_min,
        soma_max,
        pares_min,
        pares_max
    )

    st.success(f"{len(jogos_gerados)} jogos gerados")

    for i, j in enumerate(jogos_gerados, 1):
        st.write(f"Jogo {i}: {j}")

    st.subheader("🧪 Simulação histórica dos jogos gerados")
    df_sim = testar_historico(jogos_gerados, jogos[-janela:])
    st.dataframe(df_sim)

# ======================================================
# 🆕 ANÁLISE DE BOLÃO (15–20 DEZENAS)
# ======================================================
st.divider()
st.subheader("🎯 Análise de Bolão (15 a 20 dezenas)")

entrada = st.text_input(
    "Digite os números do bolão separados por vírgula",
    placeholder="Ex: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"
)

if entrada:
    try:
        bolao = sorted(set(int(n) for n in entrada.split(",")))

        if not (15 <= len(bolao) <= 20):
            st.error("O bolão deve ter entre 15 e 20 números.")
        else:
            quentes_b = [n for n in bolao if n in quentes]
            frios_b = [n for n in bolao if n in frios]
            neutros_b = [n for n in bolao if n not in quentes_b + frios_b]

            score_medio = round(np.mean([score[n] for n in bolao]), 4)

            st.success("Bolão analisado com sucesso")
            st.write(f"🔥 Quentes: {len(quentes_b)} → {quentes_b}")
            st.write(f"❄️ Frios: {len(frios_b)} → {frios_b}")
            st.write(f"⚖️ Neutros: {len(neutros_b)} → {neutros_b}")
            st.write(f"📈 Score médio do bolão: **{score_medio}**")

            resultado = simular_bolao(bolao, jogos[-janela:])

            st.subheader("🧪 Simulação histórica do bolão")
            st.write(f"Média de acertos: **{resultado['Média']}**")
            st.write(f"Máximo: **{resultado['Máx']}**")
            st.write(f"Mínimo: **{resultado['Min']}**")

            dist_df = pd.DataFrame(
                resultado["Distribuição"].items(),
                columns=["Acertos", "Frequência"]
            ).sort_values("Acertos")

            st.dataframe(dist_df)

    except Exception:
        st.error("Erro ao interpretar o bolão.")

st.caption("⚠️ Estatística aplicada. Sem promessas. Decisão assistida.")
