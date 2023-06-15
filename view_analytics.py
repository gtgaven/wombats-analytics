# -*- coding: utf-8 -*-
"""
Author: Kathy Sanchez
Institution: Jar Department
Date Created: Tue Jun 6 2023
Purpose: Wombats 2023 analytics
"""
import numpy as np
import pandas as pd 

import plotly.express as px
import plotly.io as io
from typing import List
io.renderers.default='browser'
io.templates.default = "seaborn"

class CareerGraph:
    def __init__(self):
        self.all_time_stats = pd.read_csv('output/raw_all_time_stats.csv')
        self.all_time_stats["TB"] = (self.all_time_stats['1B'] + (self.all_time_stats['2B']*2) + (self.all_time_stats['3B']*3) + (self.all_time_stats['HR']*4))
        self.all_time_stats["OPS"] = self.all_time_stats['OBP'] + self.all_time_stats['SLG']
        self.all_time_stats = self.all_time_stats.fillna(0)

    def get_bar_graph_int(self, stat):
        self.all_time_stats = self.all_time_stats.sort_values(by=stat, ascending=True)
        return px.bar(self.all_time_stats, 
                          x=stat,
                          y="Player",
                          title=f'Wombats {stat} - Career Totals',
                          text_auto=".0f",
                          orientation='h', 
                          opacity=.8).update_layout(xaxis_title=f'{stat}',
                          hoverlabel=dict(bgcolor="aliceblue"),
                          barmode='group')

    def get_bar_graph_pct(self, stat):
        self.all_time_stats = self.all_time_stats.sort_values(by=stat, ascending=True)
        return px.bar(self.all_time_stats, 
                          x=stat,
                          y="Player",
                          text_auto=".3f", 
                          title=f'Wombats {stat} - Career Totals',
                          orientation='h',
                          opacity=.8).update_layout(xaxis_title=f'{stat}',
                          hoverlabel=dict(bgcolor="aliceblue"),
                          barmode='group')

    def get_stacked_ops(self):
        self.all_time_stats = self.all_time_stats.sort_values(by="OPS", ascending=True)
        return px.bar(self.all_time_stats,
                          x=["OBP", "SLG"],
                          y="Player",
                          text_auto=".3f", opacity=.8,
                          orientation='h',
                          hover_data={'Player':False,'variable':False,'value':False,'OPS':':.3f'},
                          title='Wombats OPS - Career Totals').update_layout(xaxis_title="OPS",
                          legend_title_text="OPS Stat", 
                          hoverlabel=dict(bgcolor="aliceblue"))


class SeasonGraph:
    def __init__(self, year: str):
        cumulative_file_path = f'output/{year}/raw_cumulative.csv'
        non_cumulative_file_path = f'output/{year}/raw_non_cumulative.csv'
        self.year = year
        self.cumul = pd.read_csv(cumulative_file_path)
        self.non_cumul = pd.read_csv(non_cumulative_file_path)
        
        # create TB var (total bases) #
        self.cumul['TB'] = (self.cumul['1B'] + (self.cumul['2B']*2) + (self.cumul['3B']*3) + (self.cumul['HR']*4))
        self.non_cumul['TB'] = (self.non_cumul['1B'] + (self.non_cumul['2B']*2) + (self.non_cumul['3B']*3) + (self.non_cumul['HR']*4))
        
        # missing data #
        self.cumul = self.cumul.fillna(0)
        self.non_cumul = self.non_cumul.fillna(0)

        # define dataframe: most recent game of season only #
        last_game = self.cumul['Game'].max()
        self.cumul_last = self.cumul.drop(self.cumul[self.cumul['Game']!=last_game].index)

        # create OPS var #
        self.cumul_last["OPS"] = self.cumul_last['OBP'] + self.cumul_last['SLG']


    # clustered bar: avg, obp, slg #
    def get_bar_clustered(self):
        self.cumul_last = self.cumul_last.sort_values(by="Player", ascending=True)
        return px.bar(self.cumul_last,
                          x="Player",
                          y=["AVG", "OBP", "SLG"],
                          text_auto=".3f",
                          title=f'Wombats Key Stats by Player – {self.year} Season',
                          hover_data={'Player':True,'variable':False,'value':False},
                          opacity=.8).update_layout(yaxis_title="Key Stats",
                          legend_title_text="Stat", 
                          hoverlabel=dict(bgcolor="aliceblue"),
                          barmode='group')
