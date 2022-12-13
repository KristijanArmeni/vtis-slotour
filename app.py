
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

countries = [e.split(", ") for e in df.countries.to_numpy()]

def fix_country_typos(input_list):

    scandinavia = ["Norveska", "Norveška", "Svedska", "Švedska", "Danska"]
    typos = {
        "Grcija": "Grčija", 
        "Cile": "Čile", 
        "Urugay": "Urugvaj",
        "argentina": "Argentina",
        "srbija": "Srbija",
        "Nova zelandija": "Nova Zelandija",
            }

    output_list = []
    for e in input_list:
        e = e.strip()
        if e in typos.keys():
            e = typos[e]
        elif e in scandinavia:
            e = "Skandinavija"
        output_list.append(e)

    return output_list

countries_fixed = list(map(fix_country_typos, countries))

# conver to list with a single item
x = []
for e in countries_fixed:
    x += e

df2 = pd.DataFrame(x, columns=["countries"]).groupby('countries').size().sort_values(ascending=False)
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

st.markdown("## Povprečno število priporočil (člani vs nečlani)")

# ===== STEVILO OBISKOV GLEDE NA DRZAVO BIVANJA
st.markdown("## Število obiskov glede na državo bivanja, čas bivanja v tujini in članstvo")

subs = [f"s{i+1:03}" for i in range(len(df))]
visits = df.n_incoming.to_list()
tabroad = df.years_abroad.to_list()
ismember = df.ismember.to_list()

# create data frame
dat = None
dat = pd.DataFrame(countries_fixed, columns=[f"{i+1}" for i in range(max([len(e) for e in countries]))])
dat["years_abroad"] = tabroad
dat["n_incoming"] = visits
dat["n_rec"] = df.n_rec.tolist()
dat["ismember"] = ismember
dat["sub"] = subs

# conver to long format
datlong = pd.melt(dat, id_vars=["sub", "years_abroad", "n_incoming", "n_rec", "ismember"], value_vars=[f"{i+1}" for i in range(8)], value_name="country", var_name="country_id")

# now count the countries so we can filter by responses
tmp = datlong.groupby("country", as_index=False).size()
counts = {c: cnt for c, cnt in zip(tmp.country.tolist(), tmp["size"].tolist())}

datlong["n_samples"] = [int(counts[c]) if c is not None else None for c in datlong.country.tolist()]

# funtcion to compute weights for estimated percentages
def get_weigths_values(dfin, iv, dv, dv_values):

    if iv == "country":
        threshold = 15
        dftmp = dfin.loc[dfin.n_samples > threshold].sort_values(by="n_samples").groupby([iv, dv], as_index=False).size()
    else:
        dftmp = dfin.groupby([iv, dv], as_index=False).size()

    counts = None
    counts = dftmp.groupby(iv).agg({"size": "sum"})
    dftmp["total"] = np.nan

    for c, n in zip(counts.index.to_numpy(), counts["size"].to_numpy()):
        dftmp.loc[dftmp[iv]==c, "total"] = n

    #print(f"Group: {counts.index.to_numpy()}")
    #print(f"Group counts: {counts['size'].to_numpy()}")

    dftmp["total"] = dftmp.total.astype(int)
    dftmp["weight"] = (dftmp["size"] / dftmp.total).round(decimals=2)
    dftmp["perc"] = dftmp.weight*100

    # set estimates for number of visits
    dftmp["estimates"] = dftmp[dv].replace(dv_values.keys(), dv_values.values())
    dftmp.head(5)

    return dftmp

# create a function that takes a dataframe grouped by a variable 
# and computes a weighted average of a variable
def weighted_average(df, value, weight):

    return (df[value] * df[weight]).sum() / df[weight].sum()

values = {0: 0, 1: 5, 2: 20, 3: 40, 4: 75, 5: 150, 6: 220}
tmp2 = get_weigths_values(datlong, iv="country", dv="n_incoming", dv_values=values)

avg = pd.DataFrame(tmp2.groupby("country").apply(weighted_average, "estimates", "weight"), columns=["wavg"])
avg["country"] = avg.index
avg.wavg = avg.wavg.round(decimals=1)
avg = avg.sort_values(by="wavg", ascending=False)

st.markdown("Za spodnjo vizualizacijo smo prešteli zastopane države pri odgovorih in nato za vsako "+\
           "izračunali uteženo povprečje glede na pogostost posamičnega odgovora. " +\
            "V izračun smo zajeli le države, za katere je vzorec zajemal vsaj 15 odgovorov.")

values = {0: 0, 1: 5, 2: 20, 3: 40, 4: 75, 5: 150, 6: 220}
st.markdown("Možni odgovori (št. obiskov) so bili: "+" ".join([f"{key}; " for i, key in enumerate(value_map2.keys())]))
st.markdown("Za posamične odgovore smo uporabili sledeče srednje vrednosti: "+ " ".join([f"{v}; " for v in values.values()]))

# ===== FIGURE
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 3.5))

sns.barplot(avg, ax=ax, y="wavg", x="country", edgecolor="w", color=colors[0])

ax.set_title("Število obiskov glede na državo bivanja")
ax.set_xticks(ticks=ax.get_xticks(), labels=ax.get_xticklabels(), rotation=35, ha='right')
ax.set_ylabel("število obiskov\n(uteženo povprečje)")
ax.set_xlabel("država/regija")

for i, v in enumerate(avg.wavg.tolist()):
    ax.text(x=i, y=avg.wavg[i]-1.5, s=v, ha="center", color="w")

sns.despine()

st.pyplot(fig=fig)

# ===== GLEDE NA CAS BIVANJA V TUJINI
values = {0: 0, 1: 5, 2: 20, 3: 40, 4: 75, 5: 150, 6: 220}
tmp3 = get_weigths_values(df, iv="years_abroad", dv="n_incoming", dv_values=values)

