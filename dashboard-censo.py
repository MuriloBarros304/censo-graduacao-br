import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# A configuração da página deve ser o primeiro comando do Streamlit
st.set_page_config(
    page_title="Dashboard Censo Educação Superior",
    page_icon="🎓",
    layout="wide" # 'centered' ou 'wide'
)

# --- Carregamento e Cache dos Dados ---
# @st.cache_data garante que o pré-processamento pesado só rode uma vez.
@st.cache_data
def carregar_dados():
    # Caminho para o arquivo Excel
    path = 'https://raw.githubusercontent.com/MuriloBarros304/censo-graduacao-br/main/data/raw/tabelas_de_divulgacao_censo_da_educacao_superior_2023.xls'
    
    # Carrega os dados de ingressantes
    df_ingressantes = pd.read_excel(path, sheet_name="Tab3.04", header=None)
    df_ingressantes = df_ingressantes.iloc[7:]
    df_ingressantes = df_ingressantes.drop(71)
    df_ingressantes.columns = [
        'Ano', 'Grau', 'Total geral', 'Total geral publica', 'Total geral federal',
        'Total geral estadual', 'Total geral municipal', 'Total geral privada',
        'Total geral com fins', 'Total geral sem fins', 'Total presencial', 'Total presencial publica',
        'Total presencial federal', 'Total presencial estadual', 'Total presencial municipal',
        'Total presencial privada', 'Total presencial com fins', 'Total presencial sem fins',
        'Total geral remota', 'Total remota publica', 'Total remota federal',
        'Total remota estadual', 'Total remota municipal', 'Total remota privada',
        'Total remota com fins', 'Total remota sem fins'
    ]
    df_ingressantes = df_ingressantes.dropna(how='all').reset_index(drop=True)
    df_ingressantes['Ano'] = df_ingressantes['Ano'].ffill()
    df_ingressantes = df_ingressantes.fillna(0).replace({'.': 0, '-': 0})
    
    # Carrega os dados de concluintes
    df_concluintes = pd.read_excel(path, sheet_name="Tab3.05", header=None)
    df_concluintes = df_concluintes.iloc[8:]
    df_concluintes = df_concluintes.drop(61)
    df_concluintes.columns = [
        'Ano', 'Grau', 'Total geral', 'Total geral publica',
        'Total geral federal', 'Total geral estadual', 'Total geral municipal',
        'Total geral privada', 'Total geral com fins', 'Total geral sem fins',
        'Total presencial', 'Total presencial publica', 'Total presencial federal',
        'Total presencial estadual', 'Total presencial municipal',
        'Total presencial privada', 'Total presencial com fins',
        'Total presencial sem fins', 'Total geral remota',
        'Total remota publica', 'Total remota federal',
        'Total remota estadual', 'Total remota municipal','Total remota privada',
        'Total remota com fins', 'Total remota sem fins'
    ]
    df_concluintes = df_concluintes.dropna(how='all').reset_index(drop=True)
    df_concluintes['Ano'] = df_concluintes['Ano'].ffill()
    df_concluintes = df_concluintes.fillna(0).replace({'.': 0, '-': 0})
    
    # Conversão de tipos para ambos os dataframes
    cols_to_convert = list(df_ingressantes.columns)
    cols_to_convert.remove('Grau')
    for col in cols_to_convert:
        df_ingressantes[col] = pd.to_numeric(df_ingressantes[col], errors='coerce').fillna(0).astype(int)
        df_concluintes[col] = pd.to_numeric(df_concluintes[col], errors='coerce').fillna(0).astype(int)
        
    return df_ingressantes, df_concluintes

# Carrega os dados usando a função cacheada
df_ingressantes, df_concluintes = carregar_dados()

# --- Barra Lateral (Sidebar) com Filtros ---
st.sidebar.image("images/logo.png", width=250)
st.sidebar.title("Filtros Interativos")
st.sidebar.markdown("Use os filtros abaixo para explorar os dados:")

# Filtro para selecionar Ingressantes ou Concluintes
tipo_analise = st.sidebar.radio(
    "Selecione a base de dados:",
    ("Ingressantes", "Concluintes"),
    key="tipo_analise"
)

# Define o dataframe ativo com base na seleção
df_ativo = df_ingressantes if tipo_analise == "Ingressantes" else df_concluintes

# Filtro de intervalo de anos
ano_min = df_ativo["Ano"].min()
ano_max = df_ativo["Ano"].max()
ano_selecionado = st.sidebar.slider(
    "Selecione o Ano:",
    min_value=ano_min,
    max_value=ano_max,
    value=ano_max # Padrão para o ano mais recente
)

