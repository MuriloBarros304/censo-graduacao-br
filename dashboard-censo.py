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
    path = 'https://raw.githubusercontent.com/MuriloBarros304/censo-graduacao-br/main/data/raw/tabelas_de_divulgacao_censo_da_educacao_superior_2023.xls'
    # path = 'tabelas_de_divulgacao_censo_da_educacao_superior_2023.xls'
    
    try:
        df_ingressantes = pd.read_excel(path, sheet_name="Tab3.04", header=None)
        df_concluintes = pd.read_excel(path, sheet_name="Tab3.05", header=None)
        
        df_ingressantes = df_ingressantes.iloc[7:].drop(71)
        df_ingressantes.columns = [
            'Ano', 'Grau', 'Total geral', 'Total geral publica', 'Total geral federal', 'Total geral estadual', 'Total geral municipal', 'Total geral privada',
            'Total geral com fins', 'Total geral sem fins', 'Total presencial', 'Total presencial publica', 'Total presencial federal', 'Total presencial estadual',
            'Total presencial municipal', 'Total presencial privada', 'Total presencial com fins', 'Total presencial sem fins', 'Total geral remota',
            'Total remota publica', 'Total remota federal', 'Total remota estadual', 'Total remota municipal', 'Total remota privada', 'Total remota com fins', 'Total remota sem fins'
        ]
        df_ingressantes = df_ingressantes.dropna(how='all').reset_index(drop=True)
        df_ingressantes['Ano'] = df_ingressantes['Ano'].ffill()
        df_ingressantes = df_ingressantes.fillna(0).replace({'.': 0, '-': 0})

        df_concluintes = df_concluintes.iloc[8:].drop(61)
        df_concluintes.columns = [
            'Ano', 'Grau', 'Total geral', 'Total geral publica', 'Total geral federal', 'Total geral estadual', 'Total geral municipal', 'Total geral privada',
            'Total geral com fins', 'Total geral sem fins', 'Total presencial', 'Total presencial publica', 'Total presencial federal', 'Total presencial estadual',
            'Total presencial municipal', 'Total presencial privada', 'Total presencial com fins', 'Total presencial sem fins', 'Total geral remota', 'Total remota publica',
            'Total remota federal', 'Total remota estadual', 'Total remota municipal','Total remota privada', 'Total remota com fins', 'Total remota sem fins'
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
    
    except pd.errors.EmptyDataError:
        st.error("Erro ao carregar os dados. O arquivo está vazio ou não foi encontrado.")
    except pd.errors.ParserError as e:
        st.error(f"Erro de análise ao carregar os dados. Verifique o formato do arquivo. Erro: {e}")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
        return None, None

# Carrega os dados usando a função cacheada
df_ingressantes, df_concluintes = carregar_dados()

if df_ingressantes is None or df_concluintes is None:
    st.stop() # Interrompe a execução se os dados não puderem ser carregados

# --- Sidebar com Filtros ---
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
ano_min = int(df_ativo["Ano"].min())
ano_max = int(df_ativo["Ano"].max())

anos_selecionados = st.sidebar.slider(
    "Selecione o Período:",
    min_value=ano_min,
    max_value=ano_max,
    value=(ano_min, ano_max) # Padrão: seleciona o intervalo completo
)

# Desempacota os anos selecionados
ano_inicio, ano_fim = anos_selecionados

# Cria um texto dinâmico para os títulos
if ano_inicio == ano_fim:
    texto_anos = f"ano de {ano_inicio}"
else:
    texto_anos = f"período de {ano_inicio} a {ano_fim}"

# Filtro de grau acadêmico
graus_disponiveis = df_ativo[(df_ativo['Grau'] != 'Total') & (df_ativo['Grau'] != 'Não aplicável')]['Grau'].unique()
grau_selecionado = st.sidebar.multiselect(
    "Selecione o Grau Acadêmico:",
    options=graus_disponiveis,
    default=graus_disponiveis # Padrão para todos os graus
)

# Filtra o dataframe com base nas seleções
df_filtrado = df_ativo[
    (df_ativo['Ano'].between(ano_inicio, ano_fim)) &
    (df_ativo["Grau"].isin(grau_selecionado))
]

# --- Corpo Principal do Dashboard ---
st.title(f"Dashboard do Censo da Educação Superior")
st.markdown(f"Fonte: [Censo da Educação Superior 2023](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/censo-da-educacao-superior)")
st.markdown(f"## Análise de **{tipo_analise}** para o **{texto_anos}**")

# --- KPIs ---
st.markdown("---")
st.subheader("Visão Geral")
total_geral = df_filtrado['Total geral'].sum()
# Por categoria administrativa
total_publica = df_filtrado['Total geral publica'].sum()
total_privada = df_filtrado['Total geral privada'].sum()

# Por modalidade
total_presencial = df_filtrado['Total presencial'].sum()
total_remota = df_filtrado['Total geral remota'].sum()

# Por modalidade e categoria administrativa
total_remota_publica = df_filtrado['Total remota publica'].sum()
total_remota_privada = df_filtrado['Total remota privada'].sum()
total_presencial_publica = df_filtrado['Total presencial publica'].sum()
total_presencial_privada = df_filtrado['Total presencial privada'].sum()

# Por modalidade e categoria administrativa (detalhado)
# Públicas
pres_estadual = df_filtrado['Total presencial estadual'].sum()
pres_federal = df_filtrado['Total presencial federal'].sum()
pres_mun = df_filtrado['Total presencial municipal'].sum()
rem_estadual = df_filtrado['Total remota estadual'].sum()
rem_federal = df_filtrado['Total remota federal'].sum()
rem_mun = df_filtrado['Total remota municipal'].sum()

# Privadas
pres_com_fins = df_filtrado['Total presencial com fins'].sum()
rem_com_fins = df_filtrado['Total remota com fins'].sum()
pres_sem_fins = df_filtrado['Total presencial sem fins'].sum()
rem_sem_fins = df_filtrado['Total remota sem fins'].sum()

# Layout em colunas para os KPIs
col1, col2, col3 = st.columns(3)
col1.metric(f"Total de {tipo_analise}", f"{total_geral:,}".replace(",", "."))
col2.metric("Total em Instituições Públicas", f"{total_publica:,}".replace(",", "."))
col3.metric("Total em Instituições Privadas", f"{total_privada:,}".replace(",", "."))

# --- Gráficos ---
st.markdown("---")
mapa_de_cores = {
    # Cores Principais
    'Pública': '#005A9C',
    'Privada': '#FFAA00',
    'Presencial': "#04AD1B",
    'Remota (EAD)': "#A5BE5F",

    # Detalhes do Setor Público (Tons de Azul)
    'Federal': "#003A64",
    'Estadual': "#2165A0",
    'Municipal': "#4BCCFF",

    # Detalhes do Setor Privado (Tons de Laranja)
    'Com Fins': "#FFAA00",
    'Sem Fins': "#FF6F00"
}
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Distribuições Gerais", "Modalidades de Ensino", "Categorias Administrativas", "Pública", "Privada", "Dados Brutos"])

with tab1:
    st.markdown(f"#### Distribuição Geral de {tipo_analise} ({texto_anos})")
    c1, c2 = st.columns(2)
    with c1:
        df_adm = pd.DataFrame({
            'Categoria': ['Pública', 'Privada'],
            'Total': [total_publica, total_privada]
        })
        fig_dist_adm = px.bar(
            df_adm,
            x='Categoria',      # Eixo X com as categorias
            y='Total',          # Eixo Y com os valores numéricos
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
            x='Modalidade',     # Eixo X
            y='Total',          # Eixo Y
            title="Geral Por Modalidade de Ensino",
            color='Modalidade', # Colorir as barras pela modalidade
            color_discrete_map=mapa_de_cores,
            text_auto=True      # Adiciona os valores nas barras
        )
        st.plotly_chart(fig_dist_mod, use_container_width=True)
    df_adm_pie = pd.DataFrame({
        'Categoria': ['Pública', 'Privada'],
        'Total': [total_publica, total_privada]
    })
    fig_adm_pie = px.pie(
        df_adm_pie,
        names='Categoria',
        values='Total',
        title="Distribuição Geral por Categoria Administrativa",
        hole=0.5,
        color='Categoria',
        color_discrete_map=mapa_de_cores
    )
    st.plotly_chart(fig_adm_pie, use_container_width=True)

with tab2:
    st.markdown(f"#### Distribuição de Categorias Administrativas de {tipo_analise} por Modalidade de Ensino ({texto_anos})")
    c1, c2 = st.columns(2)
    with c1:
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
    st.markdown(f"#### Distribuição de Modalidades de Ensino de {tipo_analise} por Categoria Administrativa ({texto_anos})")
    c1, c2 = st.columns(2)
    with c1:
        df_mod_publica = pd.DataFrame({
            'Modalidade': ['Presencial', 'Remota (EAD)'],
            'Total': [total_presencial_publica, total_remota_publica]
        })
        fig_mod_publica = px.pie(
            df_mod_publica,
            names='Modalidade',
            values='Total',
            title="Instituições Públicas",
            hole=0.3,
            color='Modalidade',
            color_discrete_map=mapa_de_cores
        )
        st.plotly_chart(fig_mod_publica, use_container_width=True)
    with c2:
        df_mod_privada = pd.DataFrame({
            'Modalidade': ['Presencial', 'Remota (EAD)'],
            'Total': [total_presencial_privada, total_remota_privada]
        })
        fig_mod_privada = px.pie(
            df_mod_privada,
            names='Modalidade',
            values='Total',
            title="Instituições Privadas",
            hole=0.3,
            color='Modalidade',
            color_discrete_map=mapa_de_cores
        )
        st.plotly_chart(fig_mod_privada, use_container_width=True)

with tab4:
    st.markdown(f"#### Detalhamento de Categorias Administrativas de {tipo_analise} Para o Setor Público ({texto_anos})")
    c1, c2 = st.columns(2)
    with c1:
        df_presencial_detalhado = pd.DataFrame({
            'Categoria': ['Federal', 'Estadual', 'Municipal'],
            'Total': [pres_federal, pres_estadual, pres_mun]
        })
        fig_presencial_detalhado = px.pie(
            df_presencial_detalhado,
            names='Categoria',
            values='Total',
            title="Modalidade Presencial",
            hole=0.3,
            color='Categoria',
            color_discrete_map=mapa_de_cores
        )
        fig_presencial_detalhado.for_each_trace(lambda t: t.update(name=t.name.replace('Total presencial ', '').capitalize()))
        st.plotly_chart(fig_presencial_detalhado, use_container_width=True)
    with c2:
        df_remota_detalhado = pd.DataFrame({
            'Categoria': ['Federal', 'Estadual', 'Municipal'],
            'Total': [rem_federal, rem_estadual, rem_mun]
        })
        fig_remota_detalhado = px.pie(
            df_remota_detalhado,
            names='Categoria',
            values='Total',
            title="Modalidade Remota (EAD)",
            hole=0.3,
            color='Categoria',
            color_discrete_map=mapa_de_cores
        )
        fig_remota_detalhado.for_each_trace(lambda t: t.update(name=t.name.replace('Total remota ', '').capitalize()))
        st.plotly_chart(fig_remota_detalhado, use_container_width=True)

with tab5:
    st.markdown(f"#### Detalhamento de Categorias Administrativas de {tipo_analise} Para o Setor Privado ({texto_anos})")
    c1, c2 = st.columns(2)
    with c1:
        df_presencial_privada = pd.DataFrame({
            'Categoria': ['Com Fins', 'Sem Fins'],
            'Total': [pres_com_fins, pres_sem_fins]
        })
        fig_presencial_privada = px.pie(
            df_presencial_privada,
            names='Categoria',
            values='Total',
            title="Modalidade Presencial",
            hole=0.3,
            color='Categoria',
            color_discrete_map=mapa_de_cores
        )
        fig_presencial_privada.for_each_trace(lambda t: t.update(name=t.name.replace('Total presencial ', '').replace(' fins', '').capitalize()))
        st.plotly_chart(fig_presencial_privada, use_container_width=True)
    with c2:
        df_remota_privada = pd.DataFrame({
            'Categoria': ['Com Fins', 'Sem Fins'],
            'Total': [rem_com_fins, rem_sem_fins]
        })
        fig_remota_privada = px.pie(
            df_remota_privada,
            names='Categoria',
            values='Total',
            title="Modalidade Remota (EAD)",
            hole=0.3,
            color='Categoria',
            color_discrete_map=mapa_de_cores
        )
        fig_remota_privada.for_each_trace(lambda t: t.update(name=t.name.replace('Total remota ', '').replace(' fins', '').capitalize()))
        st.plotly_chart(fig_remota_privada, use_container_width=True)

with tab6:
    st.markdown(f"#### Dados Filtrados ({tipo_analise} - {texto_anos})")
    st.dataframe(df_filtrado)
    @st.cache_data
    def convert_df_to_csv(df): return df.to_csv(index=False).encode('utf-8')
    csv = convert_df_to_csv(df_filtrado)
    st.download_button(label="Baixar dados como CSV", data=csv, file_name=f'{tipo_analise.lower()}_{anos_selecionados}.csv', mime='text/csv')

# --- Comparação entre Ingressantes e Concluintes ---
st.markdown("---")
st.subheader(f"Ingressantes vs. Concluintes ({texto_anos})")
if grau_selecionado:
    st.subheader("Comparação de Ingressantes e Concluintes em Valores Absolutos")
    st.markdown(f"Analisando os graus: **{', '.join(grau_selecionado)}**")

    # Filtrar ambos os dataframes com base nas seleções da sidebar
    df_ing_filtrado = df_ingressantes[
        (df_ingressantes['Ano'].between(ano_inicio, ano_fim)) &
        (df_ingressantes["Grau"].isin(grau_selecionado))
    ]
    df_con_filtrado = df_concluintes[
        (df_concluintes["Ano"].between(ano_inicio, ano_fim)) &
        (df_concluintes["Grau"].isin(grau_selecionado))
    ]

    # Calcular totais para a métrica
    total_ing = df_ing_filtrado['Total geral'].sum()
    total_con = df_con_filtrado['Total geral'].sum()
    proporcao = (total_con / total_ing ) * 100 if total_ing > 0 else 0

    st.metric(
        label=f"Proporção Concluintes / Ingressantes no {texto_anos}",
        value=f"{proporcao:.2f} %",
        help="Proporção de alunos que concluíram em relação aos ingressantes no período selecionado. Esta métrica ajuda a entender a retenção e conclusão dos alunos nas instituições de ensino superior. Fórmula utilizada: (Total Concluintes / Total Ingressantes) * 100."
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
    df_comparativo_plot = pd.DataFrame(dados_comparativos).melt( # Transformando o DataFrame para o formato longo
        id_vars='Métrica', var_name='Tipo', value_name='Número de Alunos'
    )

    # Gráfico de barras agrupado
    fig_comparativo = px.bar(
        df_comparativo_plot, x='Métrica', y='Número de Alunos', color='Tipo',
        barmode='group', title=f"Comparativo Detalhado para o {texto_anos}",
        labels={'Número de Alunos': 'Total de Alunos', 'Métrica': 'Categoria'},
        text_auto=True, color_discrete_map={'Ingressantes':"#F9C825", 'Concluintes':"#D90505"}
    )
    st.plotly_chart(fig_comparativo, use_container_width=True)

    st.markdown("---")
    st.subheader("Comparação de Ingressantes e Concluintes em Taxa de Aproveitamento")

    st.sidebar.markdown("### Filtros da Taxa de Aproveitamento")

    # Slider para selecionar o intervalo de anos de INGRESSO
    anos_disponiveis = sorted(df_ingressantes['Ano'].unique())
    anos_ingresso_selecionados = st.sidebar.slider(
        "Selecione o período de ingresso para a análise:",
        min_value=min(anos_disponiveis),
        max_value=max(anos_disponiveis) - 5, # Garante que há dados de conclusão
        value=(min(anos_disponiveis), max(anos_disponiveis) - 5), # Padrão: seleciona o intervalo completo menos 5 anos (defasagem padrão)
        step=1
    )

    # Input para a defasagem de anos
    defasagem_anos = st.sidebar.number_input(
        "Defasagem de anos para conclusão:",
        min_value=1,
        max_value=10,
        value=5
    )

    # Gera a lista de anos de ingresso a partir da seleção do slider
    anos_ing = range(anos_ingresso_selecionados[0], anos_ingresso_selecionados[1] + 1)

    @st.cache_data # Usando cache para otimizar os cálculos
    def calcular_taxas(dicionario_modalidades, _df_ingressantes, _df_concluintes, anos_ingresso, defasagem):
        records = []
        for ano in anos_ingresso:
            ano_conc = ano + defasagem
            if ano_conc in _df_concluintes['Ano'].unique():
                for nome, (c_ing, c_conc) in dicionario_modalidades.items():
                    ing = _df_ingressantes.loc[_df_ingressantes['Ano']==ano, c_ing].sum()
                    conc = _df_concluintes.loc[_df_concluintes['Ano']==ano_conc, c_conc].sum()
                    taxa = (conc/ing*100) if ing>0 else 0
                    records.append({
                        'Ano Ingresso': ano,
                        'Ano Conclusão': ano_conc,
                        'Categoria': nome,
                        'Taxa de Aproveitamento (%)': round(taxa, 2)
                    })
        return pd.DataFrame(records)

    # --- Dicionários de Taxas ---
    taxas_geral = {'Taxa Geral': ('Total geral', 'Total geral')}
    taxas_setor = {'Pública': ('Total geral publica', 'Total geral publica'), 'Privada': ('Total geral privada', 'Total geral privada')}
    taxas_modalidade = {'Presencial': ('Total presencial', 'Total presencial'), 'Remota (EAD)': ('Total geral remota', 'Total geral remota')}
    taxas_detalhe_pub = {'Federal': ('Total geral federal', 'Total geral federal'), 'Estadual': ('Total geral estadual', 'Total geral estadual'), 'Municipal': ('Total geral municipal', 'Total geral municipal')}
    taxas_detalhe_priv = {'Com Fins': ('Total geral com fins', 'Total geral com fins'), 'Sem Fins': ('Total geral sem fins', 'Total geral sem fins')}


    # --- Visão Geral da Taxa de Aproveitamento ---
    st.markdown(f"##### Visão Geral para uma defasagem de {defasagem_anos} anos")
    df_taxa_geral = calcular_taxas(taxas_geral, df_ingressantes, df_concluintes, anos_ing, defasagem_anos)
    if not df_taxa_geral.empty:
        fig_geral = px.line(df_taxa_geral, x='Ano Conclusão', y='Taxa de Aproveitamento (%)', markers=True, color_discrete_sequence=['#d62728'])
        fig_geral.update_yaxes(ticksuffix="%")
        fig_geral.update_xaxes(dtick=1)
        st.plotly_chart(fig_geral, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado para o período e defasagem selecionados.")

    st.markdown("### Análise Detalhada da Taxa de Aproveitamento")
    tab1, tab2, tab3, tab4 = st.tabs(["Por Categoria Administrativa", "Por Modalidade de Ensino", "Público", "Privado"])

    with tab1:
        df_plot = calcular_taxas(taxas_setor, df_ingressantes, df_concluintes, anos_ing, defasagem_anos)
        fig = px.line(df_plot, x='Ano Conclusão', y='Taxa de Aproveitamento (%)', color='Categoria', markers=True, color_discrete_map=mapa_de_cores, title='Taxa de Aproveitamento por Categoria Administrativa')
        fig.update_yaxes(ticksuffix="%")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True, grid=True)
        with st.expander("Ver dados da tabela"):
            st.dataframe(df_plot)

    with tab2:
        df_plot = calcular_taxas(taxas_modalidade, df_ingressantes, df_concluintes, anos_ing, defasagem_anos)
        fig = px.line(df_plot, x='Ano Conclusão', y='Taxa de Aproveitamento (%)', color='Categoria', markers=True,color_discrete_map=mapa_de_cores, title='Taxa de Aproveitamento por Modalidade de Ensino')
        fig.update_yaxes(ticksuffix="%")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Ver dados da tabela"):
            st.dataframe(df_plot)

    with tab3:
        df_plot = calcular_taxas(taxas_detalhe_pub, df_ingressantes, df_concluintes, anos_ing, defasagem_anos)
        fig = px.line(df_plot, x='Ano Conclusão', y='Taxa de Aproveitamento (%)', color='Categoria', markers=True, color_discrete_map=mapa_de_cores, title='Taxa de Aproveitamento no Setor Público')
        fig.update_yaxes(ticksuffix="%")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Ver dados da tabela"):
            st.dataframe(df_plot)

    with tab4:
        df_plot = calcular_taxas(taxas_detalhe_priv, df_ingressantes, df_concluintes, anos_ing, defasagem_anos)
        fig = px.line(df_plot, x='Ano Conclusão', y='Taxa de Aproveitamento (%)', color='Categoria', markers=True, color_discrete_map=mapa_de_cores, title='Taxa de Aproveitamento no Setor Privado')
        fig.update_yaxes(ticksuffix="%")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Ver dados da tabela"):
            st.dataframe(df_plot)

        # Exibir a tabela de dados
        with st.expander("Ver dados da tabela"):
            st.dataframe(df_plot)
    
else:
    st.warning("Selecione pelo menos um Grau Acadêmico na barra lateral para ver a comparação.")

st.markdown("---")
st.markdown("#### Sobre o Dashboard")
st.markdown("""
Este dashboard foi desenvolvido para facilitar a visualização e análise dos dados do Censo da Educação Superior de 2023. Ele permite que usuários explorem as informações sobre ingressantes e concluintes, filtrando por ano e grau acadêmico.
A análise inclui gráficos interativos que ajudam a entender as tendências e distribuições dos dados, além de permitir comparações diretas entre ingressantes e concluintes.
Para mais informações, consulte a [documentação do Streamlit](https://docs.streamlit.io/) e o [repositório do projeto](https://github.com/MuriloBarros304/censo-graduacao-br).
### Autores
- [Murilo Barros](https://github.com/MuriloBarros304)
- [Pablo Paraguai](https://github.com/pabloart702)""")

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.image("images/DCA2.gif", width=150)
with c2:
    st.image("images/ufrn.png", width=150)
