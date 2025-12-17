import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Aplicativo Loto Fácil",
    page_icon="🎯",
    layout="centered"
)

st.title("Aplicativo Loto Fácil 🎯")
st.write("Bem-vindo!")
st.write("Aqui vamos analisar resultados e gerar jogos da Lotofácil.")

st.divider()

st.sidebar.title("Menu")

opcao = st.sidebar.selectbox(
    "Escolha uma opção:",
    ["Início", "Importar Resultados"]
)

if opcao == "Início":
    st.subheader("Próximo passo:")
    st.write("• Importar resultados")
    st.write("• Analisar números quentes e frios")
    st.write("• Gerar combinações")

elif opcao == "Importar Resultados":
    st.subheader("Importar resultados da Lotofácil")
    arquivo = st.file_uploader(
        "Envie um arquivo CSV com os resultados",
        type=["csv"]
    )

    if arquivo:
        df = pd.read_csv(arquivo, sep=",", engine="python")
        st.subheader("📊 Análise de Frequência das Dezenas")

# seleciona apenas as colunas das dezenas
colunas_dezenas = [col for col in df.columns if col.startswith("dezena")]

# transforma todas as dezenas em uma única série
todas_dezenas = df[colunas_dezenas].values.flatten()

# conta frequência
frequencia = pd.Series(todas_dezenas).value_counts().sort_index()

# cria tabela
tabela_freq = frequencia.reset_index()
tabela_freq.columns = ["Dezena", "Frequência"]

# mostra tabela
st.dataframe(tabela_freq)

# números quentes e frios
st.subheader("🔥 Números mais frequentes")
st.write(tabela_freq.sort_values("Frequência", ascending=False).head(5))

st.subheader("❄️ Números menos frequentes")
st.write(tabela_freq.sort_values("Frequência", ascending=True).head(5))

st.success("Arquivo importado com sucesso!")
st.dataframe(df)
