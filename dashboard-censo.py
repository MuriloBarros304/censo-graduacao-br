import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

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
    path = 'https://raw.githubusercontent.com/MuriloBarros304/censo-graduacao-br/main/data/raw/tabelas_de_divulgacao_censo_da_educacao_superior_2023.xls'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        response = requests.get(path, headers=headers, timeout=30)
        response.raise_for_status()
        file_content = io.BytesIO(response.content)
        
        df_ingressantes = pd.read_excel(file_content, sheet_name="Tab3.04", header=None)
        file_content.seek(0)
        df_concluintes = pd.read_excel(file_content, sheet_name="Tab3.05", header=None)
        
        df_ingressantes = df_ingressantes.iloc[7:].drop(71)
        df_ingressantes.columns = [
            'Ano', 'Grau', 'Total geral', 'Total geral publica', 'Total geral federal', 'Total geral estadual', 'Total geral municipal', 'Total geral privada',
            'Total geral com fins', 'Total geral sem fins', 'Total presencial', 'Total presencial publica', 'Total presencial federal', 'Total presencial estadual',
            'Total presencial municipal', 'Total presencial privada', 'Total presencial com fins', 'Total presencial sem fins', 'Total geral remota',
            'Total remota publica', 'Total remota  federal', 'Total remota estadual', 'Total remota municipal', 'Total remota privada', 'Total remota com fins', 'Total remota sem fins'
        ]
        df_ingressantes = df_ingressantes.dropna(how='all').reset_index(drop=True)
        df_ingressantes['Ano'] = df_ingressantes['Ano'].ffill()
        df_ingressantes = df_ingressantes.fillna(0).replace({'.': 0, '-': 0})

        df_concluintes = df_concluintes.iloc[8:].drop(61)
        df_concluintes.columns = [
            'Ano', 'Grau', 'Total geral', 'Total geral publica', 'Total geral federal',  'Total geral estadual', 'Total geral municipal', 'Total geral privada',
            'Total geral com fins', 'Total geral sem fins', 'Total presencial', 'Total presencial publica', 'Total presencial federal', 'Total presencial estadual',
            'Total presencial municipal', 'Total presencial privada', 'Total presencial com fins', 'Total presencial sem fins', 'Total geral remota', 'Total remota publica',
            'Total remota  federal', 'Total remota estadual', 'Total remota municipal','Total remota privada', 'Total remota com fins', 'Total remota sem fins'
        ]
        df_concluintes = df_concluintes.dropna(how='all').reset_index(drop=True)
        df_concluintes['Ano'] = df_concluintes['Ano'].ffill()
        df_concluintes = df_concluintes.fillna(0).replace({'.': 0, '-': 0})
        
        cols_to_convert = list(df_ingressantes.columns)
        cols_to_convert.remove('Grau')
        for col in cols_to_convert:
            df_ingressantes[col] = pd.to_numeric(df_ingressantes[col], errors='coerce').fillna(0).astype(int)
            df_concluintes[col] = pd.to_numeric(df_concluintes[col], errors='coerce').fillna(0).astype(int)
            
        return df_ingressantes, df_concluintes
    
    except requests.exceptions.RequestException as e:
        st.error(f"Falha de rede ao carregar os dados. Verifique sua conexão. Erro: {e}")
        return None, None

# Carrega os dados usando a função cacheada
df_ingressantes, df_concluintes = carregar_dados()

if df_ingressantes is None or df_concluintes is None:
    st.stop()  # Interrompe a execução se os dados não puderem ser carregados

# --- Barra Lateral (Sidebar) com Filtros ---
st.sidebar.image("images/logo.png", width=250)
st.sidebar.title("Filtros")
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
graus_disponiveis = df_ativo[(df_ativo['Grau'] != 'Total') & (df_ativo['Grau'] != 'Não aplicável')]['Grau'].unique()
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
total_geral = df_filtrado['Total geral'].sum()
total_publica = df_filtrado['Total geral publica'].sum()
total_privada = df_filtrado['Total geral privada'].sum()
total_presencial = df_filtrado['Total presencial'].sum()
total_remota = df_filtrado['Total geral remota'].sum()
total_remota_publica = df_filtrado['Total remota publica'].sum()
total_remota_privada = df_filtrado['Total remota privada'].sum()
total_presencial_publica = df_filtrado['Total presencial publica'].sum()
total_presencial_privada = df_filtrado['Total presencial privada'].sum()

# Layout em colunas para os KPIs
col1, col2, col3 = st.columns(3)
col1.metric(f"Total de {tipo_analise}", f"{total_geral:,}".replace(",", "."))
col2.metric("Total em Instituições Públicas", f"{total_publica:,}".replace(",", "."))
col3.metric("Total em Instituições Privadas", f"{total_privada:,}".replace(",", "."))

