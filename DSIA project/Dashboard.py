import base64
import streamlit as st
import plotly.express as px
import pandas as pd 
import os
import numpy as np
import warnings 
warnings.filterwarnings('ignore')
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pylab as plt
st.set_page_config(page_title='Dashboard!!!',page_icon=':bar_chart:',layout='wide')
st.title(" :bar_chart: Mutual_fund EDA ")
def set_page_bg(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url(data:image/jpg;base64,{encoded});
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# # Example usage:
set_page_bg('bg.jpg')

def sidebar_bg(side_bg):

   side_bg_ext = 'jpg'

   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
      }}
      </style>
      """,
      unsafe_allow_html=True,
      )
side_bg = 'bg.jpg'
sidebar_bg(side_bg)

df=pd.read_csv("mutual_funds_cleanup_dataset.csv")
col1,col2=st.columns(2)
Min_risk=df['risk_level'].min()
Max_risk=df["risk_level"].max()
with col1:
    Minrisk=st.number_input("select minimum risk",min_value=Min_risk,max_value=Max_risk)
with col2:
    Maxrisk=st.number_input("select Maximum risk ",min_value=Min_risk,max_value=Max_risk)
df=df[(df['risk_level'] >= Minrisk) & (df['risk_level'] <= Maxrisk)]
    
st.sidebar.header('choose your filter: ')
#  create for category 
category=st.sidebar.multiselect("Pick Your category",df["category"].unique())
if not category:
    df2=df.copy()
else:
    df2 = df[df["category"].isin(category)]
#  for single value 
# category=st.sidebar.selectbox("Pick Your category",df["category"].unique())
# if not category:
#     df2=df.copy()
# else:
#     df2 = df[df["category"].isin(category)]
#  cretae for subcategory
# -------
subcategory=st.sidebar.multiselect("Pick the subcategory",df2['sub_category'].unique())
if not subcategory:
    df3=df2.copy()
else:
    df3=df2[df2["sub_category"].isin([subcategory])]
# ---
# st.sidebar.header('Subcategory')
# selected_category=st.sidebar.multiselect('select category:',df['category'].unique())
# st.sidebar.header('sub_category(category_type)')
# selected_subcategory_category=st.sidebar.multiselect('pick your sub_category',df.groupby('category')['sub_category'].unique())
# st.subheader(f'Displaying information for {selected_category}')
# if not selected_subcategory_category:
#     df_filtered_category = df[df['category'] == selected_category]
#     df3=df2.copy()
# else:
#     df_filtered_category = df[(df['category'] == selected_category) & (df['sub_category'].isin(selected_subcategory_category))]
#     st.write(df_filtered_category)
#     st.sidebar.header('Sub-Sidebar (Subcategory Level)')
# selected_subcategory_subcategory = st.sidebar.multiselect("Pick Subcategory for Subcategory", df_filtered_category['sub_category'].unique())

#  for single subcategory
# subcategory=st.sidebar.selectbox("Pick the subcategory",df2['sub_category'].unique())
# if not subcategory:
#     df3=df2.copy()
# else:
#     df3=df2[df2["sub_category"].isin(subcategory)]
# subcategory=st.sidebar.selectbox("Pick the subcategory",df2['sub_category'].unique())
# if not subcategory:
#     df3=df2.copy()
# else:
#     df3=df2[df2["sub_category"].isin([subcategory])]

#  for risk level
scheme_name=st.sidebar.multiselect("Choose scheme name ",df3['scheme_name'].unique())

# filter for the data based n category , sub_category, scheme_name
if not category and not subcategory and not scheme_name:
    filtered_df=df
elif not subcategory and not scheme_name:
    filtered_df=df[df["category"].isin(category)]
elif not category and not scheme_name: #df3 : df2
    filtered_df=df2[df["sub_category"].isin(subcategory)]
elif not category and not subcategory:
     filtered_df=df3[df["scheme_name"].isin(scheme_name)]
elif subcategory and  scheme_name:
    filtered_df=df3[df["sub_category"].isin(subcategory) & df3['scheme_name'].isin(scheme_name)]
elif category and  scheme_name:
    filtered_df=df3[df["category"].isin(category) & df3['scheme_name'].isin(scheme_name)]
elif category and  subcategory:
    filtered_df=df3[df["category"].isin(category) & df3['sub_category'].isin(subcategory)]
elif scheme_name:
    filtered_df=df3[df3["scheme_name"].isin(scheme_name)]
elif category: #
    filtered_df=df3[df["category"].isin(category)]
elif subcategory: #
    filtered_df=df3[df["sub_category"].isin(subcategory)]
elif category and  subcategory and  scheme_name:
    filtered_df=df #df3
    
else:
    filtered_df=df3[df3["category"].isin(category)&df3["sub_category"].isin(subcategory)& df3["scheme_name"].isin(scheme_name)]
   
category_df=filtered_df.groupby(by= ['category'], as_index=False)['fund_age_yr'].mean() #category
try:
     with col1:
            st.subheader("category wise fund age")
            fig=px.bar(category_df,
               x=category,
               y='fund_age_yr', text=['Age {:,.0f}'.format(x) for x in category_df['fund_age_yr']],
                template = 'seaborn')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig,use_container_width=True,height=200)

     with col2:
            st.subheader("subcategory wise fund age")
            sub_category_df=filtered_df.groupby('sub_category')["fund_age_yr"].mean().reset_index()
            fig=px.pie(sub_category_df.head(10),values ='fund_age_yr',names='sub_category',hole=0.5)
            fig.update_traces(text=filtered_df['sub_category'],textposition='outside',opacity=0.8,textfont=dict(color='DarkBlue'))
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig,use_container_width=True)
except ValueError:
       print("value Error")

# Download Data
cl1,cl2=st.columns(2)
with cl1:
    with st.expander("category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv=category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download_Data",data=csv,file_name="category.csv",mime="txt/csv",help="click here to download the data ")
        
with cl2:
    with st.expander("subcategory_ViewData"):
        sub_category=filtered_df.groupby('sub_category')["fund_age_yr"].mean().reset_index()
        st.write(sub_category.style.background_gradient(cmap="Blues"))
        csv=sub_category.to_csv(index=False).encode('utf-8')
        st.download_button("Download_Data",data=csv,file_name="subcategory.csv",mime="txt/csv",help="click here to download the data as a csv_file")




# create a piechart based on  sharpe
chart1,chart2=st.columns(2)
with chart1:
    st.subheader("category wise sharpe")
    fig=px.pie(filtered_df,values='sharpe',names='category',template="plotly_dark")
    fig.update_traces(text=filtered_df['category'],textposition="outside",textfont=dict(color='DarkBlue'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig,use_container_width=True)
    
with chart2:
    st.subheader("subcategory wise sharpe")
    fig=px.pie(filtered_df.head(10),values='sharpe',names='sub_category',template="plotly_dark")
    fig.update_traces(text=filtered_df['sub_category'],textposition="outside",textfont=dict(color='DarkBlue'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig,use_container_width=True)
# creating pie chart using rating
category_mean_rating= filtered_df.groupby('category')['rating'].mean().reset_index()
chart3,chart4=st.columns(2)
rating=filtered_df['rating'].mean()
with chart3:
    st.subheader("category wise rating")
    fig=px.pie(category_mean_rating,values='rating',names='category',template="plotly_dark")
    fig.update_traces(text=category_mean_rating['category'],textposition="outside",textfont=dict(color='DarkBlue'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig,use_container_width=True)
    
category_mean_rating= filtered_df.groupby('sub_category')['rating'].mean().reset_index().head()
with chart4:
    st.subheader("subcategory wise rating")
    fig=px.pie(category_mean_rating,values='rating',names='sub_category',template="plotly_dark")
    fig.update_traces(text=category_mean_rating['sub_category'],textposition="outside",textfont=dict(color='DarkBlue'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig,use_container_width=True)
col3,col4=st.columns(2)
with col3:
    with st.expander("download view data"):
        category_mean_rating= filtered_df.groupby('category')['rating'].mean().reset_index()
        st.write(category_mean_rating.style.background_gradient(cmap='Blues'))
        csv=category_mean_rating.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data',data=csv,file_name="ctaegory.csv",mime="txt/csv",help="click here to download data")

with col4:
    with st.expander("sub_category_data"):
        category_mean_rating= filtered_df.groupby('sub_category')['rating'].mean().reset_index().head()
        st.write(category_mean_rating.style.background_gradient(cmap='Blues'))
        csv=category_mean_rating.to_csv(index=False).encode('utf-8')
        st.download_button('download Data',data=csv,file_name="sub_category.csv",mime="txt/csv",help="click here to download data")


        
chart5,chart8=st.columns(2)
category_mean_rating= filtered_df.groupby('scheme_name')['rating'].max().reset_index()
with chart5:
    st.subheader("scheme_name wise rating")
    fig=px.pie(category_mean_rating.head(10),values='rating',names='scheme_name',template="plotly_dark")
    fig.update_traces(text=category_mean_rating['scheme_name'],textposition="inside",textfont=dict(color='DarkBlue'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig,use_container_width=True)
    
category_mean_rating= filtered_df.groupby('amc_name')['rating'].max().reset_index()
with chart8:
    st.subheader("amc_name wise rating(mean)")
    fig=px.pie(category_mean_rating.head(10),values='rating',names='amc_name',template='plotly_dark')
    fig.update_traces(text=category_mean_rating['amc_name'],textposition='inside',textfont=dict(color='DarkBlue'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig,use_container_width=True)
data=filtered_df
# return_mean_df=filtered_df.groupby('category')['returns_1yr'].mean().reset_index()
chart6,=st.columns(1)
with chart6:
     st.subheader("category wise MAX return of returns_1yr,returns_3yr,returns_5yr")
     colors=['red','blue','green']
     max_values=data.groupby('category').agg({
         'returns_1yr':'max',
        'returns_3yr':'max',
        'returns_5yr':'max'
     }).reset_index()
     max_values=max_values.sort_values(by=['returns_1yr','returns_3yr','returns_5yr'],ascending=False).head()
     fig=px.line(
         max_values,
         x='category',
         y=['returns_1yr','returns_3yr','returns_5yr'],
         markers=True,
         labels={'values':'MAX Returns'},
         color_discrete_sequence=colors, 
       )
     for col in ['returns_1yr', 'returns_3yr', 'returns_5yr']:
        fig.add_trace(go.Scatter(x=max_values['category'], y=max_values[col],
                                 mode='text', text=max_values[col].round(2),
                                 textposition='bottom center'))
     fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
     fig.update_traces(marker=dict(size=10),textfont=dict(color='DarkBlue'))
     st.plotly_chart(fig,use_container_width=True)
     

chart7,=st.columns(1)   
with chart7:
    st.subheader("subcategory wise MAX returns of returns_1yr,returns_3yr,returns_5yr")
    # max_values=filtered_df.groupby('sub_category').agg({
    #     'returns_1yr':'max',
    #     'returns_3yr':'max',
    #     'returns_5yr':'max'
    # }).reset_index()
    
    max_values=data.sort_values(by=['returns_1yr','returns_3yr','returns_5yr'],ascending=False).head(5)
    colors=['red','blue','orange']
    
    fig=px.line(
        max_values,
        x='sub_category',
        y=['returns_1yr','returns_3yr','returns_5yr'],
        markers=True,
        labels={'values':'MAX Returns'},
        color_discrete_sequence=colors,
        
        # text=['{:,.2f}'.format(x) for x in mean_values[['returns_1yr', 'returns_3yr', 'returns_5yr']].values.flatten()]
    )
    for col in ['returns_1yr', 'returns_3yr', 'returns_5yr']:
        fig.add_trace(go.Scatter(x=max_values['sub_category'], y=max_values[col],
                                 mode='text', text=max_values[col].round(2),
                                 textposition='bottom center'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig.update_traces(marker=dict(size=10),textfont=dict(color='DarkBlue')
    
    #   text=[f'{y:.2f}' for y in mean_values[['returns_1yr', 'returns_3yr', 'returns_5yr']].values.flatten()]
      )
    
    st.plotly_chart(fig,use_container_width=True)
    
# relationship between  data using pairplot
# chart8,=st.columns(1)
# with chart8:
    # st.subheader("Pairplot of data")
    # fig=sns.pairplot(filtered_df,hue="category",corner=False)
    # st.pyplot(fig,use_container_width=True)
    
    