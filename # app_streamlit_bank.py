import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title='Análise de Campanha Bancária',
    page_icon=r"C:\Users\rodrigo\Documents\ebac\Desenvolvimento de aplicações com Python\Streamlit III\tarefa1\Profissão Cientista de Dados M19 Pratique 1\img\telmarketing_icon.png",
    layout="wide",
    initial_sidebar_state='expanded'
)

st.title('Análise de Campanha Bancária')
st.markdown("---")

# Exibir imagem na sidebar
image = Image.open(r"C:\Users\rodrigo\Documents\ebac\Desenvolvimento de aplicações com Python\Streamlit III\tarefa1\Profissão Cientista de Dados M19 Pratique 1\img\Bank-Branding.jpg")
st.sidebar.image(image)

# Carregar dados
@st.cache_data
def carregar_dados():
    return pd.read_csv('bank-additional-full.csv', sep=';')

bank = carregar_dados()

# Mostrar dataframe com checkbox
if st.sidebar.checkbox('Mostrar os dados brutos'):
    st.dataframe(bank.head(10))

# --- FILTROS SIDEBAR ---
st.sidebar.header('Filtros')

# Escolaridade
escolaridades = sorted(bank['education'].unique())
escolaridade = st.sidebar.selectbox('Escolaridade:', escolaridades)

# Faixa etária (slider)
idade_min = int(bank['age'].min())
idade_max = int(bank['age'].max())
faixa_idade = st.sidebar.slider('Faixa Etária:', min_value=idade_min, max_value=idade_max, value=(idade_min, idade_max))

# Profissão
profissoes = sorted(bank['job'].unique())
profissao_selecionada = st.sidebar.selectbox('Selecione a profissão:', profissoes)

# Aplicar filtros
dados_filtrados = bank[
    (bank['education'] == escolaridade) &
    (bank['age'] >= faixa_idade[0]) &
    (bank['age'] <= faixa_idade[1]) &
    (bank['job'] == profissao_selecionada)
]

# Exibir resultados
st.markdown(f"### Total de registros filtrados: {dados_filtrados.shape[0]}")
if not dados_filtrados.empty:
    st.dataframe(dados_filtrados[['age', 'job', 'education', 'y']].head())

    # Métricas
    total_sim = dados_filtrados[dados_filtrados['y'] == 'yes'].shape[0]
    total_nao = dados_filtrados[dados_filtrados['y'] == 'no'].shape[0]
    taxa_conversao = (total_sim / dados_filtrados.shape[0]) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de 'Sim'", total_sim)
    col2.metric("Total de 'Não'", total_nao)
    col3.metric("Taxa de Conversão", f"{taxa_conversao:.2f}%")

    # Gráfico de barras da resposta (y)
    st.subheader("Distribuição da resposta (y)")
    resposta_contagem = dados_filtrados['y'].value_counts().reset_index()
    resposta_contagem.columns = ['Resposta', 'Total']

    fig_bar, ax_bar = plt.subplots()
    sns.barplot(data=resposta_contagem, x='Resposta', y='Total', palette='Set2', ax=ax_bar)
    ax_bar.set_title('Distribuição das Respostas à Campanha')
    st.pyplot(fig_bar)

    # Exportar CSV
    csv = dados_filtrados.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Baixar dados filtrados em CSV",
        data=csv,
        file_name='dados_filtrados.csv',
        mime='text/csv'
    )

# Histograma de idade com botão
if st.sidebar.button('📊 Gerar histograma de idade'):
    fig_hist, ax_hist = plt.subplots()
    sns.histplot(dados_filtrados['age'], kde=True, bins=20, ax=ax_hist)
    ax_hist.set_title(f'Histograma de Idade - {profissao_selecionada} | {escolaridade}')
    st.pyplot(fig_hist)

# Gráfico por profissão (barra lado a lado) com rolagem horizontal
st.subheader("📊 Resposta à campanha por profissão")

# Preparar dados agrupados
resposta_por_profissao = (
    bank
    .groupby(['job', 'y'])
    .size()
    .unstack(fill_value=0)
    .sort_values(by='yes', ascending=False)
)

jobs = resposta_por_profissao.index.tolist()
# Define largura proporcional ao número de profissões (0.5 polegada por profissão, mínimo 10)
largura_figura = max(10, len(jobs) * 0.5)

fig_prof, ax_prof = plt.subplots(figsize=(largura_figura, 5))

# Plot barra lado a lado para 'no' e 'yes'
resposta_por_profissao.plot(kind='bar', stacked=False, color=['#F44336', '#4CAF50'], ax=ax_prof)

ax_prof.set_title('Respostas por Profissão')
ax_prof.set_ylabel('Total de Pessoas')
ax_prof.set_xlabel('Profissão')
ax_prof.legend(title='Resposta')
plt.xticks(rotation=45, ha='right')

st.pyplot(fig_prof)