# TODO tooltip

    # stacked ops : on base and slg #
    def get_stacked_ops(self):
        self.cumul_last = self.cumul_last.sort_values(by="OPS", ascending=False)
        return px.bar(self.cumul_last,
                          x="Player",
                          y=["OBP", "SLG"],
                          text_auto=".3f", opacity=.8,
                          hover_data={'Player':False,'variable':False,'value':False,'OPS':':.3f'},
                          title=f'Wombats OPS by Player – {self.year} Season').update_layout(yaxis_title="OPS",
                          legend_title_text="OPS Stat", 
                          hoverlabel=dict(bgcolor="aliceblue"))

    def get_line_cumulative_player_avg(self):
        return px.line(self.cumul, 
                       x='Game', 
                       y='AVG', 
                       color='Player', 
                       title=f'Wombats Cumulative Batting Average by Game – {self.year} Season').update_xaxes(dtick=1)
                # TODO fix decimals

    def get_histogram_season_avg(self):
        histogram = px.histogram(self.cumul_last, x='AVG', nbins=7, title=f'Wombats Batting Average Distribution – {self.year} Season', opacity=.8)
        histogram.update_layout(xaxis_title='AVG', yaxis_title='Frequency (Players)', bargap=0.01)
        return histogram


    # cumulative flow #
    def get_areachart_season(self, stat: str):
        return px.area(self.cumul, x='Game', 
                                  y=stat, 
                                  color = 'Player', 
                                  title=f'Wombats Stacked {stat} by Player – {self.year} Season').update_xaxes(dtick=1)
 # TODO sort areas and tooltips

    # bar #
    def get_bar_bases_player_season(self):
        self.cumul_last = self.cumul_last.sort_values(by="TB", ascending=False)
        return px.bar(self.cumul_last, x='Player',
                      y='TB',
                      opacity=.8,
                      title=f'Wombats Total Bases by Player – {self.year} Season')
    # TODO overlay slg pct
    # TODO horizontal

def export_all_graphs(seasons: List[str], output_dir: str):
    for year in seasons:
        # new instance of season graph for each year
        sg_instance = SeasonGraph(year)
        clustered = sg_instance.get_bar_clustered()
        io.write_html(clustered, file=f'{output_dir}/{year}/CHART_avg_obp_slg.html')

        stacked_ops = sg_instance.get_stacked_ops()
        io.write_html(stacked_ops, file=f'{output_dir}/{year}/CHART_ops.html')

        season_tb = sg_instance.get_bar_bases_player_season()
        io.write_html(season_tb, file=f'{output_dir}/{year}/CHART_tb.html')

    cs_instance = CareerGraph()
    clustered_graph = cs_instance.get_bar_graph_pct('AVG')
    io.write_html(clustered_graph, file=f'{output_dir}/career/CHART_avg.html')
    
    ops_graph = cs_instance.get_stacked_ops()
    io.write_html(ops_graph, file=f'{output_dir}/career/CHART_ops.html')

    career_tb = cs_instance.get_bar_graph_int('TB')
    io.write_html(career_tb, file=f'{output_dir}/career/CHART_tb.html')


def showfigs():
    cs_instance = CareerGraph()
    cs_instance.get_bar_graph_pct('AVG').show()
    cs_instance.get_stacked_ops().show()
    cs_instance.get_bar_graph_int('TB').show()
    
    sg_instance = SeasonGraph('2023')
    sg_instance.get_bar_clustered().show()
    sg_instance.get_stacked_ops().show()
    sg_instance.get_bar_bases_player_season().show()
    
if __name__ == "__main__":
    showfigs()


############################
