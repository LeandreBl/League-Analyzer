#!/bin/env python3

import argparse
import os
from numpy.core.fromnumeric import var
import requests
import pandas
import matplotlib.pyplot as plt
import numpy as np
from math import pi

CSV_URI = 'https://storage.googleapis.com/kaggle-data-sets/610763/1096497/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20210114%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210114T154656Z&X-Goog-Expires=259199&X-Goog-SignedHeaders=host&X-Goog-Signature=6949899d99717328c6298f9fdb3241114c6f0fd683c40946c1d0a2cfedb9518bc203d5ae621e43546c247a4c50e42f51a20720f96979a44759cd59fc68256e50240310e22893d28bebe4af1e3588b83f324c19a01cb1a62fa97172ef3a0cff2944356f9f2058066a9df7cb7719219bdb6abfed94cec78a4e7e9a8d31df2eaa68730f7a60d656fa618dd71f734d1be4c9e21cac67f14c11b0dca1188645f9e2272edd08029f0278becf1b6b1918618b3fd887f8ced9ed900be51d5995f6d49c30ae4fddf03473f84e226c7d98a622c8f21e466d90df9d974de2129ad24e6d631a8df567d14eee17f5e7238d9d5d36d9dc2629a70902fcd74a31cb7d099842b427'
ZIP_FILENAME = 'league_stats.zip'
CSV_DIR = 'datas'
PLOT_TYPES = ['radar', 'bar']
parser = argparse.ArgumentParser()

parser.add_argument(
    '--gen-datas', help='Regenerate the .csv file from internet', action='store_true')
parser.add_argument(
    '--input', help='.csv input file (in datas directory)', type=str, default=os.path.join(CSV_DIR, 'Challenger_Ranked_Games.csv')
)
parser.add_argument(
    '--output', help='PNG output file', type=str, default=None)
parser.add_argument(
    '--ploting', help='The ploting aspect', type=str, default="radar", choices=PLOT_TYPES)

args = parser.parse_args()

OUTPUT_PATH = f'{args.input}_stats.png' if args.input == None else args.input if args.input.endswith(
    '.png') else f'{args.input}.png'
INPUT_CSV = args.input


def get_raw_stats(teams, variables, csv):
    V = len(variables)
    T = len(teams)
    stats = [None] * T
    for t in range(T):
        stats[t] = [None] * V
        for v in range(V):
            stats[t][v] = []
        for i in range(len(csv[teams[t]])):
            for v in range(V):
                if csv[variables[v]][i] != 0:
                    stats[t][v].append(csv[teams[t]][i])
    return stats


def get_percentages(stats):
    T = len(stats)
    V = len(stats[0])
    perc = np.empty([T, V])
    for v in range(V):
        for t in range(T):
            perc[t][v] = sum(stats[t][v]) / len(stats[t][v])
    return perc


def plot_radar(percentages, variables, teams):
    T = len(percentages)
    V = len(percentages[0])
    angles = [v / float(V) * 2 *
              pi for v in range(V)]
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles, variables)
    ax.set_rlabel_position(0)
    plt.yticks([0, 1], ["Lose", "Win"], color="grey", size=10)
    plt.ylim(0, 1)
    for t in range(T):
        ax.plot(angles, percentages[t], linewidth=1, linestyle='solid',
                label=teams[t].replace('Wins', ''))
        ax.fill(angles, percentages[t], teams[t][0], alpha=0.1)
        for ai, per in zip(angles, percentages[t]):
            ax.text(round(ai + 0.05, 1), round(per - 0.03, 1), round(per, 2), color='green',
                    ha='center', va='center')

    plt.legend(loc='best')
    plt.savefig(OUTPUT_PATH)


def plot_bars(percentages, variables, teams):
    pass


if args.gen_datas:
    r = requests.get(CSV_URI)
    if r.status_code == 200:
        if os.path.exists(CSV_DIR) == False:
            os.mkdir(CSV_DIR)
        path = os.path.join(CSV_DIR, ZIP_FILENAME)
        open(path, 'wb').write(r.content)
        os.system(f'unzip {path} -d {CSV_DIR}')
        os.remove(path)
    else:
        print("Failed to retrieve data")
        exit(1)

try:
    csv = pandas.read_csv(INPUT_CSV)
except:
    print(f'"{INPUT_CSV}" is not a valid CSV file')
    exit(1)

csv = csv.drop(columns=['gameId', 'gameDuraton'])

teams = []
variables = []

for label in csv.columns:
    if label.endswith('Wins'):
        teams.append(label)
    elif 'First' in label:
        variables.append(label)

stats = get_raw_stats(teams, variables, csv)
perc = get_percentages(stats)

ploters = {
    PLOT_TYPES[0]: plot_radar,
    PLOT_TYPES[1]: plot_bars
}

ploters[args.ploting](perc, variables, teams)
