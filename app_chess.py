# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 08:39:02 2022

@author: Henrique Barreiros
"""
import dash 
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import re


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP],meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])
app.title = "Chess Statistics"

df = pd.read_csv('games.csv')
country_df = pd.read_csv('country_df.csv')

color_1 = '#faf3f0'
color_2 = '#f0bdb3'
color_3 = '#f5e7e1'
text_color = '#0e0705'

min_white_rating = df['white_rating'].min()
max_white_rating = df['white_rating'].max()
min_black_rating = df['black_rating'].min()
max_black_rating = df['black_rating'].max()

def splitopening(x):
    df['opening_name'] = df['opening_name'].str.split(x).str[0]
    return df['opening_name']

def get_white_marks():
    marks = {}
    df_filtered = df.sort_values(by='white_rating',ignore_index=True)
    for i in range(len(df_filtered)):
        if(i%6000 == 1000):
            marks[str(df_filtered['white_rating'][i])] = str(df_filtered['white_rating'][i])
    return marks

def get_black_marks():
    marks = {}
    df_filtered = df.sort_values(by='black_rating',ignore_index=True)
    for i in range(len(df_filtered)):
        if(i%6000 == 1000):
            marks[str(df_filtered['black_rating'][i])] = str(df_filtered['black_rating'][i])
    return marks


def squares_dictionary_maker():
    dictionary = {}
    for i in range(8):
        for j in range(8):
            square = chr(97+i) + str(j+1)
            dictionary[square] = 0
            
    return dictionary

def captured_moves(column):
    captured_list = []
    for i in range(len(column)):
        moves_list = column[i].split()
        for i in range(len(moves_list)):
            pattern = re.compile(r'x')
            if pattern.findall(moves_list[i]):
                captured_list.append(moves_list[i])
    return pd.Series(captured_list)

# sq_dict = squares_dictionary_maker()

def board_heatmap(moves): #Fills the above created dictionary for 
    moves = moves.split(' ')
    moves = [move for move in moves if move.endswith('.') == False]
    for move in moves:
        if move.startswith('O-'):
            if move == 'O-O':
                index = moves.index(move)
                if index%2 == 0:
                    sq_dict['f1'] = sq_dict['f1'] + 1
                    sq_dict['g1'] = sq_dict['g1'] + 1
                else:
                    sq_dict['f8'] = sq_dict['f8'] + 1
                    sq_dict['g8'] = sq_dict['g8'] + 1
                moves[index] = ''
            elif move == 'O-O-O':
                index = moves.index(move)
                if index%2 == 0:
                    sq_dict['d1'] = sq_dict['d1'] + 1
                    sq_dict['c1'] = sq_dict['c1'] + 1
                else:
                    sq_dict['d8'] = sq_dict['d8'] + 1
                    sq_dict['c8'] = sq_dict['c8'] + 1
                moves[index] = ''
        elif move.endswith('+') or move.endswith('#'):
            if str(move[-3]) == '=':
                sq_dict[str(move[-5:-3])] = sq_dict[str(move[-5:-3])] + 1
            else:
                sq_dict[str(move[-3:-1])] = sq_dict[str(move[-3:-1])] + 1
        elif move.endswith('Q') or move.endswith('N') or move.endswith('B') or move.endswith('R'):
            sq_dict[str(move[-4:-2])] = sq_dict[str(move[-4:-2])]+1
        elif move == '':
            continue
        else:
            sq_dict[str(move[-2:])] = sq_dict[str(move[-2:])] + 1
    
    return True


def dict_formatter(sq_dict):  #Making a 2d-array from our dictionary
    square_values = np.array(list(sq_dict.values())) 
    square_values = square_values.reshape(8, 8)
    sq_T = square_values.T
    sq_T = np.flip(sq_T, 0)
    return sq_T



app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Label("Control Panel",className='display-5 mb-5 text-center'),
                                
                                dbc.Label('Select Time Increment:'),
                                dcc.Dropdown(df['increment_code'].unique(), [],multi=True, id='dropdown-increment',className='mb-5'),
                
                                  
                                
                                dbc.Label(id = "white-player-rating"),
                                dcc.RangeSlider(min_white_rating, max_white_rating, value=[min_white_rating, max_white_rating], marks=get_white_marks(), id='my-range-slider1',className='mb-5'),
                                dbc.Label(id='black-player-rating'),
                                dcc.RangeSlider(min_black_rating, max_black_rating, value=[min_black_rating, max_black_rating],marks=get_black_marks(), id='my-range-slider2'),
                
                                
                            ]
                        ),

                    ],style={"background-color":color_2},md=2
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                            html.H1(['Chess Statistics'],className='text-center display-3'),
                            html.Hr(style={'background-color':'rgb(61,61,61)'}),
                            ]
                        ),
                
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader('The Number of Turns Distribution',className='text-center fs-3',style={'background-color':color_2}),
                                        dbc.CardBody(id='turns_dist_graph',style={'background-color':color_3})
                                    ],className="shadow p-0 mb-3 bg-white rounded border-light"
                                )
        
                            ],md=6
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader('Victory Status',className='text-center fs-3',style={'background-color':color_2}),
                                        dbc.CardBody(id='victory_status_graph',style={'background-color':color_3})
                                    ],className="shadow p-0 mb-3 bg-white rounded border-light"
                                )
                            ],md=6
                        )
                        
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader('Opening Statistics',className='text-center fs-3',style={'background-color':color_2}),
                                        dbc.CardBody(id='opening_stats_graph',style={'background-color':color_3})
        
                                    ],className="shadow p-0 mb-3 bg-white rounded border-light"
                                )
                                
                            ],md=6
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader('Captured pieces',className='text-center fs-3',style={'background-color':color_2}),
                                        dbc.CardBody(id='pieces-captured-graph',style={'background-color':color_3})
        
                                    ],className="shadow p-0 mb-3 bg-white rounded border-light"
                                )
                                
                            ],md=6
                        )
                    ]
                ),
                        dbc.Row(
                            [html.Div([
                                html.H4("Top Chess Players by Nationality (FIDE)", style={'text-align': 'center'}),
                                dcc.Slider(2000, 2015, 1, value=2000, id="slct_year",
                                           marks={
                                               int(h): {'label': int(h),
                                                        'style': {'color': '#000000'}} for h in range(2000, 2016)
                                           }
                                           ),

                                html.Div(id='output_container', children=[]),
                                html.Br(),
                                dcc.Graph(id='nationality_map', figure={}, style={'background-color': color_3}),
                            ])])
                    ],style={'background-color':color_1},md=10
                )
            ]
        )
    ],fluid=True
)

@callback(
    [Output('white-player-rating','children'),Output('black-player-rating','children')],
    [Input('my-range-slider1','value'),Input('my-range-slider2','value')]
)

def update_label(white_value,black_value):
    return ["Range Selected for White Player Rating: "+str(white_value[0])+" - "+str(white_value[1]), "Range Selected for Black Player Rating: "+str(black_value[0])+" - "+str(black_value[1]) ]


@callback(
        [Output(component_id='output_container', component_property='children'),
         Output(component_id='nationality_map', component_property='figure')],
        [Input(component_id='slct_year', component_property='value')]
)

def update_map(option_slctd):
    container = "The year chosen by user was: {}".format(option_slctd)
    dff = country_df.copy()
    dff = dff[dff["year"] == option_slctd]
    fig = px.choropleth(dff, locations="country",
                            color="Country Count",
                            hover_name="country",
                            animation_frame="year", animation_group="country",
                            color_continuous_scale='temps',
                             width=1500,
                             height=600)
    fig.update_layout(xaxis=dict(),paper_bgcolor=color_3, plot_bgcolor=color_3, dragmode=False, font=dict(size=16, color='black'))
    return container,fig


@callback(
    [Output('turns_dist_graph','children'),Output('victory_status_graph','children'),Output('opening_stats_graph','children'),Output('pieces-captured-graph','children')],
    [Input('my-range-slider1','value'),Input('my-range-slider2','value'),Input('dropdown-increment','value')]
)

def update_graph(white_slider,black_slider,increment_value):
    fig1 = go.Figure()
    fig2 = go.Figure()
    fig3 = go.Figure()
    fig4 = go.Figure()

    white_min = white_slider[0]
    white_max = white_slider[1]
    black_min = black_slider[0]
    black_max = black_slider[1]

    splitopening(':')
    splitopening('|')
    splitopening('Game')
    splitopening('#')
    splitopening('Opening')

    df_filtered = df[(df['white_rating'] >= white_min) & (df['white_rating'] <= white_max) & (df['black_rating'] >= black_min) & (df['black_rating'] <= black_max)]



    frames = []
    if increment_value:
        for increments in increment_value:
            frames.append(df_filtered[df_filtered['increment_code'] == increments])
            df_final = pd.concat(frames,axis=0)
            df_final.reset_index(inplace=True,drop=True)
    else:
        df_final = df_filtered

    ############### HISTOGRAM ##################

    fig1.add_trace(go.Histogram(
                         x=df_final['turns'],
                         #name=sentiment,
                         #orientation='h',
                         marker=dict(color="rgb(99, 110, 250)")
                         )
                )
    fig1.update_layout(xaxis=dict(title='Number of Turns'),font_color=text_color,font_size=14,paper_bgcolor=color_3,plot_bgcolor=color_3,margin=dict(t=0))
    fig1.update_xaxes(showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)
    fig1.update_yaxes(showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)

    ############## VICTORY STATUS BAR GRAPH ##################

    for status in df_final['victory_status'].unique():
        df_filtered_victory = df_final[df_final['victory_status'] == status]

        df_filtered_victory = df_filtered_victory.groupby(by='winner').count().sort_values(by='id',ascending=False)
        fig2.add_trace(go.Bar(
            x=df_filtered_victory.index,
            y=df_filtered_victory.id,
            name= status
        ))

    fig2.update_layout(xaxis=dict(title='Winners'),barmode='group',font_color=text_color,font_size=14,paper_bgcolor=color_3,plot_bgcolor=color_3,margin=dict(t=0))
    fig2.update_xaxes(showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)
    fig2.update_yaxes(showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)


    ################ OPENING NAME BAR GRAPH ##################

    
    df_final['opening_name'] = df_final['opening_name'].str.strip()

    df_opening = df_final.groupby(by='opening_name').count().sort_values(by='id',ascending=False)

    fig3.add_trace(go.Bar(
                      x=df_opening.index[:20],
                      y=df_opening['id'][:20]
    ))
    fig3.update_layout(xaxis=dict(title='Opening Name'),font_color=text_color,font_size=14,paper_bgcolor=color_3,plot_bgcolor=color_3,margin=dict(t=0))
    fig3.update_xaxes(tickangle = 45,showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)
    fig3.update_yaxes(showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)

    ################# Heatmap ###################

    global sq_dict 
    sq_dict = squares_dictionary_maker()

    len(np.vectorize(board_heatmap)(captured_moves(df_final['moves'])))


    heatmap_frame = pd.DataFrame(dict_formatter(sq_dict))
    heatmap_frame.index = ['1', '2', '3', '4', '5', '6', '7', '8']
    heatmap_frame.columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    
    fig4.add_trace(go.Heatmap(
                        z=heatmap_frame,
                        y=heatmap_frame.index,
                        x=heatmap_frame.columns,
                        colorscale = 'Viridis'))
    fig4.update_traces(hovertemplate="%{x}%{y}: %{z}<extra></extra>",colorbar_exponentformat="none", selector=dict(type='heatmap'))
    fig4.update_layout(font_color=text_color,font_size=14,paper_bgcolor=color_3,plot_bgcolor=color_3,margin=dict(t=0,b=0))
    

    return [dcc.Graph(figure=fig1),dcc.Graph(figure=fig2),dcc.Graph(figure=fig3),dcc.Graph(figure=fig4)]



if __name__ == "__main__":
    app.run_server(debug=False)
