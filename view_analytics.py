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
    def __init__(self, file_path):
        self.all_time_stats = pd.read_csv(file_path)
        self.all_time_stats['TB'] = (self.all_time_stats['1B'] + (self.all_time_stats['2B']*2) + (self.all_time_stats['3B']*3) + (self.all_time_stats['HR']*4))

        self.all_time_stats = self.all_time_stats.fillna(0)

    def get_bar_graph(self, stat: str):
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
        return px.histogram(self.cumul_last, x='AVG', nbins=7, title='Wombats Season AVG').update_layout(xaxis_title='AVG', yaxis_title='Frequency (Players)', bargap=0.01)
    # You may want to adjust the drops by season depending on the distribution of games played.

    def get_bar_bases_player_season(self):
        self.cumul_last = self.cumul_last.sort_values(by="TB", ascending=False)
        return px.bar(self.cumul_last, x='Player',
                      y='Bases',
                      opacity=.7,
                      title="Total Season Bases by Player") 
    # TODO fix slg pct decimals
    # TODO overlay slg pct

def main():
    cg = CareerGraph('output/raw_all_time_stats.csv')
    cg.get_grouped_bar_graph(['AVG', 'OBP', 'SLG']).show()
    

    #gc = SeasonGraph('2022')
    #graph =  gc.get_histogram_season_avg()
    #graph.show()
    #plot = ggplot_wrapper_2022.get_bar_bases_season_player()
    #print(plot)
    
#    GraphCreator.get_bar_bases_player_season('testingexport.html')


if __name__ == "__main__":
    main()


############################
