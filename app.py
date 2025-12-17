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

        # --- ANÁLISE DE FREQUÊNCIA ---
        st.subheader("📊 Análise de Frequência das Dezenas")

        # Seleciona apenas colunas que começam com 'dezena'
        colunas_dezenas = [col for col in df.columns if col.startswith("dezena")]

        # Junta todas as dezenas em uma única lista
        todas_dezenas = df[colunas_dezenas].values.flatten()

        # Calcula frequência
        frequencia = (
            pd.Series(todas_dezenas)
            .value_counts()
            .sort_index()
        )

        tabela_freq = frequencia.reset_index()
        tabela_freq.columns = ["Dezena", "Frequência"]

        # --- RESULTADOS ---
        st.subheader("🔥 Números mais frequentes")
        st.dataframe(
            tabela_freq.sort_values("Frequência", ascending=False)
        )

        st.subheader("❄️ Números menos frequentes")
        st.dataframe(
            tabela_freq.sort_values("Frequência", ascending=True)
        )

        # --- ANÁLISE DE FREQUÊNCIA ---
        todas_dezenas = df.values.flatten()
        tabela_freq = (
            pd.Series(todas_dezenas)
            .value_counts()
            .reset_index()
        )
        tabela_freq.columns = ["Número", "Frequência"]

        st.subheader("🔥 Números mais frequentes")
        st.dataframe(tabela_freq.sort_values("Frequência", ascending=False))

        st.subheader("❄️ Números menos frequentes")
        st.dataframe(tabela_freq.sort_values("Frequência", ascending=True))

        st.divider()

        # --- GERAÇÃO DE JOGOS ESTRATÉGICOS ---
        st.subheader("🎯 Gerar jogos estratégicos")

        qtd_jogos = st.slider(
            "Quantos jogos deseja gerar?",
            min_value=1,
            max_value=20,
            value=5
        )

        if st.button("Gerar jogos"):
            quentes = tabela_freq.sort_values("Frequência", ascending=False)["Número"].head(15).tolist()
            frios = tabela_freq.sort_values("Frequência", ascending=True)["Número"].head(10).tolist()

            jogos = []

            for _ in range(qtd_jogos):
                jogo = set()

                # 10 números quentes
                jogo.update(pd.Series(quentes).sample(10).tolist())

                # 5 números frios
                jogo.update(pd.Series(frios).sample(5).tolist())

                # Garantia de 15 dezenas
                while len(jogo) < 15:
                    jogo.add(pd.Series(quentes).sample(1).iloc[0])

                jogos.append(sorted(jogo))

            st.success("Jogos gerados com base em quentes + frios")

            for i, jogo in enumerate(jogos, 1):
                st.write(f"Jogo {i}: {jogo}")
