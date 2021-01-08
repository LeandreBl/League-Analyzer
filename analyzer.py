#!/bin/env python3

import argparse
import os
from numpy.core.fromnumeric import var
import requests
import pandas
import matplotlib.pyplot as plt
import numpy as np
from math import pi

CSV_URI = 'https://storage.googleapis.com/kaggle-data-sets/610763/1096497/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T121116Z&X-Goog-Expires=259199&X-Goog-SignedHeaders=host&X-Goog-Signature=1a266b31f31754512c0d0db65e1efbce309c92e5bca6fcb04c4e259a41a0e3d636dbb9a832d727caf02baefdf854dfb9b8076131e300e2f9c30c168f0faae3a86715a7353813384a21c6076dee0305255d0754934269c10450b770f232f483bb125d1e57cfcf0148b95cd470fbb13b669c2477d245f0110a2d732fa07022734c326645fcf5458785f00767c2114f3339891f9ef3fe47858fbf68b8f4153ce6403eb8127abbb5a5d4535d68cea230a4aef81c92fbd20442517524bd8b48ce55d061461f99adf37f3009ca14301e6ba71d5a0f9b6ff3bed0e999a4903b38daa3c2cc29ccc9ab4e72347ad16768c747e50397916b58f8820f100f48bb0715dd3e03'
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
