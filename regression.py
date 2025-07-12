from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

def prever_tendencias(df_historico: pd.DataFrame, anos_para_prever: int) -> pd.DataFrame:
    """
    Prevê tendências futuras com base em dados históricos usando regressão linear.
    Args:
        df_historico (pd.DataFrame): DataFrame contendo os dados históricos com colunas 'Ano' e 'Total geral'.
        anos_para_prever (int): Número de anos para prever no futuro.
    Returns:
        pd.DataFrame: DataFrame contendo as previsões futuras com colunas 'Ano', 'Total geral' e 'Tipo'.
    """
    # Garante que estamos trabalhando com uma cópia e com os dados ordenados por ano
    df_historico_limpo = df_historico[['Ano', 'Total geral']].copy().sort_values(by='Ano').reset_index(drop=True)
    
    # 1. Engenharia de Features
    df_eng = df_historico_limpo.copy()
    df_eng['tendencia'] = range(len(df_eng))
    df_eng['lag_1'] = df_eng['Total geral'].shift(1)
    df_eng['media_movel_2a'] = df_eng['Total geral'].shift(1).rolling(window=2).mean()
    df_eng = df_eng.dropna().reset_index(drop=True)

    if len(df_eng) < 2:
        return pd.DataFrame() # Retorna DF vazio se não houver dados suficientes

    X_hist = df_eng[['tendencia', 'lag_1', 'media_movel_2a']]
    y_hist = df_eng['Total geral']
    
    modelo = LinearRegression()
    modelo.fit(X_hist, y_hist)

    previsoes_futuras = []
    ultimo_ano = df_eng['Ano'].iloc[-1]
    ultima_tendencia = df_eng['tendencia'].iloc[-1]
    ultimo_valor = y_hist.iloc[-1]
    penultimo_valor = y_hist.iloc[-2]

    for i in range(anos_para_prever):
        tendencia_futura = ultima_tendencia + 1 + i
        lag_1_futuro = ultimo_valor
        media_movel_futura = (ultimo_valor + penultimo_valor) / 2.0
        features_futuras = np.array([[tendencia_futura, lag_1_futuro, media_movel_futura]])
        proximo_valor_previsto = modelo.predict(features_futuras)[0]
        previsoes_futuras.append(proximo_valor_previsto)
        penultimo_valor = ultimo_valor
        ultimo_valor = proximo_valor_previsto

    anos_futuros = [ultimo_ano + i + 1 for i in range(anos_para_prever)]
    df_futuro = pd.DataFrame({'Ano': anos_futuros, 'Total geral': previsoes_futuras, 'Tipo': 'Previsão'})
    
    df_plot_hist = pd.DataFrame({'Ano': df_historico_limpo['Ano'], 'Total geral': df_historico_limpo['Total geral'], 'Tipo': 'Histórico'})

    df_final = pd.concat([df_plot_hist, df_futuro]).reset_index(drop=True)
    return df_final