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
# 🔹 Repositório: robsonsucessoagoraloto/aplicativo-loto-facil
# 🔹 Arquivo: lotofacil_resultados.csv
# 🔹 Branch: main
# 🔹 OBS: se a base cair, o sistema usa CSV manual sem erro visual

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
    st.info("Base online indisponível no momento. Envie um CSV manualmente.")
    arquivo = st.file_uploader("Upload CSV", type=["csv"])
    if arquivo:
        df = pd.read_csv(arquivo)
        df.columns = [c.lower() for c in df.columns]

if df is None:
    st.stop()

st.dataframe(df.tail())

# ======================================================
# ANÁLISE
# ======================================================
jogos = extrair_dezenas(df)
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
    st.stop()

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

# ======================================================
# SIMULAÇÃO HISTÓRICA
# ======================================================
st.divider()
st.subheader("🧪 Simulação histórica")

df_sim = testar_historico(jogos_gerados, jogos[-janela:])
st.dataframe(df_sim)

st.caption("⚠️ Estatística aplicada. Sem promessas. Decisão assistida.")
# ======================================================
# ANÁLISE DE BOLÃO (15 a 20 dezenas)
# ======================================================
st.divider()
st.subheader("🎯 Análise de Bolão")

st.write(
    "Informe um bolão com **15 a 20 dezenas** (separadas por vírgula). "
    "O sistema fará análise estatística e simulação histórica."
)

entrada_bolao = st.text_input(
    "Exemplo: 1,3,5,6,7,9,10,11,12,13,14,15,17,18,20"
)

if entrada_bolao:
    try:
        bolao = sorted(
            set(int(n.strip()) for n in entrada_bolao.split(",") if n.strip())
        )

        if not (15 <= len(bolao) <= 20):
            st.error("⚠️ O bolão deve ter entre 15 e 20 dezenas.")
        elif any(n < 1 or n > 25 for n in bolao):
            st.error("⚠️ As dezenas devem estar entre 1 e 25.")
        else:
            st.success(f"Bolão válido com {len(bolao)} dezenas")

            # Classificação quente / frio / neutro
            bolao_quentes = [n for n in bolao if n in quentes]
            bolao_frios = [n for n in bolao if n in frios]
            bolao_neutros = [n for n in bolao if n not in quentes + frios]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("🔥 Quentes no bolão")
                st.write(bolao_quentes)

            with col2:
                st.subheader("❄️ Frios no bolão")
                st.write(bolao_frios)

            with col3:
                st.subheader("⚖️ Neutros no bolão")
                st.write(bolao_neutros)

            # Score médio do bolão
            score_medio = np.mean([score[n] for n in bolao])
            st.metric("📊 Score médio do bolão", round(score_medio, 4))

            # Simulação histórica
            st.subheader("🧪 Simulação histórica do bolão")

            resultados = []
            for sorteio in jogos[-janela:]:
                acertos = len(set(bolao) & set(sorteio))
                resultados.append(acertos)

            df_bolao = pd.DataFrame(resultados, columns=["Acertos"])
            distribuicao = df_bolao["Acertos"].value_counts().sort_index()

            st.write("Distribuição de acertos no histórico:")
            st.dataframe(distribuicao.rename("Ocorrências"))

            st.metric("Máximo de acertos", df_bolao["Acertos"].max())
            st.metric("Média de acertos", round(df_bolao["Acertos"].mean(), 2))

            # Comparação com jogos gerados
            st.subheader("⚔️ Comparação: Bolão vs Jogos Gerados")

            media_gerados = df_sim["Média de acertos"].mean()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Bolão (média)", round(df_bolao["Acertos"].mean(), 2))
            with col2:
                st.metric("Jogos gerados (média)", round(media_gerados, 2))

    except Exception as e:
        st.error(f"Erro ao processar bolão: {e}")
# ======================================================
# DIAGNÓSTICO TEXTUAL + ESTRATÉGIAS AVANÇADAS (CORRIGIDO)
# ======================================================
st.divider()
st.header("🧠 Diagnóstico Estatístico Inteligente")

