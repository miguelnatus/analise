#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import random # Adicionado para o gerador

# Importar funções do script de análise principal
from lotofacil_core_analysis import (
    load_data,
    analyze_even_odd_per_draw,
    analyze_number_frequency,
    analyze_overdue_numbers,
    analyze_repeated_numbers,
    generate_numbers_frequency_based, # Nova importação
    generate_numbers_even_odd_based,  # Nova importação
    generate_numbers_overdue_based,   # Nova importação
    generate_numbers_repeated_based   # Nova importação
)

st.set_page_config(layout="wide")

# --- Funções de Plotagem Adaptadas para Streamlit ---
def plot_number_frequency_st(number_counts):
    sorted_counts = sorted(number_counts.items())
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
    count_pares_por_sorteio = df_even_odd["Pares"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=count_pares_por_sorteio.index, y=count_pares_por_sorteio.values, ax=ax, palette="coolwarm")
    ax.set_title("Distribuição da Quantidade de Números Pares por Sorteio")
    ax.set_xlabel("Quantidade de Números Pares no Sorteio")
    ax.set_ylabel("Número de Sorteios")
    plt.tight_layout()
    st.pyplot(fig)

def plot_repeated_numbers_distribution_st(df_repeated):
    if df_repeated.empty or "Repetidos" not in df_repeated.columns:
        st.write("Não há dados suficientes para exibir o gráfico de números repetidos.")
        return
    count_repetidos = df_repeated["Repetidos"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=count_repetidos.index, y=count_repetidos.values, ax=ax, palette="mako")
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
    st.error("Arquivo lotofacil.csv não encontrado. Verifique o caminho no script `lotofacil_core_analysis.py` ou coloque o arquivo no diretório correto.")
    st.stop()
except Exception as e:
    st.error(f"Ocorreu um erro ao carregar os dados: {e}")
    st.stop()

st.sidebar.header("Configurações")

# Opções de Análise ou Geração
app_mode = st.sidebar.selectbox(
    "Escolha o modo:",
    [
        "Análise Estatística",
        "Gerador de Jogos"
    ]
)

if app_mode == "Análise Estatística":
    st.sidebar.subheader("Opções de Análise")
    analysis_type = st.sidebar.selectbox(
        "Escolha o tipo de análise:",
        [
            "Frequência dos Números",
            "Distribuição Pares/Ímpares por Sorteio",
            "Números Atrasados (Ciclos)",
            "Números Repetidos do Sorteio Anterior"
        ]
    )

    if analysis_type == "Frequência dos Números":
        st.header("Frequência dos Números Sorteados")
        number_frequencies = analyze_number_frequency(df, dezenas_cols)
        plot_number_frequency_st(number_frequencies)
        st.subheader("Dados de Frequência (Número: Vezes Sorteado)")
        st.json(dict(sorted(number_frequencies.items())))

    elif analysis_type == "Distribuição Pares/Ímpares por Sorteio":
        st.header("Análise de Pares e Ímpares por Sorteio")
        even_odd_df = analyze_even_odd_per_draw(df, dezenas_cols)
        plot_even_odd_distribution_st(even_odd_df)
        st.subheader("Estatísticas da Quantidade de Pares por Sorteio")
        st.dataframe(even_odd_df["Pares"].value_counts(normalize=True).sort_index().reset_index(name="Percentual").style.format({"Percentual": "{:.2%}"}))
        st.subheader("Dados Detalhados (Primeiros 100 Sorteios)")
        st.dataframe(even_odd_df.head(100))

    elif analysis_type == "Números Atrasados (Ciclos)":
        st.header("Análise de Números Atrasados (Ciclos)")
        num_draws_option_cycles = st.sidebar.number_input(
            "Considerar quantos sorteios anteriores para análise de atraso? (0 para todos)", 
            min_value=0, 
            value=100, 
            step=10,
            key="cycles_draws_option"
        )
        num_draws_to_consider_cycles = None if num_draws_option_cycles == 0 else num_draws_option_cycles
        
        if num_draws_to_consider_cycles:
            st.write(f"Analisando atraso nos últimos {num_draws_to_consider_cycles} sorteios.")
        else:
            st.write("Analisando atraso em todos os sorteios disponíveis.")
            
        overdue_numbers_data = analyze_overdue_numbers(df, dezenas_cols, num_draws_to_consider=num_draws_to_consider_cycles)
        plot_overdue_numbers_st(overdue_numbers_data)
        st.subheader("Dados de Atraso (Número: Sorteios Atrasado)")
        st.json(dict(sorted(overdue_numbers_data.items(), key=lambda item: item[1], reverse=True)))

    elif analysis_type == "Números Repetidos do Sorteio Anterior":
        st.header("Análise de Números Repetidos do Sorteio Anterior")
        repeated_numbers_df = analyze_repeated_numbers(df, dezenas_cols)
        if not repeated_numbers_df.empty:
            plot_repeated_numbers_distribution_st(repeated_numbers_df)
            st.subheader("Estatísticas da Quantidade de Números Repetidos")
            st.dataframe(repeated_numbers_df["Repetidos"].value_counts(normalize=True).sort_index().reset_index(name="Percentual").style.format({"Percentual": "{:.2%}"}))
            st.subheader("Dados Detalhados (Primeiros 100 Sorteios com Análise)")
            st.dataframe(repeated_numbers_df.head(100))
        else:
            st.write("Não há dados suficientes para a análise de números repetidos (precisa de pelo menos 2 sorteios).")

