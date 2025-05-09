# lotofacil_analysis.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
from collections import Counter
from scipy.stats import chisquare
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 1) Carregar dados
df = pd.read_csv('lotofacil.csv')  # ajuste o caminho se necessário

# Extrair apenas as colunas de dezenas
cols = [f'Dezena{i}' for i in range(1, 16)]
dezenas = df[cols].astype(str)

# 2) Estatísticas básicas de frequência
all_nums = dezenas.values.flatten()
freq = pd.Series(all_nums).value_counts().sort_index().astype(int)
print("=== Estatísticas Básicas ===")
print(f"Média: {freq.mean():.2f}")
print(f"Mediana: {freq.median():.2f}")
print(f"Desvio-padrão: {freq.std():.2f}\n")

# 3) Histograma de frequência
plt.figure()
freq.plot(kind='bar')
plt.title('Frequência de cada dezena')
plt.xlabel('Número')
plt.ylabel('Frequência')
plt.tight_layout()
plt.savefig('relatorios/frequencia.png')
print("Salvo: frequência por número em 'frequencia.png'\n")

# 4) Análise de números primos
print("=== Análise de Primos ===")
primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
# Converter o índice de freq (string) para numeric, ignorando erros
dates = pd.to_numeric(freq.index, errors='coerce')
freq.index = dates
# Remover quaisquer índices inválidos e converter para int
freq = freq[freq.index.notna()]
freq.index = freq.index.astype(int)

prime_count = freq.loc[freq.index.isin(primos)].sum()
nonprime_count = freq.loc[~freq.index.isin(primos)].sum()
n = prime_count + nonprime_count
print(f"Total de primos sorteados: {prime_count}")
print(f"Total de não-primos sorteados: {nonprime_count}\n")

# Teste qui-quadrado de aderência
expected = [n * len(primos) / 25, n * (25 - len(primos)) / 25]
chi2_stat, p_value = chisquare(f_obs=[prime_count, nonprime_count], f_exp=expected)
print(f"Qui-quadrado: {chi2_stat:.2f}, p-value: {p_value:.3f}\n")

# Pizza de distribuição
labels = ['primos', 'não primos']
sizes = [prime_count, nonprime_count]
plt.figure()
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
plt.title('Distribuição de Números Primos')
plt.axis('equal')
plt.savefig('relatorios/primos_dist.png')
print("Salvo: pizza de primos em 'primos_dist.png'\n")

# 5) Pares mais comuns
print("=== Pares mais comuns ===")
pair_counts = Counter()
for row in dezenas.values:
    for a, b in itertools.combinations(row, 2):
        pair = tuple(sorted((a, b)))
        pair_counts[pair] += 1
for pair, cnt in pair_counts.most_common(10):
    print(f"{pair}: {cnt} vezes")
print()

# 6) Trincas mais comuns
print("=== Trincas mais comuns ===")
triple_counts = Counter()
for row in dezenas.values:
    for trip in itertools.combinations(row, 3):
        triple = tuple(sorted(trip))
        triple_counts[triple] += 1
for tri, cnt in triple_counts.most_common(10):
    print(f"{tri}: {cnt} vezes")
print()

# 7) Tendência (média móvel)
df_sorted = df.sort_values('Concurso', ascending=True)
# criar coluna de indicação de presença da dezena 10 (exemplo)
df_sorted['Tem_10'] = df_sorted[cols].eq('10').any(axis=1).astype(int)
# média móvel de 50 concursos para a dezena 10
df_sorted['MM_10'] = df_sorted['Tem_10'].rolling(window=50).mean()
plt.figure()
plt.plot(df_sorted['Concurso'], df_sorted['MM_10'])
plt.title('Média Móvel (50) - Dezena 10')
plt.xlabel('Concurso')
plt.ylabel('Probabilidade Estimada')
plt.tight_layout()
plt.savefig('relatorios/mm_dezena10.png')
print("Salvo: média móvel em 'mm_dezena10.png'\n")

# 8) Modelo simples de previsão (Random Forest para cada dezena)
print("=== Modelo de Previsão - Dezena 10 ===")
feature_df = dezenas.shift(1).eq('10').astype(int).rename(columns=lambda c: c + '_prev')
feature_df = feature_df.iloc[1:]
X = feature_df.values
y = df_sorted['Tem_10'].iloc[1:].values

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print(f"Acurácia no teste: {accuracy_score(y_test, y_pred):.3f}")

scores = cross_val_score(clf, X, y, cv=5)
print(f"CV (5-fold) acurácia média: {scores.mean():.3f}\n")

# 9) Análise de Atraso (Ciclos)
print("=== Análise de Atraso (Ciclos) ===")
delays = {}
# Para cada número de 1 a 25, calcular concursos desde última aparição
for num in range(1, 26):
    num_str = str(num).zfill(2)
    mask = df_sorted[cols].eq(num_str).any(axis=1)
    if mask.any():
        last_idx = mask[mask].index[-1]
        pos = df_sorted.index.get_loc(last_idx)
        delay = len(df_sorted) - 1 - pos
    else:
        delay = len(df_sorted)
    delays[num] = delay
# Transformar em Series ordenada
delay_series = pd.Series(delays).sort_values(ascending=False)
print(delay_series.to_string())
# Plot de atrasos
plt.figure()
delay_series.plot(kind='bar')
plt.title('Atraso em Número de Concursos desde Última Aparição')
plt.xlabel('Número')
plt.ylabel('Concursos de Atraso')
plt.tight_layout()
plt.savefig('relatorios/delay.png')
print("Salvo: gráfico de atraso em 'delay.png'\n")

# Fim do script
print("Script concluído. Ajuste e expanda conforme precisar!")
