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
import plotly.graph_objects as go
import numpy as np
io.renderers.default='browser'

class CareerGraph:
    def __init__(self):
        self.all_time_stats = pd.read_csv('output/all_time_stats.csv')
        self.all_time_stats['TB'] = (self.all_time_stats['1B'] + (self.all_time_stats['2B']*2) + (self.all_time_stats['3B']*3) + (self.all_time_stats['HR']*4))

        self.all_time_stats = self.all_time_stats.fillna(0)

    def get_bar_graph(self, stat):
        self.all_time_stats = self.all_time_stats.sort_values(by=stat, ascending=True)
        return px.bar(self.all_time_stats, 
                      x=stat, 
                      y='Player', 
                      opacity=.8, 
                      orientation='h',
                      title=f'Wombats {stat} – Career Totals')
#TODO read csv and show in var explorer


    def get_grouped_bar_graph(self, stats):
        self.all_time_stats = self.all_time_stats.sort_values(by=stats[2], ascending=False)
        return px.bar(self.all_time_stats, x='Player', y=stats, text_auto=".3f",barmode="group",title=f'Career Totals - {stats}')


class SeasonGraph:
    def __init__(self, year: str):
        cumulative_file_path = f'output/{year}/raw_cumulative.csv'
        non_cumulative_file_path = f'output/{year}/raw_non_cumulative.csv'
        self.cumul = pd.read_csv(cumulative_file_path)
        self.non_cumul = pd.read_csv(non_cumulative_file_path)
        
        # create TB var (total bases) #
        self.cumul['TB'] = (self.cumul['1B'] + (self.cumul['2B']*2) + (self.cumul['3B']*3) + (self.cumul['HR']*4))
        self.non_cumul['TB'] = (self.non_cumul['1B'] + (self.non_cumul['2B']*2) + (self.non_cumul['3B']*3) + (self.non_cumul['HR']*4))
        self.non_cumul['OPSPTR'] = (self.non_cumul['OBP']+self.non_cumul['SLG']) / self.non_cumul['TeamRuns']
        
        # missing data #
        self.cumul = self.cumul.fillna(0)
        self.non_cumul = self.non_cumul.fillna(0)

        # define dataframe: most recent game of season only #
        last_game = self.cumul['Game'].max()
        self.cumul_last = self.cumul.drop(self.cumul[self.cumul['Game']!=last_game].index)
        self.cumul_last = self.cumul_last.drop(self.cumul_last[self.cumul_last['GP']==0].index)

        # create OPS var #
        self.cumul_last["OPS"] = self.cumul_last['OBP'] + self.cumul_last['SLG']


# clustered bar: avg, obp, slg #
    def get_bar_clustered(self, year: str):
        self.cumul_last = self.cumul_last.sort_values(by="Player", ascending=True)
        return px.bar(self.cumul_last,
                          x="Player",
                          y=["AVG", "OBP", "SLG"],
                          text_auto=".3f", 
                          title=f'Wombats Key Stats by Player – {year} Season',
                          opacity=.8).update_layout(yaxis_title="Key Stats",
                          legend_title_text="Stat",
                          hoverlabel=dict(bgcolor="aliceblue"),
                          barmode='group')

# stacked ops : on base and slg #
    def get_stacked_ops(self, year: str):
        self.cumul_last = self.cumul_last.sort_values(by="OPS", ascending=False)
        return px.bar(self.cumul_last,
                          x="Player",
                          y=["OBP", "SLG"],
                          text_auto=".3f", opacity=.8,
                          hover_data={'Player':False,'variable':False,'value':False,'OPS':':.3f'},
                          title=f'Wombats OPS by Player – {year} Season').update_layout(yaxis_title="OPS",
                          legend_title_text="OPS Stat", 
                          hoverlabel=dict(bgcolor="aliceblue"))

    def get_line_cumulative_player_avg(self, year: str):
        return px.line(self.cumul, 
                       x='Game', 
                       y='AVG', 
                       color='Player', 
                       title=f'Wombats Cumulative Batting Average by Game – {year} Season').update_xaxes(dtick=1)
                # TODO fix decimals

    def get_histogram_season_avg(self, year: str):
        histogram = px.histogram(self.cumul_last, x='AVG', nbins=7, title=f'Wombats Batting Average Distribution – {year} Season', opacity=.8)
        histogram.update_layout(xaxis_title='AVG', yaxis_title='Frequency (Players)', bargap=0.01)
        return histogram


# cumulative flow #
    def get_areachart_season(self, year: str):
        return px.area(self.cumul, x='Game', 
                                  y='AVG', 
                                  color = 'Player', 
                                  title=f'Wombats Stacked Batting Average by Player – {year} Season').update_xaxes(dtick=1)

# bar #
    def get_bar_bases_player_season(self, year: str):
        self.cumul_last = self.cumul_last.sort_values(by="TB", ascending=False)
        return px.bar(self.cumul_last, x='Player',
                      y='TB',
                      opacity=.8,
                      title=f'Wombats Total Bases by Player – {year} Season')
    # TODO fix slg pct decimals
    # TODO overlay slg pct
    # TODO horizontal

def showfig():
    # clustered bar – season #
    instanceseason_clustered = SeasonGraph('2023')
    clustered = instanceseason_clustered.get_bar_clustered('2023')
    clustered.show()
    io.write_html(clustered, file='get_bar_clustered.html')

    # stacked - season- #
    instanceseason_stacked = SeasonGraph('2023')
    stackedbar = instanceseason_stacked.get_stacked_ops('2023') # self is implicit
    stackedbar.show()
    io.write_html(stackedbar, file='get_stackedbar_season.html')

    # bar - season #
    instanceseason_bar = SeasonGraph('2023')
    bargraphseason = instanceseason_bar.get_bar_bases_player_season('2023')
    bargraphseason.show()
    io.write_html(bargraphseason, file='get_bar_season.html')

    # histogram - season #
    instanceseason_histogram = SeasonGraph('2023')
    histogram = instanceseason_histogram.get_histogram_season_avg('2023')
    histogram.show()
    io.write_html(histogram, file='get_histogram_season.html')

    # line -season #
    instanceseason_line = SeasonGraph('2023')
    line = instanceseason_line.get_line_cumulative_player_avg('2023') 
    line.show()
    io.write_html(line, file='get_line_career.html')
    
    # area -season#
    instanceseason_area = SeasonGraph('2023')
    areachart = instanceseason_area.get_areachart_season('2023')
    areachart.show()
    io.write_html(areachart, file='get_areachart_season.html')

    # bar graph - career #
    instanceofcareergraph = CareerGraph()
    bargraphcareer = instanceofcareergraph.get_bar_graph("TB")
    bargraphcareer.show()
    io.write_html(bargraphcareer, file='get_bar_career.html')

if __name__ == "__main__":
    print(__name__)
    showfig()


############################
