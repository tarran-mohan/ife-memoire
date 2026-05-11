import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

path1 = r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\qgis\quartier 1 - angles.gpkg"
path2 = r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\qgis\quartier 2 - angles.gpkg"
path3 = r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\q3_angles.gpkg"
path4 = r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\q4_angles.gpkg"

def makePlot(path, title:str):
    df = gpd.read_file(path)
    fig, axs = plt.subplots(1, 1)
    axs.hist(df["internal_angle"], bins=12)
    plt.savefig(r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\Mémoire\images/" + title, bbox_inches="tight")
    plt.show()

    return df["internal_angle"].std()

makePlot(path3, "q3_angle_hist")

#---------------------------------------------------------------

path1 = r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\q1_dispo_stats_pp.gpkg"
path2 = r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\q2_dispo_stats_pp.gpkg"
path3 = r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\q3_dispo_stats_pp.gpkg"
path4 = r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\q4_dispo_stats_pp.gpkg"

def corr_plt(path, title):
    df1 = gpd.read_file(path)

    x = df1["disponibilité"]

    y = df1["mediane_ressentie"]
        
    model = LinearRegression()
    model.fit(np.array(x).reshape((-1, 1)), y)
    r2 = model.score(np.array(x).reshape((-1, 1)), y)

    a, b = np.polyfit(x, y, 1)
    gamme=range(min(x), max(x))
    plt.scatter(x, y)
    plt.plot(gamme, a*gamme + b)
    plt.xlabel("Disponibilité", size="xx-large")
    plt.ylabel("Mediane ressentie", size="xx-large")

    plt.savefig(r"C:\Users\green\OneDrive\Documents\2023-2027\Spring 2026\Stage\Mémoire\images/" + title, bbox_inches="tight")

    plt.show()
    return r2

corr_plt(path4, "dispo_plot_q4")

x=[18.20, 15.22, 13.33]
y=[2.6, 2.78, 2.90]
model = LinearRegression()
model.fit(np.array(x).reshape((-1, 1)), y)
model.score(np.array(x).reshape((-1, 1)), y)
a, b = np.polyfit(x, y, 1)
gamme=range(int(min(x)), int(max(x))+2)
plt.scatter(x, y)
plt.plot(gamme, a*gamme + b)
plt.show()
