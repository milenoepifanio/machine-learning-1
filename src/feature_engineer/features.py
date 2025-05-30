"""
Este script realiza a preparação e o enriquecimento de dados para análise de concessão de crédito. Ele carrega um 
dataset, padroniza nomes de colunas, cria novas variáveis e trata valores infinitos. Ao final, salva o dataset com 
as novas variáveis para uso posterior.

Passos detalhados:
1. Carregamento dos dados: Lê o dataset de dados de empréstimo de um arquivo CSV e captura erros de leitura.
2. Padronização de colunas: Renomeia colunas para formatos consistentes e acessíveis, tratando eventuais erros.
3. Criação de novas features: 
    - Converte valores negativos de experiência em zero.
    - Cria as seguintes variáveis:
        - `age_bracket`: Classifica a idade em faixas etárias.
        - `age_bracket_name`: Converte a faixa etária para nome de geração.
        - `income_per_family_member`: Calcula a renda por membro da família.
        - `cc_to_income_ratio`: Calcula a relação entre média de gastos no cartão de crédito e a renda.
        - `debt_to_income_ratio`: Calcula a relação dívida-renda somando a média do cartão e hipoteca.
        - `financial_maturity_index`: Índice baseado na relação entre renda e gastos no cartão.
4. Tratamento de valores infinitos: Substitui valores infinitos por NaN e remove linhas com valores ausentes.
5. Salvamento do dataset: Salva o dataset com as novas features em um CSV.

Erros tratados:
- Erro 001: Erro ao carregar os dados.
- Erro 002: Erro ao padronizar as colunas.
- Erro 003: Erro ao criar novas features.
- Erro 004: Erro ao tratar valores infinitos.

Saída:
O dataset com as novas variáveis é salvo no diretório `data/feature_store/data_with_new_features.csv`.

Bibliotecas necessárias:
- pandas
- numpy
"""


import pandas as pd
import numpy as np


# step-1: load data

try:
    df = pd.read_csv('data/external/bankloan.csv')
    print('Step 1/5 - Dados carregados com sucesso.')
except Exception as load_error:
    print('{}: Erro ao caregar os dados. Erro tipo 001.'.format(load_error))

# step-2: standardizing columns

try:
    rename_columns = {
                    'Age': 'age',
                    'Experience': 'experience',
                    'Income': 'income',
                    'ZIP.Code': 'zip_code',
                    'Family': 'family',
                    'CCAvg': 'cc_avg',
                    'Education': 'education',
                    'Mortgage': 'mortgage',
                    'Personal.Loan': 'personal_loan',
                    'Securities.Account': 'securities_account',
                    'CD.Account': 'cd_account',
                    'Online': 'online',
                    'CreditCard': 'credit_card'
                    
                    }

    df = df.rename(columns=rename_columns)
    print('Step 2/5 - Colunas padronizadas')
except Exception as standardize_columns_error:
    print('{}: Erro ao padronizar colunas. Erro tipo 002.'.format(standardize_columns_error))

# step-3: creating new features

df.loc[df['experience'] < 0, 'experience'] = 0

def age_bracket(age: int) -> int:
    if age >= 78:
        return 5
    elif age >= 59:
        return 4
    elif age >= 43:
        return 3
    elif age >= 27:
        return 2
    else:
        return 1


def age_bracket_str(age_bracket: int) -> str:
    if age_bracket == 1:
        return 'Generation Z'
    elif age_bracket == 2:
        return 'Millennials'
    elif age_bracket == 3:
        return 'Generation X'
    elif age_bracket == 4:
        return 'Baby boomers'
    else:
        return 'Silent generation'


# Avaliar métrica usada para crédito, placeholde
def age_bracket_credit_expected(age_bracket: int) -> int:
    if age_bracket == 1:
        return 665
    elif age_bracket == 2:
        return 687
    elif age_bracket == 3:
        return 710
    elif age_bracket == 4:
        return 746
    else:
        return 750


def experience_bracket(experience: int) -> int:
    if experience >= 40:
        return 4
    elif experience >= 30:
        return 3
    elif experience >= 10:
        return 2    
    else:
        return 1


def renaming(degree: int) -> str:
    if degree == 1:
        return 'high school'
    elif degree == 2:
        return 'college'
    else:
        return 'postgraduate'
    

try:
    df['age_bracket'] = df['age'].apply(age_bracket)
    df['age_bracket_name'] = df['age_bracket'].apply(age_bracket_str)
    df['income_per_family_member'] = df['income'] / (df['family'] + 1)
    df['cc_to_income_ratio'] = df['cc_avg'] / df['income']
    df['debt_to_income_ratio'] = (df['cc_avg'] + df['mortgage']) / df['income']
    df['financial_maturity_index'] = (df['income'] / df['cc_avg'])
    df['experience_bracket'] = df['experience'].apply(experience_bracket)
    df['education_degree'] = df['education'].apply(renaming)
    print('Step 3/5 - Novas features adicionadas.')
except Exception as feature_eng_error:
    print('{}: Ocorreu um erro ao criar novas features. Erro tipo 003.'.format(feature_eng_error))

    

# step-4: to treat infinity values
try:
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    print('Step 4/5 - Não há valores infinitos.')
except Exception as inf_error:
    print('{}: Ocorreu um erro ao tratar os valores tendendo ao infinito. Erro tipo 004.'.format(inf_error))

# step-5: lean on dataset
df_lean = df[['age', 'experience', 'age_bracket', 'experience_bracket', 'income', 'family',
       'education_degree', 'mortgage', 'personal_loan', 'securities_account',
       'cd_account', 'online', 'credit_card', 'cc_avg']].copy()

# step-6: saving data with new features
df.to_csv('data/feature_store/data_with_new_features.csv', index=False)
print('Step 5/5 - Dados salvos.')
