#!/bin/env python3

import argparse
import os
from numpy.core.fromnumeric import var
import requests
import pandas
import matplotlib.pyplot as plt
import numpy as np
from math import pi

CSV_URI = 'https://srv-store2.gofile.io/download/9V3H6X/league_stats.zip'
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
    T = len(percentages)
    labels = variables
    blueTeam = percentages[0]
    redTeam = percentages[1]
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, blueTeam, width, color='b', label=teams[0])
    rects2 = ax.bar(x + width/2, redTeam, width, color='r', label=teams[1])
    ax.set_ylabel('Percentage')
    ax.set_title('Percentage of win compared to some stats')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    fig.set_size_inches(18.5, 10.5)
    plt.savefig(OUTPUT_PATH)


if args.gen_datas:
    print('Downloading datasets ...')
    r = requests.get(CSV_URI)
    if r.status_code == 200:
        if os.path.exists(CSV_DIR) == False:
            os.mkdir(CSV_DIR)
        path = os.path.join(CSV_DIR, ZIP_FILENAME)
        open(path, 'wb').write(r.content)
        print('Unzipping ...')
        os.system(f'unzip {path} -d {CSV_DIR}')
        os.remove(path)
        print('Done')
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

print('Reordering stats ...')
stats = get_raw_stats(teams, variables, csv)
print('Analyzing percentages ...')
perc = get_percentages(stats)

ploters = {
    PLOT_TYPES[0]: plot_radar,
    PLOT_TYPES[1]: plot_bars
}
print('Plotting ...')
ploters[args.ploting](perc, variables, teams)
print('Done')
