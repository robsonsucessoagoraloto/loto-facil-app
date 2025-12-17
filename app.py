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

    if arquivo is not None:
        df = pd.read_csv(arquivo)

        st.success("Arquivo importado com sucesso!")
        st.dataframe(df)

        st.subheader("📊 Análise de Frequência das Dezenas")

        colunas_dezenas = [col for col in df.columns if col.startswith("dezena")]

        todas_dezenas = df[colunas_dezenas].values.flatten()

        frequencia = (
            pd.Series(todas_dezenas)
            .value_counts()
            .sort_index()
        )

        tabela_freq = frequencia.reset_index()
        tabela_freq.columns = ["Dezena", "Frequência"]

        st.dataframe(tabela_freq)

        st.subheader("🔥 Números mais frequentes")
        st.dataframe(tabela_freq.sort_values("Frequência", ascending=False))

        st.subheader("❄️ Números menos frequentes")
        st.dataframe(tabela_freq.sort_values("Frequência", ascending=True))