# Filtro de grau acadêmico (excluindo 'Total' para evitar duplicidade nas somas)
graus_disponiveis = df_ativo[df_ativo['Grau'] != 'Total']['Grau'].unique()
grau_selecionado = st.sidebar.multiselect(
    "Selecione o Grau Acadêmico:",
    options=graus_disponiveis,
    default=graus_disponiveis # Padrão para todos os graus
)

# Filtra o dataframe com base nas seleções
df_filtrado = df_ativo[
    (df_ativo["Ano"] == ano_selecionado) &
    (df_ativo["Grau"].isin(grau_selecionado))
]

# --- Corpo Principal do Dashboard ---
st.title(f"Dashboard do Censo da Educação Superior")
st.markdown(f"### Análise de **{tipo_analise}** para o ano de **{ano_selecionado}**")

# --- KPIs (Métricas Principais) ---
st.markdown("---")
st.subheader("Visão Geral do Ano Selecionado")

# Soma os valores do dataframe filtrado
total_geral = df_filtrado['Total geral'].sum()
total_publica = df_filtrado['Total geral publica'].sum()
total_privada = df_filtrado['Total geral privada'].sum()
total_presencial = df_filtrado['Total presencial'].sum()
total_remota = df_filtrado['Total geral remota'].sum()

# Layout em colunas para os KPIs
col1, col2, col3 = st.columns(3)
col1.metric(f"Total de {tipo_analise}", f"{total_geral:,}".replace(",", "."))
col2.metric("Total em Instituições Públicas", f"{total_publica:,}".replace(",", "."))
col3.metric("Total em Instituições Privadas", f"{total_privada:,}".replace(",", "."))

col4, col5 = st.columns(2)
col4.metric("Total na Modalidade Presencial", f"{total_presencial:,}".replace(",", "."))
col5.metric("Total na Modalidade Remota (EAD)", f"{total_remota:,}".replace(",", "."))


# --- Gráficos da Visão Geral ---
st.markdown("---")
st.subheader("Evolução Histórica e Distribuições")

# Gráfico de Evolução Histórica (Ingressantes vs. Concluintes)
df_ingressantes_totais = df_ingressantes[df_ingressantes['Grau'] == 'Total'].set_index('Ano')['Total geral'].rename('Ingressantes')
df_concluintes_totais = df_concluintes[df_concluintes['Grau'] == 'Total'].set_index('Ano')['Total geral'].rename('Concluintes')
df_evolucao = pd.concat([df_ingressantes_totais, df_concluintes_totais], axis=1)

fig_evolucao = px.line(
    df_evolucao,
    x=df_evolucao.index,
    y=['Ingressantes', 'Concluintes'],
    title="Evolução Anual: Ingressantes vs. Concluintes (Total)",
    labels={'value': 'Número de Alunos', 'Ano': 'Ano'},
    markers=True
)
st.plotly_chart(fig_evolucao, use_container_width=True)


# Gráficos de Pizza para o ano selecionado
c1, c2 = st.columns(2)
with c1:
    fig_dist_adm = px.pie(
        names=['Pública', 'Privada'],
        values=[total_publica, total_privada],
        title=f"Distribuição por Categoria Administrativa ({ano_selecionado})",
        hole=0.3
    )
    st.plotly_chart(fig_dist_adm, use_container_width=True)

with c2:
    fig_dist_mod = px.pie(
        names=['Presencial', 'Remota (EAD)'],
        values=[total_presencial, total_remota],
        title=f"Distribuição por Modalidade de Ensino ({ano_selecionado})",
        hole=0.3
    )
    st.plotly_chart(fig_dist_mod, use_container_width=True)

# --- Análises Detalhadas em Abas ---
st.markdown("---")
st.subheader("Análises Detalhadas")

tab1, tab2, tab3 = st.tabs(["Por Grau Acadêmico", "Por Categoria Administrativa", "Dados Brutos"])

with tab1:
    st.markdown(f"#### Análise por Grau Acadêmico para o ano de **{ano_selecionado}**")
    
    # Gráfico de Barras por Grau
    df_grau_sum = df_filtrado.groupby('Grau')['Total geral'].sum().sort_values(ascending=False)
    fig_grau = px.bar(
        df_grau_sum,
        x=df_grau_sum.index,
        y='Total geral',
        title=f"Número de {tipo_analise} por Grau Acadêmico",
        labels={'Total geral': f'Total de {tipo_analise}', 'Grau': 'Grau Acadêmico'},
        text_auto=True
    )
    st.plotly_chart(fig_grau, use_container_width=True)

