#!/usr/bin/env python3

import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
# Load the CSV file
file_path = 'lotofacil.csv' # Assumes the CSV is in the same directory as the script
df = pd.read_csv(file_path)

# Data Cleaning and Preparation
# Drop rows with any missing values in the 'Dezena' columns
dezenas_cols = [f'Dezena{i}' for i in range(1, 16)]
df.dropna(subset=dezenas_cols, inplace=True)

# Convert 'Dezena' columns to integer type
for col in dezenas_cols:
    df[col] = df[col].astype(int)

# --- Analysis Functions ---

def analyze_number_frequency(df, dezenas_cols):
    """Calculates and prints the frequency of each number drawn."""
    all_numbers = []
    for col in dezenas_cols:
        all_numbers.extend(df[col].tolist())
    number_counts = Counter(all_numbers)
    print("\n--- Frequência dos Números (Todos os Sorteios) ---")
    for num, count in sorted(number_counts.items()):
        print(f"Número {num}: {count} vezes")
    return number_counts

def analyze_even_odd(df, dezenas_cols):
    """Analyzes and prints the distribution of even and odd numbers."""
    even_odd_counts = {'pares': 0, 'ímpares': 0}
    for col in dezenas_cols:
        for num in df[col]:
            if num % 2 == 0:
                even_odd_counts['pares'] += 1
            else:
                even_odd_counts['ímpares'] += 1
    print("\n--- Análise de Pares/Ímpares ---")
    print(f"Números Pares: {even_odd_counts['pares']}")
    print(f"Números Ímpares: {even_odd_counts['ímpares']}")
    return even_odd_counts

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def analyze_prime_numbers(df, dezenas_cols):
    """Analyzes and prints the distribution of prime numbers."""
    prime_counts = {'primos': 0, 'não primos': 0}
    for col in dezenas_cols:
        for num in df[col]:
            if is_prime(num):
                prime_counts['primos'] += 1
            else:
                prime_counts['não primos'] += 1
    print("\n--- Análise de Números Primos ---")
    print(f"Números Primos: {prime_counts['primos']}")
    print(f"Números Não Primos: {prime_counts['não primos']}")
    return prime_counts

def analyze_sequences(df, dezenas_cols, length=3):
    """Identifies sequences of a given length within each draw."""
    sequence_counts = Counter()
    for index, row in df.iterrows():
        numbers_in_draw = sorted([row[col] for col in dezenas_cols])
        for i in range(len(numbers_in_draw) - length + 1):
            sequence = tuple(numbers_in_draw[i:i+length])
            # Check if the sequence is consecutive
            is_consecutive = all(sequence[j] + 1 == sequence[j+1] for j in range(len(sequence)-1))
            if is_consecutive:
                sequence_counts[sequence] += 1
    print(f"\n--- Sequências de {length} Números Mais Comuns ---")
    for seq, count in sequence_counts.most_common(10):
        print(f"Sequência {seq}: {count} vezes")
    return sequence_counts

# --- Visualization Functions ---
def plot_number_frequency(number_counts):
    """Plots the frequency of each number."""
    sorted_counts = sorted(number_counts.items())
    numbers = [item[0] for item in sorted_counts]
    counts = [item[1] for item in sorted_counts]
    plt.figure(figsize=(12, 6))
    sns.barplot(x=numbers, y=counts)
    plt.title('Frequência dos Números na Lotofácil')
    plt.xlabel('Número')
    plt.ylabel('Frequência')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('lotofacil_frequencia.png')
    print("\nGráfico de frequência salvo como lotofacil_frequencia.png")

def plot_even_odd_distribution(even_odd_counts):
    """Plots the distribution of even and odd numbers as a pie chart."""
    plt.figure(figsize=(6, 6))
    plt.pie(even_odd_counts.values(), labels=even_odd_counts.keys(), autopct='%1.1f%%', startangle=90)
    plt.title('Distribuição de Números Pares e Ímpares')
    plt.savefig('lotofacil_pares_impares.png')
    print("Gráfico de pizza de pares/ímpares salvo como lotofacil_pares_impares.png")

def plot_prime_distribution(prime_counts):
    """Plots the distribution of prime numbers as a pie chart."""
    plt.figure(figsize=(6, 6))
    plt.pie(prime_counts.values(), labels=prime_counts.keys(), autopct='%1.1f%%', startangle=90)
    plt.title('Distribuição de Números Primos')
    plt.savefig('lotofacil_primos.png')
    print("Gráfico de pizza de números primos salvo como lotofacil_primos.png")

# --- Main Execution ---
if __name__ == "__main__":
    print("Análise Estatística dos Resultados da Lotofácil")
    print("=================================================")

    # Perform analyses
    number_frequencies = analyze_number_frequency(df, dezenas_cols)
    even_odd_distribution = analyze_even_odd(df, dezenas_cols)
    prime_distribution = analyze_prime_numbers(df, dezenas_cols)
    sequences_of_3 = analyze_sequences(df, dezenas_cols, length=3)
    sequences_of_5 = analyze_sequences(df, dezenas_cols, length=5)

    # Generate and save plots
    plot_number_frequency(number_frequencies)
    plot_even_odd_distribution(even_odd_distribution)
    plot_prime_distribution(prime_distribution)

    print("\nAnálise concluída. Os gráficos foram salvos no diretório atual.")

