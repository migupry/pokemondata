import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import seaborn as sns
import plotly.express as px
from functools import reduce

st.title("Exploração dos Dados de Pokémon")

st.info('''Utilize um PC, ou a versão Desktop do site no celular, para melhor visualização.''')

# padrão de fundo gerado no site https://www.magicpattern.design/tools/css-backgrounds
# cores convertidas para rgba (para aplicar alpha) com http://hex2rgba.devoth.com/
page_bg_img = '''
<style>
.stApp {
background-color: rgba(229, 229, 247, 0.2);
background-size: 10px 10px;
background-image: repeating-linear-gradient(45deg, rgba(252, 118, 153, 0.2) 0, rgba(252, 118, 153, 0.2) 1px, rgba(229, 229, 247, 0.2) 0, rgba(229, 229, 247, 0.2) 50%);
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

# fonte cores: https://gist.github.com/apaleslimghost/0d25ec801ca4fc43317bcff298af43c3
type_colors = {	"normal": '#A8A77A', "fire": '#EE8130',	"water": '#6390F0',	"electric": '#F7D02C',	"grass": '#7AC74C',	"ice": '#96D9D6',	"fighting": '#C22E28',	"poison": '#A33EA1',	"ground": '#E2BF65',	"flying": '#A98FF3',	"psychic": '#F95587',	"bug": '#A6B91A',	"rock": '#B6A136',	"ghost": '#735797',	"dragon": '#6F35FC',	"dark": '#705746',	"steel": '#B7B7CE',"fairy": '#D685AD'}

# Carrega Dataframe e Renomeia Colunas
@st.cache(suppress_st_warning=True)
def load_csv():
  return pd.read_csv("https://github.com/migupry/pokemondata/raw/main/pokemon.csv").rename(columns={
    'abilities': "Habilidades",
    "name": "Nome",
    "pokedex_number": "Nº na Pokédex",
    "generation": "Geração",
    "japanese_name": "Nome Japonês",
    "percentage_male": "% Macho",
    "base_egg_steps": "Passos Ovo Base",
    "base_happiness": "Felicidade Base",
    "base_total": "Total Base",
    "capture_rate": "Taxa de Captura",
    "classfication": "Classificação",
    "experience_growth": "Experiência p/ Crescer",
    "is_legendary": "É lendario?",
    "type1": "Tipo",
    "type2": "Tipo2",
    "attack": "Ataque",
    "defense": "Defesa",
    "height_m": "Altura (m)",
    "hp": "HP",
    "sp_attack": "Ataque Especial",
    "sp_defense": "Defesa Especial",
    "speed": "Velocidade",
    "weight_kg": "Peso (kg)"
  }).rename(columns={f"against_{tipo}": f"Contra {tipo.capitalize()}" for tipo in list(type_colors.keys()) + ["fight"]})
df = load_csv();
st.header('Base de dados completa:')
st.write(df)

#Função para gerar checkboxes de gerações, retornando um dataframe filtrado pelos checkboxes
def gen_checkboxes(key):
  st.write("Selecionar Gerações:")
  # cria 7 checkboxes para as gerações numa estrutura de 7 colunas
  gens = [col.checkbox(label=str(i+1), key=key+str(i), value = True) for i, col in enumerate(st.columns(7))]
  # gera um erro caso nenhuma geração seja selecionada
  if sum(gens) == 0:
    st.error("Selecione ao menos uma geração! (mostrando todas)")
  # filtra o dataframe com base nas gerações, utilizando todas caso nenhuma seja selecionada
  df_gens = df if sum(gens) == 0 else df[reduce(lambda x, y: x | y, [gens[i] and df["Geração"] == i+1 for i in range(7)])]
  st.write(f"{df_gens.shape[0]} pokémons selecionados")
  return df_gens

#############################################################################
#                        Gráficos de Pizza dos Tipos                        #
#############################################################################
st.header("Tipos de Pokémon")

st.info('Em todo o universo Pokemóm temos 801 criaturas, sendo 18 tipos, e divididos em 7 gerações descobertas. Cada criatura Pokemon possui as mesmas características dos indivíduos de sua espécie, como valor de ataque, defesa, HP, entre outras. Dessa forma, buscamos entender primeiramente se a proporção de tipos é constante ao longo das gerações.')

df_gen_types = gen_checkboxes("types")
pk_types = df_gen_types.groupby("Tipo").size().reset_index(name='Quantidade')
# seta as cores na ordem dos mais frequentes (exigido pelo plotly) buscando no dicionário "type_colors"
@st.cache(suppress_st_warning=True)
def pie_chart(pk_types):
  pk_colors = [type_colors[t] for t in pk_types.sort_values(by="Quantidade",ascending=False).Tipo.values]
  return px.pie(pk_types, values='Quantidade', names = 'Tipo', color_discrete_sequence = pk_colors, title='Percentual dos tipos de Pokémon:')
fig_pie = pie_chart(pk_types)

st.plotly_chart(fig_pie)

st.info('Observando o proporcional de tipos ao longo das 7 gerações podemos observar uma predominância de Pokemons de Água, Normal, Grama e Inseto, correspondendo a quase 50% dos Pokemons, o também evidencia a raridade dos tipo Voador, Fada, Gelo e Metal.')

#############################################################################
#                          Gráficos de Dispersão                            #
#############################################################################
st.header("Gráficos de dispersão:")
st.info('No segundo gráfico, buscamos encontrar padrões entre as característcas e habilidades entre cada tipo ao longo das gerações')
options = ["Ataque", "Defesa", "HP", "Ataque Especial", "Defesa Especial", "Velocidade", "Altura (m)", "Peso (kg)"]
col1, col2 = st.columns(2)
feat_x = col1.radio("Feature para o eixo x do gráfico", options)
feat_y = col2.radio("Feature para o eixo y do gráfico", options, index=1)

df_gen_scatter = gen_checkboxes("scatter")

@st.cache(suppress_st_warning=True)
def scatter_plot(df_gen_scatter):
  fig_scat = px.scatter(df_gen_scatter, x=feat_x, y=feat_y, color="Tipo", color_discrete_map = type_colors, hover_data=['Nome', "Nº na Pokédex", "Geração"])
  # remove o texto "Type=" das legendas de cores
  fig_scat.for_each_trace(lambda t: t.update(name = {f"Tipo={t}": t for t in type_colors.keys()}[t.name]))
  return fig_scat
  
fig_scat = scatter_plot(df_gen_scatter)

st.plotly_chart(fig_scat)

st.info('''Nos gráficos de dispersão podemos observar algumas correlações entre atributos, principalmente quando filtramos por tipo.\n
Podemos destacar a correlação entre os atributos Ataque e Defesa no tipo Normal,
e entre Ataque Especial e Defesa Especial nos pokémons de tipo Elétrico.''')
st.info('''Existem apenas 27 pokémons do tipo Dragão e estes apresentam padrões em diversos atributos:
Podemos ver correlações entre Ataque x Velocidade x HP, bem como Peso e HP.''')
st.info('''Esperávamos uma correlação entre Peso e Defesa, que não foi observada em nenhum tipo de pokémon na base de dados.''')

#############################################################################
#                            Comparar Pokémons                              #
#############################################################################
st.header("Comparar pokémons:")
st.info('Abaixo podemos comparar cada espécie Pokémon e seus atributos visualizando suas imagens.')
pk_compare = [col.selectbox(f'Pokémon {i + 1}', df.Nome, (0,3)[i] ) for i, col in enumerate(st.columns(2))]
# Baixa as imagens dos pokémons e imprime na tela
getPkPic = lambda n: f"https://github.com/kvpratama/gan/raw/master/pokemon/data/pokemon/{n}.jpg"
pk_imgs = [col.image(getPkPic(df[df.Nome == pk_compare[i]]['Nº na Pokédex'].values[0])) for i, col in enumerate(st.columns(2))]

st.markdown('<style>div.css-1ezm4r7 > div.css-3ggkhc{font-size: 1.75rem}</style>', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)
pk_infos = [cols[i].metric(param, f'{df[df.Nome == pk_compare[j]][param].values[0]}')
  for i, param in enumerate(['Nº na Pokédex', 'Geração', 'Tipo'])
  for j, cols in enumerate([[col1, col2, col3], [col4, col5, col6]])]

for o_slice in np.array_split(options, 3):
  for i_o, o in enumerate(o_slice):
    val1 = df[df.Nome == pk_compare[0]][o].values[0]
    val2 = df[df.Nome == pk_compare[1]][o].values[0]
    [col1,col2,col3][i_o].metric(o, f'{val1}', f'{round( val1 - val2, 2)}')
    [col4,col5,col6][i_o].metric(o, f'{val2}', f'{round( val2 - val1, 2)}')