avg = pd.DataFrame(tmp3.groupby("years_abroad").apply(weighted_average, "estimates", "weight"), columns=["wavg"])
avg["years_abroad"] = avg.index
avg.wavg = avg.wavg.round(decimals=1)
avg.head(5)

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 3.5))

sns.barplot(avg, ax=ax, y="wavg", x="years_abroad", edgecolor="w", color=colors[0])

ax.set_title("Število obiskov glede čas bivanja v tujini")
ax.set_xticks(ticks=ax.get_xticks(), labels=years_abroad_map.keys(), rotation=0, ha='center')
ax.set_ylabel("število obiskov\n(uteženo povprečje)")
ax.set_xlabel("čas bivanja v tujini")

for i, v in enumerate(avg.wavg.tolist()):
    ax.text(x=i, y=avg.wavg[i]-2, s=v, ha="center", color="w", fontsize=14)

sns.despine()
st.pyplot(fig=fig)

# ==== ŠTEVILO OBISKOV GLEDE NA ČLANSTVO
values = {0: 0, 1: 5, 2: 20, 3: 40, 4: 75, 5: 150, 6: 220}
tmp4 = get_weigths_values(df, iv="ismember", dv="n_incoming", dv_values=values)
avg = pd.DataFrame(tmp4.groupby("ismember").apply(weighted_average, "estimates", "weight"), columns=["wavg"])
avg["ismember"] = avg.index
avg.wavg = avg.wavg.round(decimals=1)

# ===== FIGURE
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(2, 3.5))

sns.barplot(avg, ax=ax, y="wavg", x="ismember", edgecolor="w", color=colors[0])

ax.set_title("Število obiskov glede na članstvo")
ax.set_xticks(ticks=ax.get_xticks(), labels=ax.get_xticklabels(), rotation=25, ha='right')
ax.set_ylabel("število obiskov\n(uteženo povprečje)")
ax.set_xlabel("članstvo")

for i, v in enumerate(avg.wavg.tolist()):
    ax.text(x=i, y=avg.wavg[i]-1.5, s=v, ha="center", color="w", fontsize=14)

sns.despine()
st.pyplot(fig=fig)

# ===== NE GLEDE NA ČLANSTVO ===== #

values = {0: 0, 1: 5, 2: 20, 3: 40, 4: 75, 5: 150, 6: 220}
tmp6 = df.groupby(["n_incoming"], as_index=False).size()
tmp6["total"] = tmp6["size"].sum()
tmp6["weight"] = round(tmp6["size"]/tmp6.total, 3)
tmp6["estimates"] = tmp6.n_incoming.replace(values.keys(), values.values())
n_rec_total = round((tmp6["weight"]*tmp6.estimates).sum()/tmp6.weight.sum(), 0)

st.markdown(f"Skupno uteženo povprečje za število obiskov (neglede na članstvo) znaša **{int(n_rec_total)}** ljudi.")

st.markdown("## Število obiskov na enega VTISovca")

values = {0: 0, 1: 5, 2: 20, 3: 40, 4: 75, 5: 150, 6: 220}
count = df.n_incoming.replace(values.keys(), values.values()).to_numpy()
count_vtis = count[(df.ismember == "Član/-ica").to_numpy()]

n_vtis = (df.ismember == "Član/-ica").sum()

n_final = sum(count_vtis)/n_vtis

st.markdown(f"V raziskavi je sodelovalo N = {n_vtis} članov društva VTIS. " +
            f"Skupno je na podlagi njihovih priporočil Slovenijo obiskalo {sum(count_vtis)} ljudi. " +
            f"Na enega vtisovca Slovenijo torej po naši oceni obišče približno **{int(round(n_final, 0))}** ljudi. " + 
            f"Če upoštevamo **vse udeležence raziskave**, tudi nečlane, je zaradi enega Slovenca/ke v tujini Slovenijo obiskalo **{int(round(sum(count)/len(df), 0))}** ljudi. " )

values = {0: 0, 1: 5, 2: 20, 3: 40, 4: 75, 5: 150, 6: 220}
st.markdown("(Opomba: Možni odgovori (št. obiskov) so bili podani v sledečih intervalih: "+" ".join([f"{key}; " for i, key in enumerate(value_map2.keys())]) +
            " Da bi ocenili število obiskov za posameznega udeleženca, smo predpostavljali sledeče srednje vrednosti: "+ " ".join([f"{v}; " for v in values.values()]) + ")")

# ===== ŠTEVILO PRIPOROČIL ===== #

st.markdown("## Število priporočil (član vs. nečlan)")

values = {0: 0, 1: 2.5, 2: 10, 3: 22.5, 4: 40}
tmp5 = get_weigths_values(df, iv="ismember", dv="n_rec", dv_values=values)

avg = pd.DataFrame(tmp5.groupby("ismember").apply(weighted_average, "estimates", "weight"), columns=["wavg"])
avg["ismember"] = avg.index
avg.wavg = avg.wavg.round(decimals=1)
avg.head(5)
tmp5
# ==== FIGURE ===== #

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(2, 3.5))

sns.barplot(avg, ax=ax, y="wavg", x="ismember", edgecolor="w", color=colors[0])

ax.set_title("Število priporočil glede na članstvo")
ax.set_xticks(ticks=ax.get_xticks(), labels=ax.get_xticklabels(), rotation=25, ha='right')
ax.set_ylabel("ševilo priporočil\n(uteženo povprečje)")
ax.set_xlabel("članstvo")

for i, v in enumerate(avg.wavg.tolist()):
    ax.text(x=i, y=avg.wavg[i]-1, s=v, ha="center", color="w", fontsize=14)

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