elif app_mode == "Gerador de Jogos":
    st.header("Gerador de Jogos da Lotofácil")
    st.sidebar.subheader("Opções do Gerador")
    generator_type = st.sidebar.selectbox(
        "Escolha o critério de geração:",
        [
            "Baseado na Frequência",
            "Baseado em Pares/Ímpares",
            "Baseado em Números Atrasados",
            "Baseado em Números Repetidos"
        ]
    )

    num_games_to_generate = st.sidebar.number_input("Quantos jogos gerar?", min_value=1, max_value=10, value=1, step=1, key="num_games")

    generated_games_list = []

    if generator_type == "Baseado na Frequência":
        st.subheader("Gerar Jogo Baseado na Frequência dos Números")
        if st.button("Gerar Jogo(s) por Frequência"):
            number_frequencies = analyze_number_frequency(df, dezenas_cols)
            for _ in range(num_games_to_generate):
                generated_games_list.append(generate_numbers_frequency_based(number_frequencies))

    elif generator_type == "Baseado em Pares/Ímpares":
        st.subheader("Gerar Jogo Baseado na Quantidade de Pares e Ímpares")
        num_evens = st.sidebar.slider("Quantidade de números pares:", min_value=0, max_value=12, value=7, key="gen_evens") # Max 12 pares
        num_odds = 15 - num_evens
        st.sidebar.write(f"Quantidade de números ímpares: {num_odds}")
        if st.button("Gerar Jogo(s) por Pares/Ímpares"):
            if num_odds > 13: # Max 13 ímpares
                st.error("Configuração de pares/ímpares inválida (máximo de 13 ímpares).")
            else:
                try:
                    for _ in range(num_games_to_generate):
                        generated_games_list.append(generate_numbers_even_odd_based(num_evens, num_odds))
                except ValueError as e:
                    st.error(f"Erro ao gerar: {e}")

    elif generator_type == "Baseado em Números Atrasados":
        st.subheader("Gerar Jogo Baseado em Números Atrasados")
        num_draws_option_overdue_gen = st.sidebar.number_input(
            "Considerar quantos sorteios anteriores para basear o atraso? (0 para todos)", 
            min_value=0, 
            value=100, 
            step=10,
            key="overdue_gen_draws_option"
        )
        top_n_overdue_option = st.sidebar.slider(
            "Priorizar quantos dos números mais atrasados? (0 para usar todos com peso)", 
            min_value=0, max_value=25, value=15, key="top_n_overdue_gen"
        )
        num_draws_to_consider_overdue_gen = None if num_draws_option_overdue_gen == 0 else num_draws_option_overdue_gen
        top_n_overdue_val = None if top_n_overdue_option == 0 else top_n_overdue_option

        if st.button("Gerar Jogo(s) por Atraso"):
            overdue_data = analyze_overdue_numbers(df, dezenas_cols, num_draws_to_consider=num_draws_to_consider_overdue_gen)
            try:
                for _ in range(num_games_to_generate):
                    generated_games_list.append(generate_numbers_overdue_based(overdue_data, top_n_overdue=top_n_overdue_val))
            except ValueError as e:
                st.error(f"Erro ao gerar: {e}")

    elif generator_type == "Baseado em Números Repetidos":
        st.subheader("Gerar Jogo Baseado em Números Repetidos do Último Sorteio")
        if len(df) < 1:
            st.warning("Não há dados suficientes para obter o último sorteio.")
        else:
            max_repeat = min(15, len(set(df.iloc[-1][dezenas_cols].values)))
            num_to_repeat_val = st.sidebar.slider(
                "Quantos números repetir do último sorteio?", 
                min_value=0, max_value=max_repeat, value=min(8, max_repeat), key="num_repeat_gen"
            )
            if st.button("Gerar Jogo(s) por Repetição"):
                try:
                    for _ in range(num_games_to_generate):
                        generated_games_list.append(generate_numbers_repeated_based(df, dezenas_cols, num_to_repeat_val))
                except ValueError as e:
                    st.error(f"Erro ao gerar: {e}")
    
    if generated_games_list:
        st.write("--- Jogos Gerados ---")
        for i, game in enumerate(generated_games_list):
            # CORREÇÃO: Converter cada número para int antes de exibir
            cleaned_game = sorted([int(num) for num in game])
            st.markdown(f"**Jogo {i+1}:** `{cleaned_game}`")

st.sidebar.info(
    """Esta aplicação analisa dados históricos da Lotofácil e pode gerar sugestões de jogos.
    Lembre-se que resultados de loterias são aleatórios e análises passadas ou jogos gerados não garantem resultados futuros."""
)

