import pandas as pd
import numpy as np

def regressao_polinomial(df_historico: pd.DataFrame, anos_para_prever: int, grau: int, mostrar_curva: bool) -> pd.DataFrame:
    """
    Prevê tendências futuras com base em dados históricos usando regressão polinomial
    calculada manualmente através da Equação Normal.

    Args:
        df_historico (pd.DataFrame): DataFrame com colunas 'Ano' e 'Total geral'.
        anos_para_prever (int): Número de anos para prever no futuro.
        grau (int): O grau do polinômio a ser ajustado (ex: 1 para linear, 2 para quadrática).
        mostrar_curva (bool): Se True, mostra a curva ajustada nos dados históricos.

    Returns:
        pd.DataFrame: DataFrame com os dados históricos, a curva ajustada e as previsões.
    """
    df_limpo = df_historico[['Ano', 'Total geral']].copy().sort_values(by='Ano').reset_index(drop=True)

    x_hist = df_limpo['Ano'].values
    y_hist = df_limpo['Total geral'].values

    x_hist = np.array(x_hist, dtype=np.float64)
    y_hist = np.array(y_hist, dtype=np.float64)

    # Matriz de Design (X)
    # Normalizar o ano para evitar problemas numéricos
    ano_inicial = df_limpo['Ano'].min()
    x_hist_normalizado = df_limpo['Ano'].values - ano_inicial 
    y_hist = df_limpo['Total geral'].values
    # Cada coluna é x elevado a uma potência, de 0 até o grau do polinômio.
    X_hist_matrix = np.column_stack([x_hist_normalizado**p for p in range(grau + 1)])

    # Equação Normal para encontrar os coeficientes (beta)
    # beta = inv(X.T * X) * X.T * y
    try:
        xt = X_hist_matrix.T
        xtx = xt @ X_hist_matrix # Multiplicação de matrizes
        xtx_inv = np.linalg.inv(xtx) # Inversa da matriz
        xty = xt @ y_hist
        beta = xtx_inv @ xty
    except np.linalg.LinAlgError:
        # Caso a matriz seja singular (não inversível), retorna um DF vazio
        print("Erro: A matriz X.T * X é singular e não pode ser invertida. Tente um grau menor ou verifique os dados.")
        return pd.DataFrame()

    # Fazer previsões
    # Gerar os anos futuros
    ultimo_ano = x_hist[-1]
    anos_futuros = np.array([ultimo_ano + i + 1 for i in range(anos_para_prever)])

    # Normalizar os anos futuros da mesma forma
    ultimo_ano_original = df_limpo['Ano'].values[-1]
    anos_futuros_original = np.array([ultimo_ano_original + i + 1 for i in range(anos_para_prever)])
    anos_futuros_normalizado = anos_futuros_original - ano_inicial

    # Construir a Matriz de Design para os anos futuros
    X_futuro_matrix = np.column_stack([anos_futuros_normalizado**p for p in range(grau + 1)])

    # Prever os valores multiplicando a matriz futura pelos coeficientes
    previsoes = X_futuro_matrix @ beta

    # Montar o DataFrame final para visualização
    # Curva ajustada sobre os dados históricos
    y_ajustado = X_hist_matrix @ beta

    df_plot_hist = pd.DataFrame({'Ano': x_hist, 'Total geral': y_hist, 'Tipo': 'Histórico'})
    df_plot_ajuste = pd.DataFrame({'Ano': x_hist, 'Total geral': y_ajustado, 'Tipo': 'Ajuste Polinomial'})
    df_futuro = pd.DataFrame({'Ano': anos_futuros, 'Total geral': previsoes, 'Tipo': 'Previsão Polinomial'})

    if mostrar_curva: # Se o usuário quiser ver a curva ajustada
        # Concatenar os dados históricos, a curva ajustada e as previsões
        df_final = pd.concat([df_plot_hist, df_plot_ajuste, df_futuro]).reset_index(drop=True)
    else:
        # Se não, concatena apenas os dados históricos e as previsões
        df_final = pd.concat([df_plot_hist, df_futuro]).reset_index(drop=True)
    
    # Imprimir os coeficientes encontrados para análise
    print(f"Coeficientes do Polinômio (beta) de grau {grau}:")
    for i, b in enumerate(beta):
        print(f"β{i} (x^{i}): {b:.4f}")

    return df_final