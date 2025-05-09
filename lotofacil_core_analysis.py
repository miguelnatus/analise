#!/usr/bin/env python3

import pandas as pd
from collections import Counter
import random

# --- Analysis Functions ---

def load_data(file_path='lotofacil.csv'):
    """Loads and preprocesses the Lotofácil data."""
    df = pd.read_csv(file_path)
    dezenas_cols = [f'Dezena{i}' for i in range(1, 16)]
    df.dropna(subset=dezenas_cols, inplace=True)
    for col in dezenas_cols:
        df[col] = df[col].astype(int)
    # Ensure Concurso is sorted for consistent 'last draw' retrieval
    if 'Concurso' in df.columns:
        df = df.sort_values(by='Concurso').reset_index(drop=True)
    return df, dezenas_cols

def analyze_even_odd_per_draw(df, dezenas_cols):
    """Analyzes the distribution of even and odd numbers for each draw."""
    results = []
    for index, row in df.iterrows():
        evens = 0
        odds = 0
        for col in dezenas_cols:
            if row[col] % 2 == 0:
                evens += 1
            else:
                odds += 1
        results.append({'Concurso': row['Concurso'], 'Pares': evens, 'Ímpares': odds})
    return pd.DataFrame(results)

def analyze_number_frequency(df, dezenas_cols):
    """Calculates the frequency of each number drawn."""
    all_numbers = []
    for col in dezenas_cols:
        all_numbers.extend(df[col].tolist())
    number_counts = Counter(all_numbers)
    return number_counts

def analyze_overdue_numbers(df, dezenas_cols, num_draws_to_consider=None):
    """Identifies how many draws ago each number was last seen."""
    if num_draws_to_consider is None or num_draws_to_consider <= 0:
        df_filtered = df
    else:
        df_filtered = df.tail(num_draws_to_consider)

    last_seen_concurso_index = {}
    # Initialize with a value indicating not seen or very overdue
    for number in range(1, 26):
        last_seen_concurso_index[number] = -len(df_filtered) 

    for i, row in df_filtered.iterrows():
        # i is the original DataFrame index if df_filtered is a slice
        # We need an index relative to df_filtered for consistent overdue calculation
        relative_index = df_filtered.index.get_loc(i)
        for col in dezenas_cols:
            num = row[col]
            last_seen_concurso_index[num] = relative_index
    
    max_relative_index_filtered = len(df_filtered) - 1
    overdue_counts = {}
    for number in range(1, 26):
        # overdue is (current_draw_index - last_seen_index)
        # if last_seen_concurso_index[number] is negative, it means it wasn't seen in the window
        overdue_counts[number] = max_relative_index_filtered - last_seen_concurso_index[number]
            
    return overdue_counts

def analyze_repeated_numbers(df, dezenas_cols):
    """Analyzes the number of repeated numbers from the previous draw."""
    repeated_counts_list = []
    if len(df) < 2:
        return pd.DataFrame(columns=['Concurso', 'Repetidos'])
        
    for i in range(1, len(df)):
        current_draw_numbers = set(df.iloc[i][dezenas_cols].values)
        previous_draw_numbers = set(df.iloc[i-1][dezenas_cols].values)
        repeated_count = len(current_draw_numbers.intersection(previous_draw_numbers))
        repeated_counts_list.append({'Concurso': df.iloc[i]['Concurso'], 'Repetidos': repeated_count})
    return pd.DataFrame(repeated_counts_list)

# --- Generator Functions ---

def generate_numbers_frequency_based(number_counts, num_to_pick=15):
    """Generates numbers based on frequency (weighted random sampling)."""
    population = list(number_counts.keys())
    weights = list(number_counts.values())
    # Ensure we don't pick more than available unique numbers
    if len(population) < num_to_pick:
        return sorted(random.sample(population, len(population)))
    # k=num_to_pick for random.choices, then ensure uniqueness
    chosen_numbers = set()
    attempts = 0
    max_attempts = num_to_pick * 10 # Safety break
    while len(chosen_numbers) < num_to_pick and attempts < max_attempts:
        # random.choices can return duplicates, so we sample one by one if we need unique set
        # A simpler way for weighted sampling without replacement is harder with just `random`
        # So, we sample with replacement and add to set until we have enough unique numbers.
        # This is not perfectly weighted without replacement but a common approximation.
        selected = random.choices(population, weights=weights, k=1)[0]
        chosen_numbers.add(selected)
        attempts += 1    
    if len(chosen_numbers) < num_to_pick: # Fallback if unique set not filled
        remaining_needed = num_to_pick - len(chosen_numbers)
        available_to_add = [p for p in population if p not in chosen_numbers]
        chosen_numbers.update(random.sample(available_to_add, min(remaining_needed, len(available_to_add))))
    return sorted(list(chosen_numbers))

def generate_numbers_even_odd_based(num_evens, num_odds, num_to_pick=15):
    """Generates numbers based on a specified count of even and odd numbers."""
    if num_evens + num_odds != num_to_pick:
        raise ValueError(f"A soma de números pares ({num_evens}) e ímpares ({num_odds}) deve ser {num_to_pick}.")
    
    all_evens = [n for n in range(1, 26) if n % 2 == 0]
    all_odds = [n for n in range(1, 26) if n % 2 != 0]

    if num_evens > len(all_evens) or num_odds > len(all_odds):
        raise ValueError("Solicitação de pares/ímpares excede a quantidade disponível.")

    chosen_evens = random.sample(all_evens, num_evens)
    chosen_odds = random.sample(all_odds, num_odds)
    
    return sorted(chosen_evens + chosen_odds)

