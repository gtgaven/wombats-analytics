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

class GraphCreator:

    def __init__(self, year: str):
        cumulative_file_path = f'output/{year}/raw_cumulative.csv'
        non_cumulative_file_path = f'output/{year}/raw_non_cumulative.csv'
        self.cumul = pd.read_csv(cumulative_file_path)
        self.non_cumu = pd.read_csv(non_cumulative_file_path)
        
        # create col:     hits = single + double + triple + home run #
        self.cumul['Hits'] = self.cumul['1B'] + self.cumul['2B'] + self.cumul['3B'] + self.cumul['HR']
        
        # create col:    at bats = plate appearance - sac flies - walks #
        self.cumul['At Bats'] = self.cumul['PA'] - self.cumul['SF'] - self.cumul['BB']
        
        # create col:    on base pctage = at bats + walk + sac flies #
        self.cumul['OBP'] = (self.cumul['Hits'] + self.cumul['BB']) / (self.cumul['At Bats'] + self.cumul['BB'] + self.cumul['SF'])
        
        # create col:    avg = hits / at bats # 
        self.cumul['AVG'] = self.cumul['Hits'] / self.cumul['At Bats']
        
        # create col:    slug = at bat + walk + sac flies #
        self.cumul['SLG'] = (self.cumul['1B'] + (self.cumul['2B']*2) + (self.cumul['3B']*3) + (self.cumul['HR']*4))/self.cumul['At Bats']
        
        # create col:    total bases #
        self.cumul['Bases'] = (self.cumul['1B'] + (self.cumul['2B']*2) + (self.cumul['3B']*3) + (self.cumul['HR']*4))
        
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
        self.cumul_last = self.cumul_last.sort_values(by="Bases", ascending=False)
        return px.bar(self.cumul_last, x='Player',
                      y='Bases',
                      opacity=.7,
                      title="Total Season Bases by Player") 
    # TODO fix slg pct decimals
    # TODO overlay slg pct

def main():
    gc = GraphCreator('2022')
    graph =  gc.get_bar_bases_player_season()
    graph.show()
    #plot = ggplot_wrapper_2022.get_bar_bases_season_player()
    #print(plot)
    
#    GraphCreator.get_bar_bases_player_season('testingexport.html')


if __name__ == "__main__":
    main()


############################
