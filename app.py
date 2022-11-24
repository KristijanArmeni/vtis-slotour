
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

st.markdown("Izhodiščni podatki so predstavljeni v spodnji tabeli. ")

df

questions = "\n".join([f"1. {q} (`{k}`)" for q, k in zip(new_cols.keys(), new_cols.values())])

st.markdown(
    "Stolpci predstavljajo odgovore na naslednja vprašanja: "
)

st.markdown(f"{questions}")

st.markdown("Kodiranja:")
st.markdown("`n_rec`: " + " let; ".join([f"{value_map1[key]} = {key}" for key in value_map1.keys()]))
st.markdown("`n_incoming`: "+" let; ".join([f"{value_map2[key]} = {key}" for key in value_map2.keys()]))
st.markdown("`years_abroad`: "+" let; ".join([f"{years_abroad_map[key]} = {key}" for key in years_abroad_map.keys()]))

# ===== DEMOGRAPHICS ===== #
st.markdown("## Leta bivanja v tujini")

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6.5, 4.5))

# get counts and compute percents and format as text for annotation
dat = None
dat = pd.DataFrame(df.groupby("years_abroad").size(), columns=["counts"])
dat["perc"] = ((dat["counts"]/len(df))*100).round(decimals=1)
dat["text"] = dat.perc.apply(lambda x: f"{x}%") + dat.counts.apply(lambda x: f" ({x})")

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
for i, v in enumerate(dat.text.tolist()):
    ax.text(x=ax.get_xticks()[i], y=dat.perc[i]+1, s=v, ha="center")
plt.tight_layout()
sns.despine()

st.pyplot(fig=fig)

# ===== DRŽAVA BIVANJA ===== #
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

# ===== ŠTEVILO PROMOCIJ ===== #
st.markdown("## Kako in koliko člani društva VTIS promovirajo Slovenijo?")

st.markdown("### Število priporočil")

groups = ["ismember", "n_rec"]
ismember_count = df.groupby("ismember")["n_rec"].transform("sum")
dat_count = df.groupby(groups).agg({"n_rec": "count"})
dat_total = df.groupby("ismember").agg({"n_rec": "count"})
dat_count['perc'] = (dat_count.div(dat_total, level="ismember")*100).round(decimals=0).astype(int)
dat_count['text'] = dat_count.perc.apply(lambda x: f"{x}%") + dat_count.n_rec.apply(lambda x: f"\n({x})")

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6.5, 4.5))
shrinkage = 0.9
ax = sns.histplot(df,
                  ax=ax,
                  x='n_rec',
                  hue='ismember',
                  discrete=True,
                  multiple='dodge',
                  binwidth=1,
                  shrink=shrinkage,
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

xloc = np.tile(ax.get_xticks(), 2).astype(float)
xloc[0:5] = xloc[0:5] + shrinkage/4
xloc[5::] = xloc[5::] - shrinkage/4

for i, v in enumerate(dat_count.text.tolist()):
    ax.text(x=xloc[i], y=dat_count.perc[i]+2, s=v, ha="center")

ax.annotate(text=f"N = {len(df)}", xy=[ax.get_xlim()[0]*-0.01, 90], fontsize=12)
sns.move_legend(ax, loc='upper right', title="")
plt.tight_layout()
sns.despine()

st.pyplot(fig=fig)

# ===== 
st.markdown("### Število obiskov")

# format percents texts for plotting on top of histograms
groups = ["ismember", "n_incoming"]
dv = "n_incoming"
dat_count = df.groupby(groups).agg({dv: "count"})

# add categories that have not occured just for plotting
dat_count.loc[('Nisem član/-ica', 3), "n_incoming"] = 0
dat_count.loc[('Nisem član/-ica', 5), "n_incoming"] = 0
dat_count.n_incoming = dat_count.n_incoming.astype(int)
dat_count = dat_count.sort_index()

# compute counts and format percentages
dat_total = df.groupby("ismember").agg({dv: "count"})
dat_count['perc'] = (dat_count.div(dat_total, level="ismember")*100).round(decimals=0).astype(int)
dat_count['text'] = dat_count.perc.apply(lambda x: f"{x}%") + dat_count[dv].apply(lambda x: f"\n({x})")

# FIGURE
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6.5, 4.5))