def diagnostico_textual(jogo, quentes, frios, media_historica):
    q_quentes = len(set(jogo) & set(quentes))
    q_frios = len(set(jogo) & set(frios))

    if q_quentes >= 7 and q_frios <= 3:
        perfil = "Agressivo (predominância de números quentes)"
    elif q_frios >= 6:
        perfil = "Conservador (predominância de números frios)"
    else:
        perfil = "Equilibrado"

    return (
        f"• Números quentes: {q_quentes}\n"
        f"• Números frios: {q_frios}\n"
        f"• Perfil estatístico: {perfil}\n"
        f"• Média histórica de acertos: {media_historica:.2f}\n\n"
        "Diagnóstico baseado exclusivamente em dados históricos."
    )

# ======================================================
# COMPARADOR DE ESTRATÉGIAS A vs B vs C (ROBUSTO)
# ======================================================
st.divider()
st.header("📊 Comparador de Estratégias")

def gerar_base_estrategia(quentes, frios, tipo):
    universo = list(range(1, 26))

    if tipo == "A":  # Equilibrada
        return sorted(set(quentes + frios))
    elif tipo == "B":  # Mais quentes
        resto = [n for n in universo if n not in quentes]
        return sorted(quentes + resto[: max(0, 15 - len(quentes))])
    elif tipo == "C":  # Mais frios
        resto = [n for n in universo if n not in frios]
        return sorted(frios + resto[: max(0, 15 - len(frios))])

estrategias = {
    "A (Equilibrada)": gerar_base_estrategia(quentes, frios, "A"),
    "B (Quentes)": gerar_base_estrategia(quentes, frios, "B"),
    "C (Frios)": gerar_base_estrategia(quentes, frios, "C")
}

resultado_estrategias = []

for nome, base_est in estrategias.items():
    if len(base_est) < 15:
        continue

    jogos_est = gerar_jogos(
        base_est,
        10,
        soma_min,
        soma_max,
        pares_min,
        pares_max
    )

    sim = testar_historico(jogos_est, jogos[-janela:])

    # 🔒 Normalização segura das colunas
    sim.columns = [c.lower().strip() for c in sim.columns]

    if "média de acertos" in sim.columns:
        media = sim["média de acertos"].mean()
    elif "media de acertos" in sim.columns:
        media = sim["media de acertos"].mean()
    else:
        continue  # não quebra o app

    resultado_estrategias.append({
        "Estratégia": nome,
        "Média Histórica": round(media, 2)
    })

df_estrategias = pd.DataFrame(resultado_estrategias)

if not df_estrategias.empty:
    df_estrategias = df_estrategias.sort_values("Média Histórica", ascending=False)
    st.dataframe(df_estrategias)

    # ======================================================
    # IA ASSISTIDA — DECISÃO BASEADA EM DADOS
    # ======================================================
    st.divider()
    st.header("🤖 Decisão Assistida (IA Estatística)")

    melhor = df_estrategias.iloc[0]

    st.success(
        f"A estratégia com melhor desempenho histórico foi "
        f"**{melhor['Estratégia']}**, "
        f"com média de **{melhor['Média Histórica']} acertos**.\n\n"
        "Decisão baseada exclusivamente em simulação histórica."
    )
else:
    st.warning("Não foi possível comparar estratégias com os parâmetros atuais.")

# ======================================================
# DIAGNÓSTICO DOS JOGOS GERADOS
# ======================================================
st.divider()
st.header("📝 Diagnóstico dos Jogos Gerados")

df_sim.columns = [c.lower().strip() for c in df_sim.columns]

for i, jogo in enumerate(jogos_gerados, 1):
    linha = df_sim[df_sim["jogo"] == i]

    if not linha.empty:
        media_jogo = linha.iloc[0].get("média de acertos", 0)
    else:
        media_jogo = 0

    texto = diagnostico_textual(jogo, quentes, frios, media_jogo)

    with st.expander(f"Jogo {i} – Diagnóstico"):
        st.write(jogo)
        st.text(texto)

# ======================================================
# EXPORTAÇÃO (VALOR COMERCIAL)
# ======================================================
st.divider()
st.header("📥 Exportação de Diagnóstico")

df_export = df_sim.copy()
df_export["estratégia_recomendada"] = melhor["Estratégia"] if not df_estrategias.empty else "N/A"

csv = df_export.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Baixar diagnóstico em CSV",
    data=csv,
    file_name="diagnostico_lotofacil.csv",
    mime="text/csv"
)
# ======================================================
# 🧮 ANÁLISE DE BOLÕES (16–20 DEZENAS)
# ======================================================
import itertools

