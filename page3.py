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
df=pd.read_excel('data\dataset.xlsx')

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
app=dash.Dash(external_stylesheets=[dbc.themes.CYBORG],meta_tags=[{'name': 'viewport',
'content': 'width=device-width, initial-scale=1.0'}],suppress_callback_exceptions=True)
server=app.server
app.layout=dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H6('MONTHLY CLINICS PERFORMANCE DASHBOARD',className='text-center mb4')
            ,width=12)
    ]),
    dbc.Row(
        html.Marquee("Monthly Hospital Performance Dashboard-Designed by-Mohammed Bahageel-Data Analyst-the Information displayed is stricly confidential"),
        style = {'color':'cyan'}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src='https://media0.giphy.com/media/hvDtUqsPbB2GNjhIdN/giphy.gif?cid=5e2148863a8ad0973c5d9deaa92353c6bbd932544462c74e&rid=giphy.gif&ct=g',top=True,bottom=False),
                dbc.CardBody([
                    html.H4('Abha Private Hospital',className='card-title'),
                    html.P('Choose The Clinc & the Revenue category:',className='card-text'),
                    dcc.Dropdown(id='selection_clinic',
                                 multi=False,
                                 options=[{'label':x,'value':x} for x in df['clinic'].unique()],
                                 value='الطوارئ',
                                 clearable=False ,style={'color': '#000000'}),
                    dcc.Dropdown(id='selection_doctor',
                                 multi=False,
                                 options=[],
                                 value='د. عبدالله كمال النابلسي' ,# I want to make this default value whenever I switched between clinics It yields the first doctor name dynamically and doesnot render empty charts ,
                                 clearable=False ,style={'color': '#000000'}),
                    dcc.Dropdown(id='selection_op',
                                 multi=False,
                                 options=[{'label':x,'value':x} for x in df['revenue_category'].unique()],
                                 value='CONSULTATION ',
                                 clearable=False ,style={'color': '#000000'})
                ]),
            ])
        ],width=1,xs=12, sm=12, md=12, lg=5, xl=2),dbc.Col([
            html.Div(id='revenues_doctor')
        ],width=3,xs=12, sm=12, md=12, lg=6, xl=6),
        dbc.Col([html.Div(id='outpatvsinpts_doctor')],width=3,xs=12, sm=12, md=12, lg=6, xl=4),
   
        
        
    ]),
    html.Br(),
    dbc.Row([dbc.Col([html.Div(id='patientss_doctor')],width=6,xs=12, sm=12, md=12, lg=6, xl=6),
             dbc.Col([html.Div(id='cash_credits_doctor')],width=6,xs=12, sm=12, md=12, lg=6, xl=6)])
],fluid=True)
#the callback functions--------------------------------3 inputs and 4 outputs ------------------------------------------------
@app.callback(
        Output('selection_doctor','options'),
        Input('selection_clinic','value')
)
def set_doctors_options(chosen_clinic):
    df23=df[(df['year']==2023)&(df['clinic']==chosen_clinic)]
    return [{'label':x,'value':x} for x in df23['doctor']]
# set the availabe options ---------------------------------------------------------------------------------------------------------------------------------------
# @app.callback(
#         Output('selection_doctor','value'),
#         Input('selection_doctor','options')
# )
# def set_doctors_values(available_options):
#     return [x['value'] for x in available_options]

