
import numpy as np
import streamlit as st
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

st.title("Pomen Slovencev v tujini za slovenski turizem")

fname = "./data/slotour_resp.tsv"

df = pd.read_csv(fname, sep="\t", header=0)

new_cols = {'Koliko ljudem ste v zadnjih 12 mesecih predlagali potovanje v Slovenijo ali priporočili znamenitosti, aktivnosti, nastanitve, restavracije itd., ko so se že odločili za potovanje v Slovenijo in vas vprašali za priporočilo?': "n_rec",
            "Približno koliko ljudi je Slovenijo obiskalo zaradi vašega predloga, odkar ste prvič odšli v tujino? ": "n_incoming",
            "Kakšni so najpogostejši nameni obiska Slovenije tujcev, s katerimi ste se pogovarjali o njihovem potovanju v Slovenijo?": "purposes",
            "Obisk katerih regij jim najpogosteje predlagate?": "regions",
            'Kakšni so vaši predlogi za turistično manj znane lokacije (npr. Bled, Ljubljana in Piran so že na seznamu vsakega turista)?': "less_known",
            "Lahko delite z nami razloge, zakaj promovirate lepote Slovenije z vašo mrežo v tujini?": "why_promote",
            "V kateri/-h državi/-ah v tujini ste do sedaj živeli?": "countries",
            "Koliko let že prebivate ali ste prebivali v tujini?": "years_abroad",
            "Ali ste član/ica društva VTIS? ": "ismember",
            "Imate še kakšen dodaten komentar, idejo?": "comment"}

df = df.rename(columns=new_cols)

value_map1 = {"0": 0, "1-5": 1, "6-15": 2, "16-30": 3, "31+": 4}
df.n_rec = df.n_rec.replace(value_map1.keys(), value_map1.values())

value_map2 = {"0": 0, "1-10": 1, "11-30": 2, "31-50": 3, "51-100": 4, "101-200": 5, "200+": 6}
df.n_incoming = df.n_incoming.replace(value_map2.keys(), value_map2.values())

years_abroad_map = {"Manj kot 1": 0, '1-3': 1, '3-5': 2, '5-10': 3, 'Več kot 10 let': 4}
df.years_abroad = df.years_abroad.replace(years_abroad_map.keys(), years_abroad_map.values())

ismember_map = {"Redni član/-ica": "Član/-ica", "Izredni član/-ica": "Član/-ica"}
df.ismember = df.ismember.replace(ismember_map.keys(), ismember_map.values())

# get color cycle
prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

# ===== DATA ===== #
st.markdown("## Izhodiščni podatki")
df

# ===== DEMOGRAPHICS ===== #
st.markdown("## Leta bivanja v tujini")

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6.5, 4.5))

ax = sns.histplot(df,
                  ax=ax,
                  x='years_abroad',
                  discrete=True,
                  multiple='dodge',
                  shrink=0.9,
                  common_norm=False,
                  legend=True,
                  stat='percent',
                  edgecolor='w')

ax.set_xticks(ticks=list(years_abroad_map.values()), labels=years_abroad_map.keys())

ax.set(ylabel="% odgovorov", xlabel="leta bivanja v tujini")
ax.set_title(label="Koliko let že prebivate ali ste prebivali v tujini?",
             ha="center",
             fontsize=14)
ax.set_ylim([0, 100])
ax.annotate(text=f"N = {len(df)}", xy=[ax.get_xlim()[0]*-0.01, 90], fontsize=12)
#sns.move_legend(ax, loc='upper right', title="")
plt.tight_layout()
sns.despine()

st.pyplot(fig=fig)

st.markdown("## Država bivanja")

a = [e.split(", ") for e in df.countries.to_numpy()]
x = []
for e in a:
    x += e

scandinavia = ["Norveska", "Norveška", "Svedska", "Švedska", "Danska"]
typos = {
    "Grcija": "Grčija", 
    "Cile": "Čile", 
    "Urugay": "Urugvaj",
    "argentina": "Argentina",
    "srbija": "Srbija",
    "Nova zelandija": "Nova Zelandija",
        }

d = []
for e in x:
    e = e.strip()
    if e in typos.keys():
        e = typos[e]
    elif e in scandinavia:
        e = "Skandinavija"
    d.append(e)

df2 = pd.DataFrame(d, columns=["countries"]).groupby('countries').size().sort_values(ascending=False)
df2 = pd.DataFrame(df2, columns=["count"])

# count those with count <2
other = len(df2.loc[df2["count"] < 2, :])
other_list = df2.loc[df2["count"] < 2, :].index.tolist()

# only show contries with > 2 counts
df2 = df2.loc[df2["count"] > 2, :]
df2['countries'] = df2.index
df2 = pd.concat([df2, pd.DataFrame({"count": [other], "countries": ["drugo"]})]).sort_values(by="count", ascending=False)

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 3.5))
#color1 = np.asarray([0, 190, 255])/255 #00BEFF
sns.barplot(df2, 
            ax=ax,
            x='countries',
            y='count',
            color=colors[0],
            edgecolor='w')

ax.set(ylabel="št. odgovorov", 
       xlabel="država/regija")
ax.set_title(label="V kateri/-h državi/-ah v tujini ste do sedaj živeli?", 
             fontsize=14)
ax.set_xticks(ticks=ax.get_xticks(), labels=ax.get_xticklabels(), rotation=35, ha='right')
sns.despine()

st.pyplot(fig=fig)

st.markdown("## Kako in koliko člani društva VTIS promovirajo Slovenijo?")

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6.5, 4.5))

ax = sns.histplot(df,
                  ax=ax,
                  x='n_rec',
                  hue='ismember',
                  discrete=True,
                  multiple='dodge',
                  shrink=0.8,
                  common_norm=False,
                  legend=True,
                  stat='percent',
                  edgecolor='w',
                  label="Test")

ax.set(ylabel="% odgovorov", xlabel="št. ljudi")
ax.set_title(label="Koliko ljudem ste v zadnjih 12 mesecih predlagali potovanje v Slovenijo?",
             ha="center",
             fontsize=14)
ax.set_xticks(ticks=list(value_map1.values()), labels=value_map1.keys())
ax.set_ylim([0, 100])
ax.annotate(text=f"N = {len(df)}", xy=[ax.get_xlim()[0]*-0.01, 90], fontsize=12)
sns.move_legend(ax, loc='upper right', title="")
plt.tight_layout()
sns.despine()

st.pyplot(fig=fig)