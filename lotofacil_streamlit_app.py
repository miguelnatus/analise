#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import random

# Importar funções do script de análise principal
from lotofacil_core_analysis import (
    load_data,
    analyze_even_odd_per_draw,
    analyze_primes_per_draw,
    analyze_number_frequency,
    analyze_overdue_numbers,
    analyze_repeated_numbers,
    generate_numbers_frequency_based,
    generate_numbers_even_odd_based,
    generate_numbers_prime_based,
    generate_numbers_overdue_based,
    generate_numbers_repeated_based,
    PRIMES_UP_TO_25
)

st.set_page_config(page_title="Lotofácil Dashboard", layout="wide")

# --- Funções de Plotagem Adaptadas para Streamlit ---
def plot_number_frequency_st(number_counts):
    sorted_counts = sorted(number_counts.items(), key=lambda x: int(x[0]))
    numbers = [item[0] for item in sorted_counts]
    counts = [item[1] for item in sorted_counts]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=numbers, y=counts, ax=ax, palette="viridis")
    ax.set_title("Frequência dos Números na Lotofácil")
    ax.set_xlabel("Número")
    ax.set_ylabel("Frequência")
    ax.tick_params(axis="x", rotation=90)
    plt.tight_layout()
    st.pyplot(fig)


def plot_even_odd_distribution_st(df_even_odd):
    count_data = df_even_odd["Pares"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=count_data.index, y=count_data.values, ax=ax, palette="coolwarm")
    ax.set_title("Distribuição da Quantidade de Números Pares por Sorteio")
    ax.set_xlabel("Quantidade de Números Pares no Sorteio")
    ax.set_ylabel("Número de Sorteios")
    plt.tight_layout()
    st.pyplot(fig)


def plot_primes_distribution_st(df_primes):
    count_data = df_primes["Primos"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=count_data.index, y=count_data.values, ax=ax, palette="crest")
    ax.set_title("Distribuição da Quantidade de Números Primos por Sorteio")
    ax.set_xlabel("Quantidade de Números Primos no Sorteio")
    ax.set_ylabel("Número de Sorteios")
    plt.tight_layout()
    st.pyplot(fig)


def plot_repeated_numbers_distribution_st(df_repeated):
    if df_repeated.empty or "Repetidos" not in df_repeated.columns:
        st.write("Não há dados suficientes para exibir o gráfico de números repetidos.")
        return
    count_data = df_repeated["Repetidos"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=count_data.index, y=count_data.values, ax=ax, palette="mako")
    ax.set_title("Distribuição da Quantidade de Números Repetidos do Sorteio Anterior")
    ax.set_xlabel("Quantidade de Números Repetidos")
    ax.set_ylabel("Número de Sorteios")
    plt.tight_layout()
    st.pyplot(fig)


def plot_overdue_numbers_st(overdue_counts):
    sorted_overdue = sorted(overdue_counts.items(), key=lambda item: item[1], reverse=True)
    numbers = [item[0] for item in sorted_overdue]
    cycles = [item[1] for item in sorted_overdue]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=numbers, y=cycles, ax=ax, palette="rocket")
    ax.set_title("Números Mais Atrasados (Ciclos)")
    ax.set_xlabel("Número")
    ax.set_ylabel("Número de Sorteios Atrasado")
    ax.tick_params(axis="x", rotation=90)
    plt.tight_layout()
    st.pyplot(fig)


# --- Interface Streamlit ---
st.title("Análise Estatística e Gerador de Jogos da Lotofácil")

# Carregar dados
try:
    df, dezenas_cols = load_data()
    st.success("Dados carregados com sucesso!")
    st.write(f"{len(df)} sorteios carregados após limpeza de dados.")
except FileNotFoundError:
    st.error("Arquivo lotofacil.csv não encontrado. Verifique o caminho no core analysis.")
    st.stop()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

st.sidebar.header("Configurações")
app_mode = st.sidebar.selectbox(
    "Escolha o modo:",
    ["Análise Estatística", "Gerador de Jogos"]
)