st.divider()
st.header("🧮 Análise de Bolão (16–20 dezenas)")

bolao_input = st.text_input(
    "Informe os números do bolão (ex: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)",
    ""
)

qtd_sim_bolao = st.slider(
    "Quantidade de concursos para simulação do bolão",
    50, min(1000, len(jogos)), 300
)

def parse_bolao(texto):
    try:
        nums = sorted(set(int(n) for n in texto.split(",") if n.strip().isdigit()))
        if 16 <= len(nums) <= 20 and all(1 <= n <= 25 for n in nums):
            return nums
    except Exception:
        pass
    return None

bolao = parse_bolao(bolao_input)

if bolao:
    st.success(f"Bolão válido com {len(bolao)} dezenas: {bolao}")

    combinacoes = list(itertools.combinations(bolao, 15))

    st.info(f"Total de combinações possíveis: {len(combinacoes)} jogos")

    historico_ref = jogos[-qtd_sim_bolao:]

    resultados = []
    distribuicao = Counter()

    for jogo in combinacoes:
        acertos = [len(set(jogo) & set(s)) for s in historico_ref]
        media = np.mean(acertos)
        maximo = max(acertos)

        distribuicao.update(acertos)

        resultados.append({
            "Jogo": list(jogo),
            "Média de acertos": round(media, 2),
            "Máx": maximo
        })

    df_bolao = pd.DataFrame(resultados)

    st.subheader("📊 Resultado Estatístico do Bolão")
    st.dataframe(df_bolao.sort_values("Média de acertos", ascending=False).head(10))

    st.subheader("📈 Distribuição de Acertos")
    dist_df = pd.DataFrame(
        [{"Acertos": k, "Ocorrências": v} for k, v in sorted(distribuicao.items())]
    )
    st.dataframe(dist_df)

    st.markdown(
        f"""
        **Diagnóstico do Bolão**
        - Média geral: **{df_bolao['Média de acertos'].mean():.2f}**
        - Máximo histórico observado: **{df_bolao['Máx'].max()}**
        """
    )

else:
    if bolao_input:
        st.error("Bolão inválido. Informe entre 16 e 20 números válidos (1–25).")

# ======================================================
# 🧠 MATRIZ DE COBERTURA (OTIMIZAÇÃO DO BOLÃO)
# ======================================================
st.divider()
st.header("🧠 Otimização por Matriz de Cobertura")

if bolao:
    qtd_jogos_otimizados = st.slider(
        "Quantidade de jogos otimizados",
        5, min(50, len(combinacoes)), 15
    )

    def score_cobertura(jogo, numeros_cobertos, pares_cobertos):
        score = 0
        for n in jogo:
            if n not in numeros_cobertos:
                score += 2
        for p in itertools.combinations(jogo, 2):
            if p not in pares_cobertos:
                score += 1
        return score

    jogos_restantes = combinacoes.copy()
    numeros_cobertos = set()
    pares_cobertos = set()
    selecionados = []

    while len(selecionados) < qtd_jogos_otimizados and jogos_restantes:
        melhor_jogo = max(
            jogos_restantes,
            key=lambda j: score_cobertura(j, numeros_cobertos, pares_cobertos)
        )

        selecionados.append(melhor_jogo)

        numeros_cobertos.update(melhor_jogo)
        pares_cobertos.update(itertools.combinations(melhor_jogo, 2))

        jogos_restantes.remove(melhor_jogo)

    st.subheader("🎯 Jogos Otimizados (Matriz de Cobertura)")
    for i, j in enumerate(selecionados, 1):
        st.write(f"Jogo {i}: {list(j)}")

    st.markdown(
        f"""
        **Cobertura alcançada**
        - Números cobertos: **{len(numeros_cobertos)} / {len(bolao)}**
        - Pares cobertos: **{len(pares_cobertos)}**
        """
    )

    # Exportação
    df_export_bolao = pd.DataFrame(
        {"Jogo": [list(j) for j in selecionados]}
    )

    csv_bolao = df_export_bolao.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Baixar jogos otimizados do bolão (CSV)",
        data=csv_bolao,
        file_name="bolao_otimizado_lotofacil.csv",
        mime="text/csv"
    )