def generate_numbers_overdue_based(overdue_counts, num_to_pick=15, top_n_overdue=None):
    """Generates numbers prioritizing more overdue ones (weighted or top N)."""
    # Sort by overdue (higher is more overdue)
    sorted_overdue = sorted(overdue_counts.items(), key=lambda item: item[1], reverse=True)
    
    if top_n_overdue and top_n_overdue >= num_to_pick:
        # Pick from the top N most overdue numbers
        population = [item[0] for item in sorted_overdue[:top_n_overdue]]
        if len(population) < num_to_pick:
             return sorted(random.sample(population, len(population))) # Should not happen if top_n_overdue >= num_to_pick
        return sorted(random.sample(population, num_to_pick))
    else:
        # Weighted random sampling: higher overdue count = higher weight
        population = [item[0] for item in sorted_overdue]
        weights = [item[1] for item in sorted_overdue] # Higher value means more overdue
        # Normalize weights to avoid issues with zero or negative if logic changes
        min_weight = min(weights)
        if min_weight <= 0: # Adjust if any weight is not positive
            weights = [w - min_weight + 1 for w in weights]

        chosen_numbers = set()
        attempts = 0
        max_attempts = num_to_pick * 10
        while len(chosen_numbers) < num_to_pick and attempts < max_attempts:
            selected = random.choices(population, weights=weights, k=1)[0]
            chosen_numbers.add(selected)
            attempts += 1
        if len(chosen_numbers) < num_to_pick:
            remaining_needed = num_to_pick - len(chosen_numbers)
            available_to_add = [p for p in population if p not in chosen_numbers]
            chosen_numbers.update(random.sample(available_to_add, min(remaining_needed, len(available_to_add))))
        return sorted(list(chosen_numbers))

def generate_numbers_repeated_based(df, dezenas_cols, num_to_repeat, num_to_pick=15):
    """Generates numbers by repeating a specific count from the last draw."""
    if len(df) == 0:
        raise ValueError("Não há dados de sorteios para obter o último sorteio.")
    
    last_draw_numbers = set(df.iloc[-1][dezenas_cols].values)
    all_possible_numbers = set(range(1, 26))
    numbers_not_in_last_draw = list(all_possible_numbers - last_draw_numbers)

    if num_to_repeat > len(last_draw_numbers) or num_to_repeat < 0:
        raise ValueError("Número de dezenas a repetir é inválido.")
    if (num_to_pick - num_to_repeat) > len(numbers_not_in_last_draw) or (num_to_pick - num_to_repeat) < 0:
        raise ValueError("Não há dezenas novas suficientes para completar o jogo.")

    repeated_chosen = random.sample(list(last_draw_numbers), num_to_repeat)
    new_chosen_count = num_to_pick - num_to_repeat
    new_chosen = random.sample(numbers_not_in_last_draw, new_chosen_count)
    
    return sorted(repeated_chosen + new_chosen)


# --- Helper for Prime Numbers (if needed for future extensions) ---
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == '__main__':
    df_main, dezenas_cols_main = load_data()

    print("--- Teste: Distribuição Pares/Ímpares por Sorteio (Primeiros 5) ---")
    even_odd_df = analyze_even_odd_per_draw(df_main, dezenas_cols_main)
    print(even_odd_df.head())

    print("\n--- Teste: Frequência dos Números ---")
    frequencies = analyze_number_frequency(df_main, dezenas_cols_main)
    print(sorted(frequencies.items()))

    print("\n--- Teste: Números Atrasados (Considerando últimos 100 sorteios) ---")
    overdue = analyze_overdue_numbers(df_main, dezenas_cols_main, num_draws_to_consider=100)
    print(f"Mais atrasados (top 5): {sorted(overdue.items(), key=lambda item: item[1], reverse=True)[:5]}")
    
    print("\n--- Teste: Números Atrasados (Considerando todos os sorteios) ---")
    overdue_all = analyze_overdue_numbers(df_main, dezenas_cols_main)
    print(f"Mais atrasados (todos, top 5): {sorted(overdue_all.items(), key=lambda item: item[1], reverse=True)[:5]}")

    print("\n--- Teste: Números Repetidos do Sorteio Anterior (Primeiros 5) ---")
    repeated_df = analyze_repeated_numbers(df_main, dezenas_cols_main)
    print(repeated_df.head())
    
    print("\n--- Testes Geradores ---")
    print(f"Gerador Frequência: {generate_numbers_frequency_based(frequencies)}")
    print(f"Gerador Pares(7)/Ímpares(8): {generate_numbers_even_odd_based(7, 8)}")
    print(f"Gerador Atrasados (Top 15 de 100 sorteios): {generate_numbers_overdue_based(overdue, top_n_overdue=15)}") # Pick 15 from top 15 overdue
    print(f"Gerador Atrasados (Ponderado de todos): {generate_numbers_overdue_based(overdue_all)}")
    if not df_main.empty:
        print(f"Gerador Repetidos (repetir 8 do último): {generate_numbers_repeated_based(df_main, dezenas_cols_main, 8)}")
    else:
        print("Não é possível testar o gerador de repetidos, DataFrame vazio.")

    print("\nTestes das funções de análise e geração concluídos.")

