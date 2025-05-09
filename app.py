# app.py - Dashboard Lotofácil com Streamlit
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
from collections import Counter
from scipy.stats import chisquare

# Configuração da página
st.set_page_config(page_title="Dashboard Lotofácil", layout="wide")

# 1) Carregar dados
@st.cache_data
def load_data(path='lotofacil.csv'):
    df = pd.read_csv(path)
    df['Concurso'] = df['Concurso'].astype(int)
    return df

df = load_data()
cols = [f'Dezena{i}' for i in range(1,16)]

# Sidebar de navegação
st.sidebar.title("Análises")
section = st.sidebar.radio("Escolha a seção:", [
    'Frequência', 'Primos', 'Atraso', 'Média Móvel', 'Pares & Trincas'
])

# 2) Frequência de dezenas
if section == 'Frequência':
    st.title("Frequência de cada dezena")
    all_nums = df[cols].values.flatten()
    freq = pd.Series(all_nums).value_counts().sort_index()
    st.bar_chart(freq)
    st.dataframe(freq.rename_axis('Número').reset_index(name='Frequência'))

# 3) Análise de primos
elif section == 'Primos':
    st.title("Análise de Números Primos")
    primos = {str(n).zfill(2) for n in [2,3,5,7,11,13,17,19,23]}
    all_nums = df[cols].values.flatten()
    freq = pd.Series(all_nums).value_counts().sort_index()
    prime_count = freq[freq.index.isin(primos)].sum()
    nonprime_count = freq[~freq.index.isin(primos)].sum()
    n = prime_count + nonprime_count
    chi2, p = chisquare(f_obs=[prime_count, nonprime_count], f_exp=[n*len(primos)/25, n*(25-len(primos))/25])
    st.markdown(f"**Total de primos:** {prime_count}  ")
    st.markdown(f"**Total de não-primos:** {nonprime_count}  ")
    st.markdown(f"**Qui-quadrado:** {chi2:.2f}, **p-value:** {p:.3f}")
    labels = ['Primos', 'Não-Primos']
    fig, ax = plt.subplots()
    ax.pie([prime_count, nonprime_count], labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

# 4) Análise de atraso
elif section == 'Atraso':
    st.title("Análise de Atraso (Ciclos)")
    df_sorted = df.sort_values('Concurso')
    delays = {}
    for num in range(1,26):
        num_str = str(num).zfill(2)
        mask = df_sorted[cols].eq(num_str).any(axis=1)
        if mask.any():
            last_idx = mask[mask].index[-1]
            pos = df_sorted.index.get_loc(last_idx)
            delay = len(df_sorted) - 1 - pos
        else:
            delay = len(df_sorted)
        delays[num] = delay
    delay_series = pd.Series(delays).sort_values(ascending=False)
    st.bar_chart(delay_series)
    st.dataframe(delay_series.rename_axis('Número').reset_index(name='Concursos de Atraso'))

# 5) Média móvel
elif section == 'Média Móvel':
    st.title("Média Móvel de uma Dezena")
    dez = st.selectbox("Selecione a dezena:", list(range(1,26)))
    dez_str = str(dez).zfill(2)
    df_sorted = df.sort_values('Concurso')
    df_sorted[f'Tem_{dez_str}'] = df_sorted[cols].eq(dez_str).any(axis=1).astype(int)
    df_sorted['MM'] = df_sorted[f'Tem_{dez_str}'].rolling(50).mean()
    fig, ax = plt.subplots()
    ax.plot(df_sorted['Concurso'], df_sorted['MM'])
    ax.set_xlabel('Concurso')
    ax.set_ylabel('Probabilidade Estimada')
    st.pyplot(fig)

# 6) Pares & Trincas
elif section == 'Pares & Trincas':
    st.title("Pares e Trincas Mais Comuns")
    all_rows = df[cols].astype(str).values
    # Pares
    pair_counts = Counter()
    for row in all_rows:
        for a, b in itertools.combinations(row, 2):
            pair = tuple(sorted((a, b)))
            pair_counts[pair] += 1
    top_pairs = pd.DataFrame(pair_counts.most_common(10), columns=['Par', 'Frequência'])
    st.subheader("Top 10 Pares")
    st.dataframe(top_pairs)
    # Trincas
    triple_counts = Counter()
    for row in all_rows:
        for trip in itertools.combinations(row, 3):
            triple = tuple(sorted(trip))
            triple_counts[triple] += 1
    top_triples = pd.DataFrame(triple_counts.most_common(10), columns=['Trinca', 'Frequência'])
    st.subheader("Top 10 Trincas")
    st.dataframe(top_triples)

# Footer
st.markdown("---")
st.markdown("_Dashboard implementado com Streamlit_  `streamlit run app.py`")
