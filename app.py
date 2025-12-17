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

        st.success("Arquivo importado com sucesso!")
        st.dataframe(df)