sns.histplot(df, 
             ax=ax,
             x='n_incoming',
             hue='ismember',
             discrete=True,
             multiple='dodge',
             shrink=0.9,
             common_norm=False,
             legend=True,
             stat='percent',
             edgecolor='w')

ax.set(ylabel="% odgovorov",
       xlabel="št. ljudi")
ax.set_title(label="Približno koliko ljudi je Slovenijo obiskalo zaradi vašega predloga,\nodkar ste prvič odšli v tujino?",
             fontsize=14)
ax.set_xticks(ticks=list(value_map2.values()), labels=value_map2.keys())
ax.set_ylim([0, 100])

# set x-axis positions for text annotations
xloc = dat_count.index.get_level_values("n_incoming").to_numpy().astype(float)
half=len(dat_count)//2
xloc[0:half] = xloc[0:half] + shrinkage/4
xloc[half::] = xloc[half::] - shrinkage/4

for i, v in enumerate(dat_count.text.tolist()):
    ax.text(x=xloc[i], y=dat_count.perc[i]+2, s=v, ha="center")

ax.annotate(text=f"N = {len(df)}", xy=[ax.get_xlim()[0]*-0.01, 90], fontsize=12)
sns.move_legend(ax, loc='upper right', title="")
sns.despine()

st.pyplot(fig=fig)

# ===== NAJBOLJ PROMOVIRANE REGIJE ===== #
st.markdown("## Najbolj promovirane regije")
regs = ", ".join([a for a in df.regions]).split(", ")

dat = []
dat = pd.DataFrame(np.array(regs), columns=["regs"])
df3 = pd.DataFrame(index=range(len(dat.value_counts())), columns=["name", "count"])
df3['name'] = [a[0] for a in dat.value_counts().index]
df3['count'] = dat.value_counts().values

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6.5, 4.5))

sns.barplot(df3,
            x="count",
            y="name",
            ax=ax,
            color=colors[0],
            edgecolor='w')

ax.set(ylabel="",
       xlabel="št. odgovorov")
ax.set_title(label="Obisk katerih regij jim najpogosteje predlagate?",
             fontsize=14)

ax.annotate(text=f"N = {len(df)}", xy=[120, ax.get_ylim()[0]*0.9], fontsize=12)
sns.despine()

st.pyplot(fig=fig)

# ===== RAZLOGI ZA PROMOCIJO ==== #
st.markdown("## Razlogi za promocijo")

options = [
    "Ponosen/-na sem na Slovenijo",
    "Prepričan/-a sem, da bo tujcem v Sloveniji všeč",
    "Želim pomagati slovenskemu turizmu",
    "Samo, če me tujci vprašajo za priporočilo, jim predlagam, kam lahko grejo v Sloveniji",
    "Ne promoviram potovanj v Slovenijo",
]

# first find all given options and add a full stop afterwards (instead of comma)
a = []
for s in df.why_promote.to_list():
    for o in options:
        s = s.replace(o, o + ".")
    a.append(s)

# now find the fullstop-comma combination and replace with just a comma
tmp = [e.replace(".,", ".") for e in a]

# now split at fullstop and count
b = [e.split(".") for e in tmp]
c = [e.strip() for b2 in b for e in b2]
c = [e for e in c if e != ""]

df3 = pd.DataFrame(c, columns=["why"]).groupby("why").size().sort_values(ascending=False)
df3 = pd.DataFrame(df3, columns=["count"])
df3['why'] = df3.index
df3 = df3.loc[df3["count"] > 1, :]

# ==== FIGURE
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 4))

# FIGURE 
sns.barplot(df3, 
            ax=ax,
            x='count',
            y='why',
            color=colors[0],
            edgecolor='w')

fs=22
ax.set_title(label="Lahko delite z nami razloge, \n" + \
                   "zakaj promovirate lepote Slovenije z vašo mrežo v tujini?",
             fontsize=fs) 
ax.set_ylabel(ylabel="")
ax.set_xlabel(xlabel="št. odgovorov", fontsize=fs)
ylabs = ax.get_yticklabels()
ylabs[3] = "Predlagam samo, če me vprašajo"
ax.set_yticklabels(labels=ylabs, rotation=0)
ax.tick_params(labelsize=22)
sns.despine()
plt.tight_layout()

st.pyplot(fig=fig)