@app.callback(
    Output('revenues_doctor','children'),
    Output('outpatvsinpts_doctor','children'),
    Output('patientss_doctor','children'),
    Output('cash_credits_doctor','children'),
    Input('selection_op','value'),
    Input('selection_clinic','value'),
    Input('selection_doctor','value'),
)
def update_graph(selected_category,selected_clinic,selected_doctor):
    if len(selected_doctor)==0:
        return dash.no_update
    else:
        df22=df[(df['year']==2022)&(df['revenue_category']==selected_category)&(df['clinic']==selected_clinic)&(df['doctor']==selected_doctor)]
        df23=df[(df['year']==2023)&(df['revenue_category']==selected_category)&(df['clinic']==selected_clinic)&(df['doctor']==selected_doctor)]
        dfgroupeddoctor22=df22.groupby(['Date','Month'])['total_revenues'].sum().reset_index('Date').sort_values('Date')
        dfgroupeddoctor23=df23.groupby(['Date','Month'])['total_revenues'].sum().reset_index('Date').sort_values('Date')
        dfgroupeddoctor23['changes']=round(dfgroupeddoctor23['total_revenues']/dfgroupeddoctor22['total_revenues']-1,2)*100
        # plot the first chart-----------------------------------------------------------------------------------------------------------------------------
        color4=np.where(dfgroupeddoctor23['changes']>0,'green','red')
        fig=make_subplots(rows=2,cols=1,shared_xaxes=True,shared_yaxes=False ,vertical_spacing=0.02,
        row_heights=[0.7,0.2] )
        fig.layout.template="plotly_dark"
        fig.add_trace(go.Scatter(x=dfgroupeddoctor22.index,y=dfgroupeddoctor22['total_revenues'],
                    line=dict(color='#00FFFF'),line_shape='spline',
                    name="Revenues in 2022"),
                    row=1,col=1,secondary_y=False)
        fig.add_trace(go.Scatter(x=dfgroupeddoctor23.index,y=dfgroupeddoctor23['total_revenues'],
                                line=dict(color='#66FF33'),line_shape='spline',
                name="Revenues in 2023"),row=1,col=1,secondary_y=False)
        fig.add_trace(go.Bar( x=dfgroupeddoctor23.index,y=dfgroupeddoctor23['changes'],marker_color=color4,name='change%')
                    ,row=2,col=1,secondary_y=False)

        fig.update_layout(title=f' Total Revenues --{selected_doctor}',xaxis=dict(showgrid=False),yaxis=dict(showgrid=False),

            hovermode='x unified', plot_bgcolor='#000000',paper_bgcolor='#000000' ,showlegend=True,
            legend=dict(orientation='h',yanchor='bottom',y=1.02, xanchor='right',x=1))
        fig.update_traces(xaxis='x2' )
        # plot the patients chart-----------------------------------------------------------------------------------------------------------------------------------------
        dfgroupeddocp22=df22.groupby(['Date','Month'])['patients'].sum().reset_index('Date').sort_values('Date')
        dfgroupeddocp23=df23.groupby(['Date','Month'])['patients'].sum().reset_index('Date').sort_values('Date')
        dfgroupeddocp23['changes_patients']=round(dfgroupeddocp23['patients']/dfgroupeddocp22['patients']-1,2)*100
        color5=np.where(dfgroupeddocp23['changes_patients']>0,'green','red')
        fig1=make_subplots(rows=2,cols=1,shared_xaxes=True,shared_yaxes=False ,vertical_spacing=0.02,
        row_heights=[0.7,0.2] )
        fig1.layout.template="plotly_dark"
        fig1.add_trace(go.Scatter(x=dfgroupeddocp22.index,y=dfgroupeddocp22['patients'],
                    line=dict(color='#00FFFF'),line_shape='spline',
                    name="Revenues in 2022"),
                    row=1,col=1,secondary_y=False)
        fig1.add_trace(go.Scatter(x=dfgroupeddocp23.index,y=dfgroupeddocp23['patients'],
                                line=dict(color='#66FF33'),line_shape='spline',
                name="Revenues in 2023"),row=1,col=1,secondary_y=False)
        fig1.add_trace(go.Bar( x=dfgroupeddocp23.index,y=dfgroupeddocp23['changes_patients'],
                            marker_color=color5,name='change%')
                    ,row=2,col=1,secondary_y=False)

        fig1.update_layout(title=f'Total Patients --{selected_doctor}',xaxis=dict(showgrid=False),yaxis=dict(showgrid=False),

            hovermode='x unified', plot_bgcolor='#000000',paper_bgcolor='#000000' ,showlegend=True,
            legend=dict(orientation='h',yanchor='bottom',y=1.02, xanchor='right',x=1))
        fig1.update_traces(xaxis='x2' )
        #plot the cash and credit chart
        dfgrougedcashdoc22=df22.groupby(['Month','Date'])['cash'].sum().reset_index('Date').sort_values('Date')
        dfgrougedcrdoc22=df22.groupby(['Month','Date'])['credit'].sum().reset_index('Date').sort_values('Date')
        dfgrougedcashdoc23=df23.groupby(['Month','Date'])['cash'].sum().reset_index('Date').sort_values('Date')
        dfgrougedcrdoc23=df23.groupby(['Month','Date'])['credit'].sum().reset_index('Date').sort_values('Date')
        fig2=go.Figure()
        fig2.add_scatter(name='Total Monthly cash of 2022',x=dfgrougedcashdoc22.index,y=dfgrougedcashdoc22['cash']  ,
                        line=dict(color='#66FF33'))
        fig2.add_scatter(name='Total Monthly credit  of 2022',x=dfgrougedcrdoc22.index,y=dfgrougedcrdoc22['credit'] ,
                        line=dict(color='#e10600'))
        fig2.add_scatter(name='Total Monthly cash of 2023',x=dfgrougedcashdoc23.index,y=dfgrougedcashdoc23['cash']  ,
                        line=dict(color='#66FF33',dash='dash'))
        fig2.add_scatter(name='Total Monthly credit of 2023',x=dfgrougedcrdoc23.index,y=dfgrougedcrdoc23['credit']  ,
                        line=dict(color='#e10600',dash='dash'))
        fig2.update_layout(title=f'Credit and Cash portions of on Monthly Basis--{selected_doctor}',
                        xaxis=dict(showgrid=True),yaxis=dict(showgrid=True),hovermode='x unified',paper_bgcolor='#000000',
                        plot_bgcolor='#000000' ,legend=dict(yanchor='bottom',y=1.02,xanchor='right',x=1,orientation='h')) 
        fig2.layout.template='plotly_dark'
        fig2.update_traces(mode="lines",hoverinfo='all')
        # Outpatients compared with inpatients --------------------------------------------------------------------------
        df23inpat=df[(df['year']==2023)&(df['revenue_category']=='INPATIENTS ')&(df['clinic']==selected_clinic)&(df['doctor']==selected_doctor)]
        df23total=df[(df['year']==2023)&(df['revenue_category']=='TOTAL REVENUES ')&(df['clinic']==selected_clinic)&(df['doctor']==selected_doctor)]
        dfInpatients=df23inpat.groupby(['Month','Date'])['patients'].sum().reset_index('Date').sort_values('Date')
        dfTotal_outpatients=df23total.groupby(['Month','Date'])['patients'].sum().reset_index('Date').sort_values('Date')
        dfconversion=round(dfInpatients['patients']/dfTotal_outpatients['patients'] ,3)*100
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
        fig3.update_layout(title=f'Outpatients Vs Inpatients and Conversion Rates in 2023----{selected_doctor}',
                        xaxis=dict(showgrid=False),yaxis=dict(showgrid=False),
                        hovermode='x unified', plot_bgcolor='#000000',paper_bgcolor='#000000' ,
                        showlegend=True,legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1))
        fig3.update_traces(xaxis='x2')
        return dcc.Graph(figure=fig),dcc.Graph(figure=fig3),dcc.Graph(figure=fig1),dcc.Graph(figure=fig2)


if __name__ == "__main__":
    app.run_server(debug=True,port=8000)
     




