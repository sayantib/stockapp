#imports
from datetime import datetime as dt
from datetime import timedelta
import requests
import pandas as pd
from pandas import DataFrame, to_datetime
import urllib
import json
from bokeh.plotting import figure, output_file, show
from bokeh import embed
import os

from flask import Flask, render_template, request, redirect

#############################################################################

def get_quandlurl(apikey, company, timeperiod):
    end_date = dt.now().strftime('%Y-%m-%d')
    start_date = (dt.now() - timedelta(days=timeperiod)).strftime('%Y-%m-%d')
    url = 'https://www.quandl.com/api/v3/datasets/WIKI/'+company+'.json?start_date='+start_date+'&end_date='+end_date+'&order=asc&api_key='+apikey
    return url

###########################################################################

def load_df(url):
    r = requests.get(url)

    if r.status_code == 200:
        data = urllib.urlopen(url).read()
        try: js = json.loads(str(data))
        except: js = None
        column_names = js["dataset"]['column_names']
        print column_names
        stock_data = js["dataset"]['data']
        stock_info = pd.DataFrame(stock_data, columns=column_names)
        return stock_info
    else:
        print "Invalid ticker! Please enter a valid ticker symbol. "
        return None

#################################################################################

#Make a Bokeh plot of the data
def makeBokehPlot(df, checked_requests, ticker_symbol):
    df = df.set_index(['Date'])
    df.index = to_datetime(df.index)
    plot = figure(x_axis_type="datetime", width=700, height=500)
    color = ['blue', 'red', 'green', 'orange']
    legend_names = {}

    for req in checked_requests:
        if req == 'Close':
            legend_names[req] = 'Closing price'
        if req == 'Open':
            legend_names[req] = 'Opening price'
        if req == 'High':
            legend_names[req] = 'Highest price'
        if req == 'Low':
            legend_names[req] = 'Lowest price'

    for item in range(len(checked_requests)):
        plot.line(df.index, df[checked_requests[item]], legend=legend_names[checked_requests[item]], color=color[item])

    plot.title = "Data from Quandle WIKI set"
    plot.title.text_font_size = "20pt"
    plot.title.align = "center"
    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = 'Price'
    plot.yaxis.axis_label_text_font_style = "normal"
    plot.xaxis.axis_label_text_font_style = "normal"

    plot.legend.border_line_width = 3
    plot.legend.border_line_color = "navy"
    plot.legend.border_line_alpha = 0.5

    return plot

##########################################################################

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/userinput')


@app.route('/userinput', methods=['GET' ,'POST'])
def userinput():
  return render_template('userinput.html')


@app.route('/Bokeh_plot',methods=['GET','POST'])
def bokehplot():
    company = request.form['ticker_symbol'].upper()
    checked_requests = request.form.getlist('options')
    api_key = 'htG3jdEXoyPPedJW9pUG'
    timeperiod = 30

    url = get_quandlurl(api_key, company, timeperiod)
    r = requests.get(url)
    df = load_df(url)

    if r.status_code != 200:
        return render_template('err.html')
    elif len(checked_requests) < 1:
        msg = "No features checked! Please check desired features."
        return render_template('userinput.html', msg=msg)
    else:
        plot = makeBokehPlot(df, checked_requests, company)
        script, div = embed.components(plot)
        return render_template('stockplot.html', script=script, div=div, company=company)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port)
    if port==5000:
        app.run(port=port,host='0.0.0.0')
    else:
	app.run(port=port)