# --- Análise Estatística ---
if app_mode == "Análise Estatística":
    st.sidebar.subheader("Opções de Análise")
    analysis_type = st.sidebar.selectbox(
        "Tipo de análise:",
        [
            "Frequência dos Números",
            "Distribuição Pares/Ímpares",
            "Distribuição de Primos",
            "Números Atrasados",
            "Números Repetidos"
        ]
    )

    if analysis_type == "Frequência dos Números":
        st.header("Frequência dos Números Sorteados")
        freqs = analyze_number_frequency(df, dezenas_cols)
        plot_number_frequency_st(freqs)
        st.dataframe(pd.DataFrame(sorted(freqs.items()), columns=["Número","Frequência"]))

    elif analysis_type == "Distribuição Pares/Ímpares":
        st.header("Distribuição Pares/Ímpares por Sorteio")
        eo_df = analyze_even_odd_per_draw(df, dezenas_cols)
        plot_even_odd_distribution_st(eo_df)
        st.dataframe(eo_df.head(100))

    elif analysis_type == "Distribuição de Primos":
        st.header("Distribuição de Primos por Sorteio")
        primes_df = analyze_primes_per_draw(df, dezenas_cols)
        plot_primes_distribution_st(primes_df)
        st.dataframe(primes_df.head(100))

    elif analysis_type == "Números Atrasados":
        st.header("Análise de Números Atrasados")
        draws = st.sidebar.number_input("Considerar quantos concursos? (0 para todos)", min_value=0, value=100, step=10)
        num_draws = None if draws == 0 else draws
        overdue = analyze_overdue_numbers(df, dezenas_cols, num_draws)
        plot_overdue_numbers_st(overdue)
        st.dataframe(pd.DataFrame(sorted(overdue.items(), key=lambda x: x[1], reverse=True), columns=["Número","Atraso"]))

    elif analysis_type == "Números Repetidos":
        st.header("Números Repetidos do Sorteio Anterior")
        rep_df = analyze_repeated_numbers(df, dezenas_cols)
        plot_repeated_numbers_distribution_st(rep_df)
        st.dataframe(rep_df.head(100))

# --- Gerador de Jogos ---
elif app_mode == "Gerador de Jogos":
    st.sidebar.subheader("Opções de Geração")
    generator_type = st.sidebar.selectbox(
        "Critério de geração:",
        [
            "Frequência",
            "Pares/Ímpares",
            "Primos",
            "Atrasados",
            "Repetidos"
        ]
    )
    num_games = st.sidebar.number_input("Quantos jogos?", min_value=1, max_value=10, value=1)
    games = []

    if generator_type == "Frequência":
        if st.button("Gerar por Frequência"):
            freq_counts = analyze_number_frequency(df, dezenas_cols)
            for _ in range(num_games):
                games.append(generate_numbers_frequency_based(freq_counts))

    elif generator_type == "Pares/Ímpares":
        evens = st.sidebar.slider("Qtd. de pares", 0, 12, 7)
        odds = 15 - evens
        st.sidebar.write(f"Ímpares: {odds}")
        if st.button("Gerar por Pares/Ímpares"):
            for _ in range(num_games):
                games.append(generate_numbers_even_odd_based(evens, odds))

    elif generator_type == "Primos":
        max_pr = len(PRIMES_UP_TO_25)
        prions = st.sidebar.slider("Qtd. de primos", 0, max_pr, min(4, max_pr))
        st.sidebar.write(f"Não-primos: {15-prions}")
        if st.button("Gerar por Primos"):
            for _ in range(num_games):
                games.append(generate_numbers_prime_based(prions))

    elif generator_type == "Atrasados":
        draws_ov = st.sidebar.number_input("Concursos para atraso (0=p/ todos)", 0, 1000, 100)
        topn = st.sidebar.slider("Top N atrasados", 0, 25, 15)
        num_draws_ov = None if draws_ov == 0 else draws_ov
        top_val = None if topn == 0 else topn
        if st.button("Gerar por Atraso"):
            od = analyze_overdue_numbers(df, dezenas_cols, num_draws_ov)
            for _ in range(num_games):
                games.append(generate_numbers_overdue_based(od, top_n_overdue=top_val))

    elif generator_type == "Repetidos":
        st.sidebar.markdown("**Repetição Padrão**: geralmente 10 ou 11 números do último sorteio")
        use_def = st.sidebar.checkbox("Usar repetição padrão (10 ou 11)")
        last_nums = set(df.iloc[-1][dezenas_cols].values)
        max_rep = min(15, len(last_nums))
        if use_def:
            rep = random.choice([n for n in (10, 11) if n <= max_rep])
            st.sidebar.write(f"Repetir {rep} números (padrão)")
        else:
            rep = st.sidebar.slider("Qtd. a repetir", 0, max_rep, min(8, max_rep))
        if st.button("Gerar por Repetidos"):
            for _ in range(num_games):
                games.append(generate_numbers_repeated_based(df, dezenas_cols, rep))

    if games:
        st.header("Jogos Gerados")
        for idx, g in enumerate(games, start=1):
            # converter numpy types para int puro
            numbers = sorted(int(x) for x in g)
            st.markdown(f"**Jogo {idx}:** {numbers}")

st.sidebar.info(
    "Esta aplicação analisa dados históricos e gera sugestões. "
    "Loterias são aleatórias, jogue com responsabilidade."
)
