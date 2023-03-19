

import pandas as pd
import numpy as np
import dash
from dash import html
from dash import dcc
import plotly.graph_objects as go
from dash.dependencies import Input ,Output
import dash_bootstrap_components as dbc
import plotly_express as px
from plotly.subplots import make_subplots
from dash import dcc, html, callback, Output
from pathlib import Path
#load the data--------------------------------------------------------------------------------------
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("./data").resolve()
df= pd.read_excel(DATA_PATH.joinpath("dataset.xlsx") )
#df=pd.read_excel('data\dataset.xlsx')

#------General Hospital Report ------------------------------------------------------------
#convert the date to datetime format-----------------------------------------------------------------------
df['Date']=pd.to_datetime(df['Date'])
#extract the month
df['Month']=df['Date'].dt.month_name()
df['year']=df['Date'].dt.year
#-----------------------------remove the white spaces
df.columns=df.columns.str.replace(" ","")
df=df.rename(columns={'CLINIC':'clinic','DOCTOR':'doctor','REVENUESCATEGORY':'revenue_category','CASH':'cash','CREDIT':'credit',
'TOTALREVENUES':'total_revenues','PATIENTS':'patients'})
# Outpatients compared with inpatients --------------------------------------------------------------------------
df23inpat=df[(df['year']==2023)&(df['revenue_category']=='INPATIENTS ')]
df23total=df[(df['year']==2023)&(df['revenue_category']=='TOTAL REVENUES ')]
dfInpatients=df23inpat.groupby(['Month','Date'])['patients'].sum().reset_index('Date').sort_values('Date')
dfTotal_outpatients=df23total.groupby(['Month','Date'])['patients'].sum().reset_index('Date').sort_values('Date')
dfconversion=round(dfInpatients['patients']/dfTotal_outpatients['patients'] ,3)*100
#plot the Graph---------------------------------------------------------------------------
fig3=make_subplots(rows=2,cols=1,shared_xaxes=True,shared_yaxes=False ,vertical_spacing=0.02,
                   row_heights=[0.7,0.2] )

fig3.layout.template="plotly_dark"

fig3.add_trace(go.Bar(x=dfTotal_outpatients.index,y=dfTotal_outpatients['patients'],marker_color='cyan',
               name="Total Outpatients in 2023"),
                row=1,col=1,secondary_y=False)
fig3.add_trace(go.Bar(x=dfInpatients.index,y=dfInpatients['patients'],marker_color='red',
                name="Inpatients in 2023"),row=1,col=1,secondary_y=False)
fig3.add_trace(go.Scatter(x=dfTotal_outpatients.index,y=dfconversion,
               line=dict(color='#66FF33') ,
                name="Conversion Rate"),
                row=2,col=1,secondary_y=False)
fig3.update_layout(title='Outpatients Vs Inpatients and Conversion Rates in 2023',
                    xaxis=dict(showgrid=False),yaxis=dict(showgrid=False), 
                 hovermode='x unified', plot_bgcolor='#000000',paper_bgcolor='#000000' ,
                 showlegend=True,legend=dict(orientation='h',
                    yanchor='bottom',y=1.02,xanchor='right',x=1))
