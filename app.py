try:
    from functools import lru_cache
except ImportError:
    # Python 2 does stdlib does not have lru_cache so let's just
    # create a dummy decorator to avoid crashing
    print ("WARNING: Cache for this example is available on Python 3 only.")
    def lru_cache():
        def dec(f):
            def _(*args, **kws):
                return f(*args, **kws)
            return _
        return dec



from __future__ import print_function
import flask
#from flask import Flask, render_template, request, redirect


#import flask

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
import pandas as pd

from os.path import dirname, join
from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, Select


app = flask.Flask(__name__)

colors = {
    'Black': '#000000',
    'Red':   '#FF0000',
    'Green': '#00FF00',
    'Blue':  '#0000FF',
}

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

DATA_DIR = join(dirname(__file__), 'daily')

DEFAULT_TICKERS = ['AAPL', 'GOOG', 'INTC', 'BRCM', 'YHOO']

def nix(val, lst):
    return [x for x in lst if x != val]

@lru_cache()
def load_ticker(ticker):
    fname = join(DATA_DIR, 'table_%s.csv' % ticker.lower())
    data = pd.read_csv(fname, header=None, parse_dates=['date'],
                       names=['date', 'foo', 'o', 'h', 'l', 'c', 'v'])
    data = data.set_index('date')
    return pd.DataFrame({ticker: data.c, ticker+'_returns': data.c.diff()})

@lru_cache()
def get_data(t1, t2):
    df1 = load_ticker(t1)
    df2 = load_ticker(t2)
    data = pd.concat([df1, df2], axis=1)
    data = data.dropna()
    data['t1'] = data[t1]
    data['t2'] = data[t2]
    data['t1_returns'] = data[t1+'_returns']
    data['t2_returns'] = data[t2+'_returns']
    return data

# set up widgets

stats = PreText(text='', width=500)
ticker1 = Select(value='AAPL', options=nix('GOOG', DEFAULT_TICKERS))
ticker2 = Select(value='GOOG', options=nix('AAPL', DEFAULT_TICKERS))

# set up plots

source = ColumnDataSource(data=dict(date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))
source_static = ColumnDataSource(data=dict(date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))
tools = 'pan,wheel_zoom,xbox_select,reset'
#@app.route('/')
#def index():
#  return render_template('index.html')

@app.route('/')
def index():
    """ Very simple embedding of a polynomial chart
    """

    # Grab the inputs arguments from the URL
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    color = getitem(args, 'color', 'Black')
    #_from = int(getitem(args, '_from', 0))
    #to = int(getitem(args, 'to', 10))

    # Create a polynomial line graph with those arguments
    aapl = pd.read_csv('./data/WIKI-AAPL.csv',  parse_dates = ["Date"])

    
    #x = list(range(_from, to + 1))
    fig = figure(title="AAPL data", x_axis_type = "datetime")
    fig.line(aapl['Date'], aapl['Close'], color=colors[color], line_width=2)

    resources = INLINE.render()

    script, div = components(fig)
    html = flask.render_template(
        'embed.html',
        plot_script=script,
        plot_div=div,
        resources=resources,
        color=color
        #_from=_from,
        #to=to
    )
    
    return html



if __name__ == '__main__':
    print(__doc__)
    app.run(port=33507)

