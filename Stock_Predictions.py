from tvDatafeed import TvDatafeed, Interval
import plotly.graph_objects as go
from plotly.subplots import make_subplots 
import streamlit as st
import pandas as pd
from pandas.tseries.offsets import BDay
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
import ssl
from urllib import request
#python -m streamlit run app.py
def Hisse_Temel_Veriler():
    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"
    context = ssl._create_unverified_context()
    response = request.urlopen(url1, context=context)
    url1 = response.read()

    df1 = pd.read_html(url1,decimal=',', thousands='.')                         #Tüm Hisselerin Tablolarını Aktar
    df1=df1[2]                                                                  #Tüm Hisselerin Özet Tablosu
    return df1

st.set_page_config(
    page_title="Hisse Temel Analiz",
    layout="wide",
    initial_sidebar_state="expanded")

with st.sidebar:
    Hisse_Temel=Hisse_Temel_Veriler()
    st.header('Hisse Arama')
    dropdown1 = st.selectbox('Hisse Adı',Hisse_Temel['Kod'])
    dropdown2 = st.slider('Data Sayısı', 0, 5000, 100, 100)
    dropdown3 = st.slider('Periyot', 0, 100, 30, 5)

tv = TvDatafeed()
data = tv.get_hist(symbol=dropdown1,exchange='BIST',interval=Interval.in_daily,n_bars=dropdown2)

st.header(dropdown1)
fig= go.Figure()
fig.add_trace(go.Scatter(x=data.index,y=data["close"],name="Hisse Fiyatı"))

st.plotly_chart(fig)
df_train=pd.DataFrame({"ds":data.index.values,"y":data['close'].values})

m=Prophet()
m.fit(df_train)
future=m.make_future_dataframe(periods=dropdown3,freq="D")
isBusinessDay = BDay().is_on_offset
match = pd.to_datetime(future['ds']).map(isBusinessDay)
future=future[match]
forecast=m.predict(future)

st.write("Forecast Data")
st.write(forecast.tail(dropdown3))
st.write("Forecast Plot")
fig1=plot_plotly(m,forecast)
st.plotly_chart(fig1)

st.write("Forecast Components")
fig2=plot_components_plotly(m, forecast)
st.write(fig2)