fig3.update_traces(xaxis='x2')
#set the application layout-------------------------------------------------------------------------------------------------------------------
app=dash.Dash(external_stylesheets=[dbc.themes.CYBORG],meta_tags=[{'name': 'viewport',
'content': 'width=device-width, initial-scale=1.0'}],suppress_callback_exceptions=True)
server=app.server
app.layout=dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H2('MONTHLY HOSPITAL PERFORMANCE DASHBOARD',className='text-center mb4')
            ,width=12)
    ]),
    dbc.Row(
        html.Marquee("Monthly Hospital Performance Dashboard-Designed by-Mohammed Bahageel-Data Analyst-the Information displayed is stricly confidential"),
        style = {'color':'cyan'}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src='https://media1.giphy.com/media/MgFP7hqxNoDhRCv6Sd/giphy.gif?cid=5e214886366cfe5b9c075895b1569635b4327781c1b7320b&rid=giphy.gif&ct=g',top=True,bottom=False),
                dbc.CardBody([
                    html.H4('Abha Private Hospital',className='card-title'),
                    html.P('Choose The revenue Category:',className='card-text'),
                    dcc.Dropdown(id='selection_op',
                                 multi=False,
                                 options=[{'label':x,'value':x} for x in df['revenue_category'].unique()],
                                 value='CONSULTATION ',
                                 clearable=False ,style={'color': '#000000'})
                ]),
            ])
        ],width=1,xs=12, sm=12, md=12, lg=5, xl=2),dbc.Col([
            html.Div(id='revenue')
        ],width=3,xs=12, sm=12, md=12, lg=6, xl=6),
        dbc.Col([dcc.Graph(id='outpatvsinpt',figure=fig3)],width=3,xs=12, sm=12, md=12, lg=6, xl=4),
    #    dbc.Row([ dbc.Col([
    #         html.Div(id='revenue')
    #     ],width=3,xs=12, sm=12, md=12, lg=6, xl=6),
    #     dbc.Col([dcc.Graph(id='outpatvsinpt',figure=fig3)],width=3,xs=12, sm=12, md=12, lg=6, xl=6)
    #     ]),
        
        
    ]),
    html.Br(),
    dbc.Row([dbc.Col([html.Div(id='patients')],width=6,xs=12, sm=12, md=12, lg=6, xl=6),dbc.Col([html.Div(id='cash_credit')],width=6,xs=12, sm=12, md=12, lg=6, xl=6)])
],fluid=True)
#----------the Callbacks-------------------------------------------------------------------------------------------------------------------------

@app.callback(

    Output('revenue','children'),
    Output('patients','children'),
    Output('cash_credit','children'),
    Input('selection_op','value')

)

