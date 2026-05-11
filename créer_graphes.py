# tous les bibliothèques préalables 
import geopandas as gpd
import matplotlib.pyplot as plt
import hypernetx as hnx
import networkx as nx
import shapely
import numpy as np

# des polylignes issus du dossier GeoPackage, trouver tous les bouts 
def get_endpoints(df):
    endpoints = []

    for i in range(0, len(df["geometry"])):
        start = df["geometry"][i:(i+1)].boundary[i].geoms[0]
        end = df["geometry"][i:(i+1)].boundary[i].geoms[-1]
        endpoints += [start, end]

    endpoints = list(set(endpoints))

    return endpoints

# trouver les point d'intersection et les ajouter au list des bouts
def get_intersections_endpoints(df):
    intersections = []

    rows = list(range(0, (df.shape[0])))

    checked = []

    for i in rows:
        rows.pop(i)
        for j in rows:
            curr_inds = set([i, j])
            if curr_inds in checked:
                continue
            checked.append(curr_inds)

        rows = list(range(0, (df.shape[0])))

    inds_list = []

    for inds in checked:
        inds_list.append(list(inds))

    for inds in inds_list:
        i, j = inds
        inter = df["geometry"][i].intersection(df["geometry"][j])
        if str(inter) == 'LINESTRING EMPTY':
            continue
        else:
            intersections.append(inter)

    intersections += get_endpoints(df)

    intersections = list(set(intersections))
    
    ints = gpd.GeoDataFrame({'geometry':intersections})

    return ints

# créer la matrice d'indicence selon une dictionnaire des incidences
def linegraph_incidence(incidences):
    cols = incidences.keys()
    edges = max(cols)
    vertices = 0

    for vertex_label in incidences.values():
        curr_max = max(vertex_label)
        if curr_max > vertices:
            vertices = curr_max
    vertices+=1

    im = np.zeros(shape=(vertices, edges))
    for col in cols:
        rows = incidences[col]
        col-=1
        for row in rows:
            im[row, col] = 1

    im = im.transpose()

    col_sums = np.sum(im, axis=0)
    to_drop = []

    for i in range(len(col_sums)):
        if col_sums[i]==1.: to_drop.append(i)

    im = np.delete(im, np.s_[to_drop], axis=1)
    return im

# mettre une matrice dans le coin gauche en haut d'une matrice d'une dimension souhaitée  
def inj(incidence_matrix, desired_dims):
    curr_dims = incidence_matrix.shape
    x_diff = desired_dims[0] - curr_dims[0]
    y_diff = desired_dims[1] - curr_dims[1]

    injected = np.pad(incidence_matrix, ((0,x_diff),(0,y_diff)), 'constant', constant_values=0)

    return injected

path = r"voiture_voies.gpkg" # fichier GeoPackage pour le réseau le plus petit. On suppose 
                             # ici  qu'il s'agit du réseau voiture. La géometrie doit être étiquété par voie et agrégé selon les étiquétes 

df = gpd.read_file(path)

shapely.to_wkt(df["geometry"]) # assurer que la géometrie est en format WKT (Well-Known Text)

ints = get_intersections_endpoints(df) # trouver les points de carrefour et les bouts

incidences = {n:[] for n in df["hyperedge_id"]} # initialiser la dictionnaire des incidences

# étiquéter les sommets 
vertex_labels = {i:ints["geometry"][i] for i in range(0, len(ints["geometry"]))} 

# s'il y a une voie qui touche un point, ajouter à la dictionnaire des incidences
for i in ints["geometry"]:
    for j in range(0, len(df["geometry"])):
        he_geometry = df["geometry"][j]
        hyperedge_id = df["hyperedge_id"][j]
        if shapely.distance(i,he_geometry) < 1e-8: # (ce n'est pas toujours exacte, donc on vérifie en réalite que c'est dans une petite zone tampon autour le voie)
            corr_vertices = [key for key,val in vertex_labels.items() if val==i]
            incidences[hyperedge_id] = incidences[hyperedge_id] + corr_vertices

incidences

#----------------------------------------------------

# répéter le processus, mais utiliser la même dictionnaire pour les sommets et ajouter les nouveaux voies

path = r"velo_voies.gpkg"

df1 = gpd.read_file(path)

shapely.to_wkt(df1["geometry"])

ints1 = get_intersections_endpoints(df1)

incidences1 = {n:[] for n in df1["hyperedge_id"]}

drop_inds = []

for i in range(len(ints)):
    for j in range(len(ints1)):
        if shapely.distance(ints["geometry"][i], ints1["geometry"][j]) < 1e-8:
            drop_inds.append(j)

new_ints = (ints1.drop(drop_inds)).reset_index().drop("index",axis=1) 

n = max(vertex_labels.keys())
new_vertices = {n+i:new_ints["geometry"][i-1] for i in range(1,len(new_ints)+1)}

vertex_labels = vertex_labels | new_vertices

for i in ints1["geometry"]:
    for j in range(0, len(df1["geometry"])):
        he_geometry = df1["geometry"][j]
        hyperedge_id = df1["hyperedge_id"][j]
        if shapely.distance(i,he_geometry) < 1e-8:
            corr_vertices = [key for key,val in vertex_labels.items() if val==i]
            incidences1[hyperedge_id] = incidences1[hyperedge_id] + corr_vertices

incidences1

# --------------------------------------------

path = r"pieton_voies.gpkg"

df2 = gpd.read_file(path)

shapely.to_wkt(df2["geometry"])

ints2 = get_intersections_endpoints(df2)

incidences2 = {n:[] for n in df2["hyperedge_id"]}

drop_inds = []

for i in range(len(ints)):
    for j in range(len(ints2)):
        if shapely.distance(ints["geometry"][i], ints2["geometry"][j]) < 1e-8:
            drop_inds.append(j)

for i in range(len(ints1)):
    for j in range(len(ints2)):
        if shapely.distance(ints1["geometry"][i], ints2["geometry"][j]) < 1e-8:
            drop_inds.append(j)

new_ints = (ints2.drop(drop_inds)).reset_index().drop("index",axis=1) 

n = max(vertex_labels.keys())
new_vertices = {n+i:new_ints["geometry"][i-1] for i in range(1,len(new_ints)+1)}

vertex_labels = vertex_labels | new_vertices

for i in ints2["geometry"]:
    for j in range(0, len(df2["geometry"])):
        he_geometry = df2["geometry"][j]
        hyperedge_id = df2["hyperedge_id"][j]
        if shapely.distance(i,he_geometry) < 1e-8:
            corr_vertices = [key for key,val in vertex_labels.items() if val==i]
            incidences2[hyperedge_id] = incidences2[hyperedge_id] + corr_vertices

incidences2

im2 = linegraph_incidence(incidences2)
im1 = linegraph_incidence(incidences1)
im = linegraph_incidence(incidences)

summed = inj(im, im2.shape) + inj(im1, im2.shape) + im2

dispo_1 = np.sum(summed, axis=1)