with tab2:
    st.markdown(f"#### Detalhamento por Categoria Administrativa ({ano_selecionado})")
    
    # Preparando dados para o gráfico de barras empilhadas
    data_detalhe = {
        'Categoria': ['Pública Federal', 'Pública Estadual', 'Pública Municipal', 'Privada com Fins Lucrativos', 'Privada sem Fins Lucrativos'],
        'Total': [
            df_filtrado['Total geral federal'].sum(),
            df_filtrado['Total geral estadual'].sum(),
            df_filtrado['Total geral municipal'].sum(),
            df_filtrado['Total geral com fins'].sum(),
            df_filtrado['Total geral sem fins'].sum()
        ],
        'Tipo': ['Pública', 'Pública', 'Pública', 'Privada', 'Privada']
    }
    df_detalhe = pd.DataFrame(data_detalhe)
    
    fig_detalhe_adm = px.bar(
        df_detalhe,
        x='Categoria',
        y='Total',
        color='Tipo',
        title=f'Detalhamento de {tipo_analise} por Tipo de Instituição',
        labels={'Total': f'Número de {tipo_analise}', 'Categoria': 'Categoria Administrativa Detalhada'},
        text_auto=True
    )
    st.plotly_chart(fig_detalhe_adm, use_container_width=True)


with tab3:
    st.markdown(f"#### Dados Filtrados ({tipo_analise} - {ano_selecionado})")
    st.dataframe(df_filtrado)
    # Adiciona um botão para download dos dados filtrados
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(df_filtrado)
    st.download_button(
        label="Baixar dados como CSV",
        data=csv,
        file_name=f'{tipo_analise.lower()}_{ano_selecionado}.csv',
        mime='text/csv',
    )

# Comparação entre Ingressantes e Concluintes
st.markdown("---")
st.subheader(f"Comparativo Direto: Ingressantes vs. Concluintes ({ano_selecionado})")
if grau_selecionado:
    st.markdown(f"Analisando os graus: **{', '.join(grau_selecionado)}**")

    # Filtrar ambos os dataframes com base nas seleções da sidebar
    df_ing_filtrado = df_ingressantes[
        (df_ingressantes["Ano"] == ano_selecionado) &
        (df_ingressantes["Grau"].isin(grau_selecionado))
    ]
    df_con_filtrado = df_concluintes[
        (df_concluintes["Ano"] == ano_selecionado) &
        (df_concluintes["Grau"].isin(grau_selecionado))
    ]

    # Calcular totais para a métrica
    total_ing = df_ing_filtrado['Total geral'].sum()
    total_con = df_con_filtrado['Total geral'].sum()
    proporcao = (total_con / total_ing * 100) if total_ing > 0 else 0

    st.metric(
        label=f"Proporção Concluintes / Ingressantes em {ano_selecionado}",
        value=f"{proporcao:.2f} %",
        help="Este valor representa quantos alunos se formaram para cada 100 que ingressaram, considerando os filtros selecionados. Não é uma taxa de evasão real, mas um indicador da proporção entre os dois grupos no mesmo ano."
    )

    # Preparar dados para o gráfico de barras comparativo
    dados_comparativos = {
        'Métrica': ['Pública', 'Privada', 'Presencial', 'Remota (EAD)'],
        'Ingressantes': [
            df_ing_filtrado['Total geral publica'].sum(), df_ing_filtrado['Total geral privada'].sum(),
            df_ing_filtrado['Total presencial'].sum(), df_ing_filtrado['Total geral remota'].sum()
        ],
        'Concluintes': [
            df_con_filtrado['Total geral publica'].sum(), df_con_filtrado['Total geral privada'].sum(),
            df_con_filtrado['Total presencial'].sum(), df_con_filtrado['Total geral remota'].sum()
        ]
    }
    df_comparativo_plot = pd.DataFrame(dados_comparativos).melt(
        id_vars='Métrica', var_name='Tipo', value_name='Número de Alunos'
    )
    
    # Gráfico de barras agrupado
    fig_comparativo = px.bar(
        df_comparativo_plot, x='Métrica', y='Número de Alunos', color='Tipo',
        barmode='group', title=f"Comparativo Detalhado para {ano_selecionado}",
        labels={'Número de Alunos': 'Total de Alunos', 'Métrica': 'Categoria'},
        text_auto=True, color_discrete_map={'Ingressantes':'#636EFA', 'Concluintes':'#FFA15A'}
    )
    st.plotly_chart(fig_comparativo, use_container_width=True)

else:
    st.warning("Selecione pelo menos um Grau Acadêmico na barra lateral para ver a comparação.")