# --- Gráficos da Visão Geral ---
 # --- SEÇÃO DE ANÁLISES COM ABAS ---
st.markdown("---")
st.subheader("Análises Gráficas")

mapa_de_cores = {'Pública': '#004A99', 'Privada': '#FFAA00', 'Presencial': '#28a745', 'Remota (EAD)': "#ea580f"}

tab1, tab2, tab3 = st.tabs(["Distribuições Gerais", "Análise Detalhada", "Dados Brutos"])

with tab1: # Supondo que você renomeou a tab1 para tab_geral
    st.markdown(f"##### Distribuição Geral de {tipo_analise} ({ano_selecionado})")
    c1, c2 = st.columns(2)
    with c1:
        df_adm = pd.DataFrame({
            'Categoria': ['Pública', 'Privada'],
            'Total': [total_publica, total_privada]
        })
        fig_dist_adm = px.bar(
            df_adm,
            x='Categoria',  # Eixo X com as categorias
            y='Total',      # Eixo Y com os valores numéricos
            title="Geral Por Categoria Administrativa",
            color='Categoria',  # Colorir as barras pela categoria (funciona igual)
            color_discrete_map=mapa_de_cores,
            text_auto=True      # Adiciona o valor em cima de cada barra, ótimo para visualização!
        )
        st.plotly_chart(fig_dist_adm, use_container_width=True)
    
    with c2:
        # O DataFrame continua o mesmo
        df_mod = pd.DataFrame({
            'Modalidade': ['Presencial', 'Remota (EAD)'],
            'Total': [total_presencial, total_remota]
        })
        fig_dist_mod = px.bar(
            df_mod,
            x='Modalidade', # Eixo X
            y='Total',      # Eixo Y
            title="Geral Por Modalidade de Ensino",
            color='Modalidade', # Colorir as barras pela modalidade
            color_discrete_map=mapa_de_cores,
            text_auto=True      # Adiciona os valores nas barras
        )
        st.plotly_chart(fig_dist_mod, use_container_width=True)

with tab2:
    st.markdown(f"##### Distribuição de {tipo_analise} por Categoria Administrativa e Modalidade ({ano_selecionado})")
    c1, c2 = st.columns(2)
    with c1:
        df_mod_publica = pd.DataFrame({
            'Modalidade': ['Presencial', 'Remota (EAD)'],
            'Total': [total_presencial_publica, total_remota_publica]
        })
        fig_dist_mod_publica = px.pie(
            df_mod_publica,
            names='Modalidade',
            values='Total',
            title="Instituições Públicas",
            hole=0.3,
            color='Modalidade',
            color_discrete_map=mapa_de_cores
        )
        st.plotly_chart(fig_dist_mod_publica, use_container_width=True)
        df_adm_presencial = pd.DataFrame({
            'Categoria': ['Pública', 'Privada'],
            'Total': [total_presencial_publica, total_presencial_privada]
        })
        fig_dist_adm_presencial = px.pie(
            df_adm_presencial,
            names='Categoria',
            values='Total',
            title="Modalidade Presencial",
            hole=0.3,
            color='Categoria',
            color_discrete_map=mapa_de_cores
        )
        st.plotly_chart(fig_dist_adm_presencial, use_container_width=True)
    with c2:
        df_mod_privada = pd.DataFrame({
            'Modalidade': ['Presencial', 'Remota (EAD)'],
            'Total': [total_presencial_privada, total_remota_privada]
        })
        fig_dist_mod_privada = px.pie(
            df_mod_privada,
            names='Modalidade',
            values='Total',
            title="Instituições Privadas",
            hole=0.3,
            color='Modalidade',
            color_discrete_map=mapa_de_cores
        )
        st.plotly_chart(fig_dist_mod_privada, use_container_width=True)
        df_adm_remota = pd.DataFrame({
            'Categoria': ['Pública', 'Privada'],
            'Total': [total_remota_publica, total_remota_privada]
        })
        fig_dist_adm_remota = px.pie(
            df_adm_remota,
            names='Categoria',
            values='Total',
            title="Modalidade Remota (EAD)",
            hole=0.3,
            color='Categoria',
            color_discrete_map=mapa_de_cores
        )
        st.plotly_chart(fig_dist_adm_remota, use_container_width=True)

with tab3:
    st.markdown(f"##### Dados Filtrados ({tipo_analise} - {ano_selecionado})")
    st.dataframe(df_filtrado)
    @st.cache_data
    def convert_df_to_csv(df): return df.to_csv(index=False).encode('utf-8')
    csv = convert_df_to_csv(df_filtrado)
    st.download_button(label="Baixar dados como CSV", data=csv, file_name=f'{tipo_analise.lower()}_{ano_selecionado}.csv', mime='text/csv')

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