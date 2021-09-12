import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import seaborn as sns
import plotly.express as px
from functools import reduce

st.title("Exploração dos Dados de Pokémon")

# padrão de fundogerado no site https://www.magicpattern.design/tools/css-backgrounds
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
df = pd.read_csv("https://github.com/migupry/pokemondata/raw/main/pokemon.csv").rename(columns={
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

df_gen_types = gen_checkboxes("types")
pk_types = df_gen_types.groupby("Tipo").size().reset_index(name='Quantidade')
# seta as cores na ordem dos mais frequentes (exigido pelo plotly) buscando no dicionário "type_colors"
pk_colors = [type_colors[t] for t in pk_types.sort_values(by="Quantidade",ascending=False).Tipo.values]
fig_pie = px.pie(pk_types, values='Quantidade', names = 'Tipo', color_discrete_sequence = pk_colors, title='Percentual dos tipos de Pokémon:')

st.plotly_chart(fig_pie)

#############################################################################
#                          Gráficos de Dispersão                            #
#############################################################################
st.header("Gráficos de dispersão:")

options = ["Ataque", "Defesa", "HP", "Ataque Especial", "Defesa Especial", "Velocidade", "Altura (m)", "Peso (kg)"]
col1, col2 = st.columns(2)
feat_x = col1.radio("Feature para o eixo x do gráfico", options)
feat_y = col2.radio("Feature para o eixo y do gráfico", options, index=1)

df_gen_scatter = gen_checkboxes("scatter")
fig_scat = px.scatter(df_gen_scatter, x=feat_x, y=feat_y, color="Tipo", color_discrete_map = type_colors, hover_data=['Nome', "Nº na Pokédex", "Geração"])

# remove o texto "Type=" das legendas de cores
fig_scat.for_each_trace(lambda t: t.update(name = {f"Tipo={t}": t for t in type_colors.keys()}[t.name]))

st.plotly_chart(fig_scat)


#############################################################################
#                            Comparar Pokémons                              #
#############################################################################
st.header("Comparar pokémons:")
pk_compare = [col.selectbox(f'Pokémon {i + 1}', df.Nome, (0,3)[i] ) for i, col in enumerate(st.columns(2))]
# Baixa as imagens dos pokémons e imprime na tela
getPkPic = lambda n: f"https://github.com/kvpratama/gan/raw/master/pokemon/data/pokemon/{n}.jpg"
pk_imgs = [col.image(getPkPic(df[df.Nome == pk_compare[i]]['Nº na Pokédex'].values[0])) for i, col in enumerate(st.columns(2))]

col1, col2, col3, col4, col5 = st.columns(5)
pk_infos = [col.metric(param, f'{df[df.Nome == pk_compare[i]][param].values[0]}') for param in ['Nº na Pokédex', 'Geração'] for i, col in enumerate([col2, col4])]

for o in options:
  val1 = df[df.Nome == pk_compare[0]][o].values[0]
  val2 = df[df.Nome == pk_compare[1]][o].values[0]
  col2.metric(o, f'{val1}', f'{round( val1 - val2, 2)}')
  col4.metric(o, f'{val2}', f'{round( val2 - val1, 2)}')