def update_graph(selected_category):
    df22=df[(df['year']==2022)&(df['revenue_category']==selected_category)]
    df22.columns=df22.columns.str.replace("  ","")
    df23=df[(df['year']==2023)&(df['revenue_category']==selected_category)]
    dfgrouged22=df22.groupby(['Month','Date'])['total_revenues'].sum().reset_index('Date')
    dfgrouged23=df23.groupby(['Month','Date'])['total_revenues'].sum().reset_index('Date')
    dfgrouged22=dfgrouged22.sort_values('Date')
    dfgrouged23=dfgrouged23.sort_values('Date')
    dfgrouged23['changes']=round(dfgrouged23['total_revenues']/dfgrouged22['total_revenues']-1,2)*100
    color=np.where(dfgrouged23['changes']>0,'green','red')
    fig=make_subplots(rows=2,cols=1,shared_xaxes=True,shared_yaxes=False ,vertical_spacing=0.02,
    row_heights=[0.7,0.2] )
    fig.layout.template="plotly_dark"
    fig.add_trace(go.Scatter(x=dfgrouged22.index,y=dfgrouged22['total_revenues'],
                line=dict(color='#00FFFF'),line_shape='spline',
                name="Revenues in 2022"),
                row=1,col=1,secondary_y=False)
    fig.add_trace(go.Scatter(x=dfgrouged23.index,y=dfgrouged23['total_revenues'],line=dict(color='#66FF33'),line_shape='spline',
               name="Revenues in 2023"),row=1,col=1,secondary_y=False)
    fig.add_trace(go.Bar( x=dfgrouged23.index,y=dfgrouged23['changes'],marker_color=color,name='change%')
                ,row=2,col=1,secondary_y=False)

    fig.update_layout(title=f'Total Hospital Monthly Revenues of {selected_category} ',xaxis=dict(showgrid=False),yaxis=dict(showgrid=False),

        hovermode='x unified', plot_bgcolor='#000000',paper_bgcolor='#000000' ,showlegend=True,legend=dict(orientation='h',yanchor='bottom',y=1.02, xanchor='right',x=1))
    fig.update_traces(xaxis='x2' )
    #the second graph------------------------------------------------------------------------------------------------
    dfgrougedp22=df22.groupby(['Month','Date'])['patients'].sum().reset_index('Date')
    dfgrougedp23=df23.groupby(['Month','Date'])['patients'].sum().reset_index('Date')
    dfgrougedp22=dfgrougedp22.sort_values('Date')
    dfgrougedp23=dfgrougedp23.sort_values('Date')
    dfgrougedp23['changes_patients']=round(dfgrougedp23['patients']/dfgrougedp22['patients']-1,2)*100
    color1=np.where(dfgrougedp23['changes_patients']>0,'green','red')
    fig1=make_subplots(rows=2,cols=1,shared_xaxes=True,shared_yaxes=False ,vertical_spacing=0.02,
    row_heights=[0.7,0.2] )
    fig1.layout.template="plotly_dark"
    fig1.add_trace(go.Scatter(x=dfgrougedp22.index,y=dfgrougedp22['patients'],
    line=dict(color='#00FFFF'),line_shape='spline',
    name="Patients in 2022"),
    row=1,col=1,secondary_y=False)
    fig1.add_trace(go.Scatter(x=dfgrougedp23.index,y=dfgrougedp23['patients'],
    line=dict(color='#66FF33'),line_shape='spline',
    name="patients in 2023"),row=1,col=1,secondary_y=False)
    fig1.add_trace(go.Bar( x=dfgrougedp23.index,y=dfgrougedp23['changes_patients'],
    marker_color=color1,name='change%'),row=2,col=1,secondary_y=False)
    fig1.update_layout(title=f'Total  Monthly Patients in {selected_category} ',xaxis=dict(showgrid=False),yaxis=dict(showgrid=False),
    hovermode='x unified', plot_bgcolor='#000000',paper_bgcolor='#000000' ,showlegend=True,legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1))
    fig1.update_traces(xaxis='x2' )
    #the thrid graph-----------------------------------------------------------------------------------------------------------------
    dfgrougedcash22=df22.groupby(['Month','Date'])['cash'].sum().reset_index('Date').sort_values('Date')
    dfgrougedcr22=df22.groupby(['Month','Date'])['credit'].sum().reset_index('Date').sort_values('Date')
    dfgrougedcash23=df23.groupby(['Month','Date'])['cash'].sum().reset_index('Date').sort_values('Date')
    dfgrougedcr23=df23.groupby(['Month','Date'])['credit'].sum().reset_index('Date').sort_values('Date')
    fig2=go.Figure()
    fig2.add_scatter(name='Total Monthly cash in  2022',x=dfgrougedcash22.index,y=dfgrougedcash22['cash']  ,line=dict(color='#66FF33'))
    fig2.add_scatter(name='Total Monthly credit  in 2022',x=dfgrougedcr22.index,y=dfgrougedcr22['credit'] ,line=dict(color='#e10600'))
    fig2.add_scatter(name='Total Monthly cash in 2023',x=dfgrougedcash23.index,y=dfgrougedcash23['cash']  ,line=dict(color='#66FF33',dash='dash'))
    fig2.add_scatter(name='Total Monthly credit of 2023',x=dfgrougedcr23.index,y=dfgrougedcr23['credit']  ,line=dict(color='#e10600',dash='dash'))
    fig2.update_layout(title=f'Credit and Cash portions of {selected_category} on Monthly Basis',xaxis=dict(showgrid=True),yaxis=dict(showgrid=True),hovermode='x unified',paper_bgcolor='#000000',
                    plot_bgcolor='#000000' ,legend=dict(yanchor='bottom',y=1.02,xanchor='right',x=1,orientation='h')) 
    fig2.layout.template='plotly_dark'
    fig2.update_traces(mode="lines", hoverinfo='all')
    return dcc.Graph(figure=fig) ,dcc.Graph(figure=fig1),dcc.Graph(figure=fig2)





        

if __name__ == "__main__":
    app.run_server(debug=True,port=8000)
