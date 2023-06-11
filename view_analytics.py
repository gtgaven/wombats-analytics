# -*- coding: utf-8 -*-
"""
Author: Kathy Sanchez
Institution: Jar Department
Date Created: Tue Jun 6 2023
Purpose: Wombats 2023 analytics
"""
############################# Notes

# clear console shortcut     ctrl + L

############################# Initial operations

# install and import packages #

# Terminal #
#    conda install -c condya-forge plotnine 
#    conda install plotnine 
#    Then I set my path manually with the PYTHONPATH manager.

import pandas as pd # data manipulation
import plotly.express as px
import plotly.io as io
io.renderers.default='browser'

class CareerGraph:
    def __init__(self):
        self.all_time_stats = pd.read_csv('output/all_time_stats.csv')
        self.all_time_stats['TB'] = (self.all_time_stats['1B'] + (self.all_time_stats['2B']*2) + (self.all_time_stats['3B']*3) + (self.all_time_stats['HR']*4))

        self.all_time_stats = self.all_time_stats.fillna(0)

    def get_bar_graph(self, stat):
        self.all_time_stats = self.all_time_stats.sort_values(by=stat, ascending=False)
        return px.bar(self.all_time_stats, x='Player', y=stat, title=f'Career Totals - {stat}')

    def get_grouped_bar_graph(self, stats):
        self.all_time_stats = self.all_time_stats.sort_values(by=stats[2], ascending=False)
        return px.bar(self.all_time_stats, x='Player', y=stats, text_auto=".3f",barmode="group",title=f'Career Totals - {stats}')


class SeasonGraph:
    def __init__(self, year: str):
        cumulative_file_path = f'output/{year}/raw_cumulative.csv'
        non_cumulative_file_path = f'output/{year}/raw_non_cumulative.csv'
        self.cumul = pd.read_csv(cumulative_file_path)
        self.non_cumu = pd.read_csv(non_cumulative_file_path)
        
        # create col:    TB = total bases #
        self.cumul['TB'] = (self.cumul['1B'] + (self.cumul['2B']*2) + (self.cumul['3B']*3) + (self.cumul['HR']*4))
        
        # missing data #
        self.cumul = self.cumul.fillna(0)

        # define dataframe: most recent game of season only #
        last_game = self.cumul['Game'].max()
        self.cumul_last = self.cumul.drop(self.cumul[self.cumul['Game']!=last_game].index)
        self.cumul_last = self.cumul_last.drop(self.cumul_last[self.cumul_last['GP']==0].index)

    def get_line_cumulative_player_avg(self):
        return px.line(self.cumul, 
                       x='Game', 
                       y='AVG', 
                       color='Player', 
                       title="Cumulative Batting Average by Game")
                # TODO fix decimals

    def get_histogram_season_avg(self):
        histogram = px.histogram(self.cumul_last, x='AVG', nbins=7, title='Wombats Season AVG')
        histogram.update_layout(xaxis_title='AVG', yaxis_title='Frequency (Players)', bargap=0.01)
        return histogram

    def get_bar_bases_player_season(self):
        self.cumul_last = self.cumul_last.sort_values(by="TB", ascending=False)
        return px.bar(self.cumul_last, x='Player',
                      y='Bases',
                      opacity=.7,
                      title="Total Season Bases by Player") 
    # TODO fix slg pct decimals
    # TODO overlay slg pct

def showfig():
    instanceofseasongraph = SeasonGraph('2023')
    histogram = instanceofseasongraph.get_histogram_season_avg() # self is imlicit
    histogram.show()
    
    # bar graph #
    instanceofcareergraph = CareerGraph()
    bargraph = instanceofcareergraph.get_bar_graph("AVG")
    bargraph.show()



if __name__ == "__main__":
    print(__name__)
    showfig()


############################
