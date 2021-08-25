#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 16:13:57 2021

@author: zhixinglu
"""

import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.sidebar.title("Navigation Pane")
option = st.sidebar.selectbox('', ('Abstract', 'Background Information', 'Getting to Know this Dataset', 'Factors', 'Results and Solution', 'Bibliography'))

MLW = pd.read_csv("MLW.csv")
MLWmeta = pd.read_csv("MLW_Meta.csv")

MLW = MLW.fillna(0)
amount = MLW.iloc[:, MLW.columns.get_loc('G1'):MLW.columns.get_loc('G213') + 1].sum().reset_index()
amount = amount.rename(columns = {'index': 'generalcode'})

difcategories = MLWmeta.merge(amount, on = 'generalcode')
totcategories = difcategories.groupby('category').sum().reset_index()
totcategories = totcategories.rename(columns = {0: 'amount'}).sort_values('amount', ascending = False)

categories = px.bar(totcategories, x = 'category', y='amount', color = 'category')


cc = pd.read_csv("Countrycode.csv")
renamedcc = cc.rename(columns={"Alpha-2 code":"BeachCountrycode", "English short name lower case": "countryname"})
renamedcc = renamedcc[['countryname', 'BeachCountrycode']]

bycountry = renamedcc.merge(MLW, on = 'BeachCountrycode')

bycountry['BeachLength_nozeros'] = bycountry['BeachLength_m'].replace({0:1})
bycountry['BeachLength_changed'] = (np.log2(bycountry['BeachLength_nozeros'])) * (np.log2(bycountry['BeachLength_nozeros']))
bycountry['totaltrash'] = MLW.iloc[:, 14:].sum(axis = 1)
bycountry_noout = bycountry.loc[bycountry['totaltrash'] < 10000]
bycountry_zoomin = bycountry.loc[bycountry['totaltrash'] < 300]

    

if option == 'Abstract':
    st.markdown('# Abstract')
    st.markdown("This case study uses a dataset provided by the European Enviornment Agency and analyzes the factors that influence the amount of trash on a beach. After making assumptions and conducting simulations to prove them, conclusions were made that the amount of trash on a beach is solely related to the regional sea that the beach is located in. Select from the sidebar to see the full case study.")
    
    
if option == 'Background Information':
    st.markdown('# Background Information')
    st.markdown("Nowadays, people are raising awareness towards pollution on both land and sea. However, there is this coastal ecosystem that often gets “underrepresented in science and largely unrecognized in management practices”, as mentioned on beachapedia.org, a website that focuses on the ecology, regulations, and damages of beaches, especially in the US. With beaches “receiving little, if any, ecological protection”, many organizations, such as the European Environment Agency, Surfrider Foundation, and Pacific Beach Coalition are taking action in saving these indispensable ecosystems.")
    st.markdown("This case study presents data from an application named Marine Litter Watch, designed to “keep track of all the efforts made to keep our beaches clean” and provided by the European Environment Agency.")
    
    st.markdown("## The Original Datasets")
    st.markdown("The first dataset, the main one, includes basic information for every beach - The beach name, the cleanup community's name, the beach's location... Click the expand key to zoom in")
    st.dataframe(MLW)
    st.markdown("")
    st.markdown("")
    st.markdown("However, at the very end of the first dataset, there are these columns named 'G1, G2, ...', what do they mean? Each one of these columns represents a specific type of trash. This second dataset classifies all these codes into big garbage categories, such as Plastic, cloth/textiles, metal...")
    st.dataframe(MLWmeta)
    st.markdown("")
    st.markdown("")
    st.markdown("Additionally, the Beach Country code in the main dataset is not straighforward and easy to understand. Therefore, I downloaded a dataset that matches every Beach Country Code to the real country name.")
    st.dataframe(cc)
    st.markdown("Before we start doing any operations, let us first get familiar with this dataset")
    
if option == 'Getting to Know this Dataset':
    st.markdown('# Quick analyses on this Dataset')
    st.markdown('## 1.Different Types of Trash in Numerous European Countries')
    st.markdown("")
    st.markdown("This graph shows the amount of the types of trash recorded in this Marine Litter Watch.")
    
    #Sorting different types of trash from the largest amount to the lowest generally.
    st.plotly_chart(categories)
    st.markdown("Apparently, PLASTIC is the most common trash.")
    st.markdown("")
    st.markdown("Sources of these garbage:")
    st.markdown("1. The tourists. Beaches are the ideal attraction for holiday, and so the high tourists flows leave behind them all kinds of plastic waste, such as food wrappers, beverage bottles, or plastic toys and tools.")
    st.markdown("2. The locals. The lack of education and recycling regulations would often lead to locals dumping their everyday wastes on beaches or any other natural enviornment.")
    st.markdown("3. Industrial waste. These wastes are extremely detrimental to natural habitats. Acids and other chemicals in them may decrease the pH in the sea and impact the coastal ecosystems")
    st.markdown("4. The ocean. Rubbish often gets carried by the tides and washed on shore because of highly polluted oceans. These garbage even be produced by foreign countries.")
    st.markdown("5. Some specific incidents, such as the Japanese tsunami that sent large quantities of foam up the coastlines of Alaska.")
    st.markdown("")
    only_trash = bycountry.iloc[:, 15:177]
    
    #Sorting, in general, the country with the most trash to the least
    st.markdown('## 2.The countries with the most trash')
    
    st.markdown("This graph shows the mean of the amount of trash in each country. (Taking the mean of the amount of trash on the beaches in each country)")
    countrytrash = bycountry.groupby('countryname')['totaltrash'].mean().reset_index()
    countrytrash = countrytrash.sort_values('totaltrash', ascending = False)
    countrytrashhist = px.bar(countrytrash, x = 'countryname', y = 'totaltrash', color = 'countryname')
    st.plotly_chart(countrytrashhist)
    st.markdown("A country in Northern Europe bordering the Baltic Sea, Estonia, has the most trash in general.")
    
    #Sorting, for each type of trash, the country with the most trash to the least
    st.markdown("Below is a interactive graph that shows the ranking of countries for each type type of trash. Select the type of trash from the select box.")
    MLWmeta_with_index = MLWmeta.set_index('generalcode')
    transpose_MLWmeta = MLWmeta_with_index.transpose()
    
    category_trash = pd.concat([transpose_MLWmeta, only_trash]).transpose()
    country_trash = category_trash.groupby('category').sum().transpose()
    country_trash = country_trash.drop('generalname')
    
    country_names = bycountry['countryname']
    country_names = country_names.reset_index()
    
    beach_type_trash = pd.concat([country_names, country_trash], axis = 1)
    
    unique_country_names = beach_type_trash['countryname'].unique()
    
    
    def country(a):
        return beach_type_trash.loc[beach_type_trash['countryname'] == a].iloc[:, 2:].mean().reset_index().set_index('index').transpose()
    
    final = pd.DataFrame()
    for i in unique_country_names:
        final = final.append(country(i))
        
    final['countryname'] = unique_country_names
    
    col1, col2 = st.beta_columns(2)
    
    with col1:
        st.markdown("")
        st.markdown("")
        optypetrash = st.selectbox('', ('Chemicals', 'Cloth/textile', 'Glass/ceramics', 'Metal', 'Paper/Cardboard', 'Plastic', 'Processed/worked wood',	'Rubber', 'unidentified'))
        st.markdown("Because of some extreme differences between countries, the bars in this graph are log2s of the real values.")
    with col2:
        sort = final.sort_values(optypetrash, ascending = False)
        tmp = px.bar(sort, x = 'countryname', y = optypetrash, title = optypetrash, log_y = True, color = 'countryname')
        st.plotly_chart(tmp)

if option == 'Factors':
    st.markdown("# Research Question")
    st.markdown('Research question: Which of the following factors -- size of the beach, its urbanization level, its type, and the regional sea it is located in -- contributed to the amount of trash on that beach?')
    st.markdown("Scroll down to see the four different hypotheses.")

    st.markdown("## 1. Size of the Beaches")
    st.markdown("My first hypothesis is that the amount of trash on a beach may be related to its size. Is this true?")
    st.markdown("First, let's see a visualized version of the data.")
        
    st.markdown('### Visualized version - Maps of the Beaches')
    st.markdown("These maps depict the location of the beaches in this Marine Litter Watch program. Each circle represents a beach, and different colors represent different countries. ")
    st.markdown("Hover your mouse above the circles, and you will see four parameters:")
    st.markdown("1. Country name")
    st.markdown("2. Altered Beach Length - If the caption says 'BeachLength_changed', then some changes were made to enlarge the difference between the circles. (It is calculated by squaring the log of the actual beach length)")
    st.markdown("3. The latitude of the location of the beach")
    st.markdown("4. The longtitude of the location of the beach")
    st.markdown("")
        
    st.markdown("Compare the two European maps below, are the sizes of the circles in these two graphs in proportion with each other?")
    #europe size map
    st.markdown('#### Map of Europe - Size of the Beaches')
    st.markdown("In this map, the sizes of the circles are determined by the length of the beach")
    beachmap_euro_size = px.scatter_geo(bycountry, lat = "lat_y1", lon = "lon_x1", 
                                        hover_name = 'countryname', projection = "natural earth", 
                                        size = "BeachLength_changed", color = 'countryname',
                                        locationmode = "country names")
    beachmap_euro_size.update_layout(
        geo = dict(
            scope='europe',
            showcountries = True,
        ),
    )
    st.plotly_chart(beachmap_euro_size)
    
    #europe - amount trash map
    st.markdown('#### Map of Europe - Amount of Trash')
    st.markdown("In this map, the sizes of the circles are determined by the amount of trash on the beach")
        
    beachmap_euro_trash = px.scatter_geo(bycountry, lat = "lat_y1", lon = "lon_x1", 
                                         hover_name = 'countryname', projection = "natural earth", 
                                         size = "totaltrash", color = 'countryname',
                                         locationmode = "country names")
    beachmap_euro_trash.update_layout(
        geo = dict(
            scope='europe',
            showcountries = True,
        ),
    )
    st.plotly_chart(beachmap_euro_trash)
        
    st.markdown("Look at the biggest circles in the first map, are there also big circles at the same location in the second graph? No :(. Sadly, the size and the amount of trash on these beaches are not in proportion, therefore, the sizes of the beaches do not affect the amount of trash on them.")
    st.markdown("")
    st.markdown("Below are two world maps – not all beaches in this study are in Europe – also depicting the size of the beaches and the amount of trash on these beaches.")
    #worldwide size map
    st.markdown('#### Worldwide Map - Size of the Beaches')
    beachmap_size = px.scatter_geo(bycountry, lat = "lat_y1", lon = "lon_x1", 
                                   hover_name = 'countryname', projection = "orthographic", 
                                   size = "BeachLength_changed", color = 'countryname',
                                   locationmode = "country names")
    st.plotly_chart(beachmap_size)
        
    #worldwide amount trashmap
    st.markdown('#### Worldwide Map - Amount of Trash')
    beachmap_trash = px.scatter_geo(bycountry, lat = "lat_y1", lon = "lon_x1", 
                                    hover_name = 'countryname', projection = "orthographic", 
                                    size = "totaltrash", color = 'countryname',
                                    locationmode = "country names")
    st.plotly_chart(beachmap_trash)
        
    st.markdown("Our eyes tell us from looking at these maps that the size of the beaches are not in proportion with the amount of trash on them. But how can we prove this with datascience and plots?")
    st.markdown('### Datascience version - Plots of Correlation')
        
    st.markdown("Below are plots that show the correlation between the size of the beaches and the amount of trash on them.")
    st.markdown('If there is a correlation between the two variables, then the datapoints on the following graphs should have a trend, either positive or negative.')
        
    #original scatter plot
    correl = px.scatter(bycountry, x = 'BeachLength_m', y = 'totaltrash')
    st.plotly_chart(correl)
        
    st.markdown("Since there are a few outliers that affects our view, a zoomed-in version is provided below containing only beach lengths less than 1000 meters")
    #zoom in version
    bycountry_cutlength = bycountry.loc[bycountry['BeachLength_m'] < 1000]
    correl_zoomin = px.scatter(bycountry_cutlength, x = 'BeachLength_m', y = 'totaltrash')
    st.plotly_chart(correl_zoomin)
        
    st.markdown("We can see from the graphs that there is no correlation between the size of the beaches and the amount of trash on them. Therefore, my first hypothesis failed.")
        
        
    st.markdown("## 2. The Urbanization Level and Location of the Beach")
    st.markdown("My second hypothesis is that the amount of trash on a beach may be related to its urbanization level or location")
    rural = bycountry.loc[bycountry['BeachLocation'] == 'Rural']['totaltrash']
    urban = bycountry.loc[bycountry['BeachLocation'] == 'Urban']['totaltrash']
    nrm = bycountry.loc[bycountry['BeachLocation'] == 'Near river mouth']['totaltrash']
            
    rural_10K = bycountry_noout.loc[bycountry['BeachLocation'] == 'Rural']['totaltrash']
    urban_10K = bycountry_noout.loc[bycountry['BeachLocation'] == 'Urban']['totaltrash']
    nrm_10K = bycountry_noout.loc[bycountry['BeachLocation'] == 'Near river mouth']['totaltrash']
    #Rural vs. Urban vs. Near river mouth
    col1, col2 = st.beta_columns([1, 2])
    with col1:
        st.markdown("")
        st.markdown("")
        opbeachloc = st.selectbox('', ('Rural', 'Urban', 'Near river mouth'))
        st.markdown("Three urbanization levels/ beach locations are recorded in this dataset: Urban, Rural, or Near River Mouth. Choose from the select box above to see the distribution for each of them")
    with col2:
        beachloc = bycountry.loc[bycountry['BeachLocation'] == opbeachloc]['totaltrash']
        lochist = px.histogram(beachloc, x = 'totaltrash', nbins=50)
        lochist.update_layout(bargap=0.1)
        lochist.update_layout(width=800,height=500)
        st.plotly_chart(lochist)
      
    dis = st.selectbox("", ("Original Dataset", "No Outliers"))
    st.markdown('#### Overlapping Distributions:')
    if dis == "Original Dataset":
        #original dataset overlapping histogram 
        
        col1, col2 = st.beta_columns([1, 1])
        with col1:
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("On the right is the distribution of the total amount of trash in three different locations, rural, urban and near river mouth. Although there are a lot less beaches near river mouths, the overall trend of the three distributions are approximately the same – all skewed to the right. The urban beaches have the most extreme outliers (above 10k), while the rural beaches have plenty of datapoints between 5k and 10k; however, the beaches near river mouth are aggregated between 0 and 5k. With this, we can infer that the average of the “Near River Mouth” distribution will be greatly less than the other two distributions. ")
        
        with col2:
            
            beachlocfig = go.Figure()
            beachlocfig.add_trace(go.Histogram(name = "Rural", x=rural, bingroup = "stack"))
            beachlocfig.add_trace(go.Histogram(name = "Urban", x=urban, bingroup = "stack"))
            beachlocfig.add_trace(go.Histogram(name = "Near River Mouth ", x=nrm, bingroup = "stack"))
            
            
            beachlocfig.update_layout(barmode='overlay')
            beachlocfig.update_traces(opacity=0.50)
            beachlocfig.update_layout(width=800,height=500)
            st.plotly_chart(beachlocfig)
    
    if dis == 'No Outliers':
        #no outlier dataset overlapping histogram 
        col1, col2 = st.beta_columns([1, 1])
        with col1:
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("However, the above distribution is too vague for us to notice any difference; so this histogram depicts all beaches with the amount of trash less than 10k. The distributions are highly similar below 3k, with about ten urban beaches from 4k to 6k and mainly rural beaches from 6k to 10k. Additionally, the beaches that are near river mouths have less data points from 0 – 0.2k, meaning that its median might be bigger than the other two locations.")
        
        with col2:
            
            beachlocfig2 = go.Figure()
            beachlocfig2.add_trace(go.Histogram(name = "Rural", x = rural_10K, bingroup = "stack"))
            beachlocfig2.add_trace(go.Histogram(name = "Urban", x = urban_10K, bingroup = "stack"))
            beachlocfig2.add_trace(go.Histogram(name = "Near River Mouth ", x = nrm_10K, bingroup = "stack"))
        
            beachlocfig2.update_layout(barmode='overlay')
            beachlocfig2.update_traces(opacity=0.50)
            beachlocfig2.update_layout(width=800,height=500)
            st.plotly_chart(beachlocfig2)
    
    #mean median
    col1, col2 = st.beta_columns([1, 1])
    with col1:
        st.markdown("Median")
        medianbeachlocation = bycountry.groupby('BeachLocation')['totaltrash'].median().reset_index().sort_values('totaltrash', ascending = False).drop(0)
        st.dataframe(data = medianbeachlocation)
        
    with col2:
        
        st.markdown("Mean")
        meanbeachlocation = bycountry.groupby('BeachLocation')['totaltrash'].mean().reset_index().sort_values('totaltrash', ascending = False).drop(0)
        st.dataframe(data = meanbeachlocation)
        
    st.markdown("As we can see, all three distributions are highly skewed, with outliers; so we should compare the medians when determining whether the location of the beach has a relationship with the amount of trash in the area. There is a difference of 36.5 between the rural and urban beaches and 48.5 between beaches that are near river mouths and urban ones. However, are these differences significant enough? Let us perform a simulation.") 
    
    def mediansim(want, standard, a, b):
            anum = bycountry.loc[bycountry[standard] == a]['countryname'].count()
            bnum = bycountry.loc[bycountry[standard] == b]['countryname'].count()
            
            if want == 'median':
                df = pd.DataFrame(columns = ['dif_medians'])
                for i in np.arange(5000):
                    sample = bycountry.sample(n = anum + bnum, replace = False)
                    amedian = sample.iloc[0:anum, :]['totaltrash'].median()
                    bmedian = sample.iloc[anum: anum + bnum, :]['totaltrash'].median()
                    row = {'dif_medians': abs(amedian - bmedian)}
                    df = df.append(row, ignore_index = True)
            
            if want == 'mean':
                df = pd.DataFrame(columns = ['dif_means'])
                for i in np.arange(5000):
                    sample = bycountry.sample(n = anum + bnum, replace = False)
                    amean = sample.iloc[0:anum, :]['totaltrash'].mean()
                    bmean = sample.iloc[anum: anum + bnum, :]['totaltrash'].mean()
                    row = {'dif_means': abs(amean - bmean)}
                    df = df.append(row, ignore_index = True)
            return df
    
    
    #standard: which aspect of the beach, location/type...
    #function to conduct simulation
    
    sim = st.checkbox("Open Beach Urbanization Level Simulation")
    
    if sim == True:
        st.markdown("")
        st.markdown("### Simulation:")
        st.markdown("To test if the difference is significant enough, we need to do a random simulation.")
        st.markdown("The null hypothesis is that the difference is caused by random chance, while the alternate hypothesis is that the difference is significant enough to prove our big assumption. ")
        st.markdown("Steps of to make a simulation (Taking Urban and Rural for example):")
        st.markdown("1.	Calculate the difference between the medians of the total trash on urban and rural beaches and name it [dif].")
        st.markdown("2. Find out the number of urban beaches in the original dataset and name it [anum]. Find out the number of rural beaches and name it [bnum].")
        st.markdown("3. Take a sample with size [anum] from the original dataset, and without replacing the values, take a sample with size [bnum]")
        st.markdown("4. Find out difference between the medians of the two samples and append it to a series named [df].")
        st.markdown("5. Repeat these steps for 5000 times. After that, you can have a series of 5000 values.")
        st.markdown("6.	Plot all the values out in a histogram. This will be the randomized simulation distribution")
        st.markdown("7. Calculate the [p-value]( https://www.scribbr.com/statistics/p-value/) (in my case the top 5% of the series) ")
        st.markdown("8. Compare the p-value with [dif]. If [dif] is greater than the p-value, then there is a relationship between the beach’s urbanization level and the amount of trash on it.")
        st.markdown("")
        st.markdown("")
        st.markdown("This is the randomized histogram for rural and urban beaches")
        medianloc = mediansim('median', 'BeachLocation', 'Rural', 'Urban')
        medianloc = medianloc.sort_values('dif_medians', ascending = False).reset_index()
        medianlochist = px.histogram(medianloc, x = 'dif_medians')
        p_value = medianloc.loc[250].dif_medians
        medianlochist.add_vline(x=p_value, line_dash = 'dash', annotation_text="P-value", annotation_position="right top", line_color = 'firebrick')
        medianlochist.add_vline(x=36.5, line_dash = 'dash', annotation_text="Calculated difference", annotation_position="left top", line_color = 'yellow')
        st.plotly_chart(medianlochist)
        st.markdown("This histogram shows the distribution of the 5000 trials. The yellow line is the real difference between rural and urban beaches: 36.5. The red line is P-value (See below how it was calculated)")
        
        st.markdown("")
        st.markdown("")
        col1, col2 = st.beta_columns([1, 1])
        with col1:
            st.markdown("This is the series mentioned above, recording the 5000 differences I simulated. 5000 is a fair number, but the more trials I do, the histogram approaches closer to a bell-shape. The differences are sorted from biggest to smallest.")
            st.markdown("Since 5% of 5000 is 250. Therefore the p-value in this case is the 250th number in the series.")
            st.write("The p-value is:", p_value)
            st.write("The real difference:", 36.5)
            
        with col2:
            st.dataframe(medianloc)
        
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    
    #Sandy vs. Rocky vs. Pebbles
    st.markdown("## 2. The Type of Beach")
    
    sandy = bycountry.loc[bycountry['BeachType'] == 'Sandy']['totaltrash']
    rocky = bycountry.loc[bycountry['BeachType'] == 'Rocky']['totaltrash']
    pebbels = bycountry.loc[bycountry['BeachType'] == 'Pebbels']['totaltrash']
    Other = bycountry.loc[bycountry['BeachType'] == 'Other (mixed)']['totaltrash']
        
    sandy_10K = bycountry_noout.loc[bycountry_noout['BeachType'] == 'Sandy']['totaltrash']
    rocky_10K = bycountry_noout.loc[bycountry_noout['BeachType'] == 'Rocky']['totaltrash']
    pebbels_10K = bycountry_noout.loc[bycountry_noout['BeachType'] == 'Pebbels']['totaltrash']
    Other_10K = bycountry_noout.loc[bycountry_noout['BeachType'] == 'Other (mixed)']['totaltrash']
        
    sandy_zoomin = bycountry_zoomin.loc[bycountry_zoomin['BeachType'] == 'Sandy']['totaltrash']
    rocky_zoomin = bycountry_zoomin.loc[bycountry_zoomin['BeachType'] == 'Rocky']['totaltrash']
    pebbels_zoomin = bycountry_zoomin.loc[bycountry_zoomin['BeachType'] == 'Pebbels']['totaltrash']
    Other_zoomin = bycountry_zoomin.loc[bycountry_zoomin['BeachType'] == 'Other (mixed)']['totaltrash']
    
    col1, col2 = st.beta_columns([1, 1])
    with col1:
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        opbeachtype = st.selectbox('', ('Sandy', 'Rocky', 'Pebbles', 'Other (mixed)'))
        st.markdown("There are four types of beaches in this dataset: Sandy, Rocky, Pebbels, and Mixed. We will mainly focus on the first three. Select the select box above to see the distribution for each type of beach")
    with col2:
        beachtype = bycountry_noout.loc[bycountry['BeachType'] == opbeachtype]['totaltrash']

        typehist = px.histogram(beachtype, x = 'totaltrash', nbins=50)
        typehist.update_layout(bargap=0.1)
        typehist.update_layout(width=800,height=500)
        st.plotly_chart(typehist)
        
    
    dis2 = st.selectbox("", ("Original Dataset ", "No Outliers ", "Zoom In "))
    st.markdown("### Overlapping Distributions")
    #original dataset overlapping histogram 
    if dis2 == "Original Dataset ":
        
        col1, col2 = st.beta_columns([1, 2])
        with col1:
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("Again, we can see that the shapes of these three distributions are very similar, all skewed to the right. We can see that rocky beaches have only a few outliers and is pretty compacted between 0 and 2k; so we can infer that is has a low mean. Also, Sandy beaches have about ten data points between 2k and 10k, while rocky beaches only have a few extreme outliers. We can therefore infer that the Sandy beaches would have a high mean. ")
        
        with col2: 
            beachtypefig = go.Figure()
            beachtypefig.add_trace(go.Histogram(name = "Sandy", x = sandy, bingroup = "stack"))
            beachtypefig.add_trace(go.Histogram(name = "Pebbles", x = pebbels, bingroup = "stack"))
            beachtypefig.add_trace(go.Histogram(name = "Rocky", x = rocky, bingroup = "stack"))
            
            #beachtypefig.add_trace(go.Histogram(name = "Other", x = Other, bingroup = "stack"))
        
            beachtypefig.update_layout(barmode='overlay')
            beachtypefig.update_traces(opacity=0.50)
            beachtypefig.update_layout(width=800,height=500)
            st.plotly_chart(beachtypefig)
    
    #without outliers dataset overlapping histogram 
    if dis2 == "No Outliers ":
        col1, col2 = st.beta_columns([1, 2])
        with col1:
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("This is the same distribution without outliers. If you look at the medians in the chart below, you can see that all the medians would be in the first bin in this distribution (you can hover your mouse above the bin to see the range). As a result, we can no longer explain the median from the shape of the distribution. ")
        
        with col2: 
            beachtypefig2 = go.Figure()
            beachtypefig2.add_trace(go.Histogram(name = "Sandy", x = sandy_10K, bingroup = "stack"))
            beachtypefig2.add_trace(go.Histogram(name = "Pebbles", x = pebbels_10K, bingroup = "stack"))
            beachtypefig2.add_trace(go.Histogram(name = "Rocky", x = rocky_10K, bingroup = "stack"))
            
            #beachtypefig.add_trace(go.Histogram(name = "Other", x = Other_10K, bingroup = "stack"))
        
            beachtypefig2.update_layout(barmode='overlay')
            beachtypefig2.update_traces(opacity=0.50)
            beachtypefig2.update_layout(width= 800,height=500)
            st.plotly_chart(beachtypefig2)
            
    if dis2 == "Zoom In ":   
        col1, col2 = st.beta_columns([1, 2])
        with col1:
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("With the zoomed in version, we can now explain why Rocky beaches have the highest median. The data points of rocky beaches are laid out and spread evenly across the axis. Therefore, the median would be closer to the middle of the distribution.")
        with col2:
            beachtypefig3 = go.Figure()
            beachtypefig3.add_trace(go.Histogram(name = "Sandy", x=sandy_zoomin, bingroup = "stack"))
            beachtypefig3.add_trace(go.Histogram(name = "Pebbles", x=pebbels_zoomin, bingroup = "stack"))
            beachtypefig3.add_trace(go.Histogram(name = "Rocky", x=rocky_zoomin, bingroup = "stack"))
            
            #fig2.add_trace(go.Histogram(name = "Other", x=Other, bingroup = "stack"))
            
            beachtypefig3.update_layout(barmode='overlay')
            beachtypefig3.update_traces(opacity=0.50)
            beachtypefig3.update_layout(width= 800,height=500)
            st.plotly_chart(beachtypefig3)
        
    #mean median
    col1, col2 = st.beta_columns([1, 1])
    with col1:
        st.markdown("Median")
        medianbeachtype = bycountry.groupby('BeachType')['totaltrash'].median().reset_index().sort_values('totaltrash', ascending = False).drop(0)
        st.dataframe(data = medianbeachtype)
        
    with col2:
        
        st.markdown("Mean")
        meanbeachtype = bycountry.groupby('BeachType')['totaltrash'].mean().reset_index().sort_values('totaltrash', ascending = False).drop(0)
        st.dataframe(data = meanbeachtype)
        
    st.markdown("As we can see, all three distributions are highly skewed, with outliers; so we should compare the medians when determining whether the type of the beach has a relationship with the amount of trash in the area. There is a difference of 68.5 between the rocky and pebble beaches. However, is this difference big enough? Let us do another simulation.")
    sim2 = st.checkbox("Open Beach Type Simulation")
    
    if sim2 == True:
        st.markdown("This is the randomized histogram for the Rocky and Pebble beaches")
        mediantype = mediansim('median', 'BeachType', 'Rocky', 'Pebbels')
        mediantype = mediantype.sort_values('dif_medians', ascending = False).reset_index()
        mediantypehist = px.histogram(mediantype, x = 'dif_medians')
        p_value2 = mediantype.loc[250].dif_medians
        mediantypehist.add_vline(x=p_value2, line_dash = 'dash', annotation_text="P-value", annotation_position="right top", line_color = 'firebrick')
        mediantypehist.add_vline(x=68.5, line_dash = 'dash', annotation_text="Calculated difference", annotation_position="left top", line_color = 'yellow')
        st.plotly_chart(mediantypehist)
        st.write("This histogram shows the distribution of the 5000 trials. The yellow line is the real difference between rural and urban beaches: 36.5. The red line is P-value:", p_value2)
        st.write("Again, the difference between pebbel and rocky beaches are less than the p-value. Also, since these two types of beaches has the greatest difference, there is no relationship between the beach's type and the amount of trash on it.")
    #regional sea
    st.markdown("")
    st.markdown("")
    st.markdown("")
    black = bycountry.loc[bycountry['BeachRegionalSea'] == 'Black Sea']['totaltrash']
    med = bycountry.loc[bycountry['BeachRegionalSea'] == 'Mediterranean Sea']['totaltrash']
    baltic = bycountry.loc[bycountry['BeachRegionalSea'] == 'Baltic Sea']['totaltrash']
    nea = bycountry.loc[bycountry['BeachRegionalSea'] == 'North-east Atlantic Ocean']['totaltrash']
    
    black_10k = bycountry_noout.loc[bycountry_noout['BeachRegionalSea'] == 'Black Sea']['totaltrash']
    med_10k = bycountry_noout.loc[bycountry_noout['BeachRegionalSea'] == 'Mediterranean Sea']['totaltrash']
    baltic_10k = bycountry_noout.loc[bycountry_noout['BeachRegionalSea'] == 'Baltic Sea']['totaltrash']
    nea_10k = bycountry_noout.loc[bycountry_noout['BeachRegionalSea'] == 'North-east Atlantic Ocean']['totaltrash']
    
    black_zoomin = bycountry_zoomin.loc[bycountry_zoomin['BeachRegionalSea'] == 'Black Sea']['totaltrash']
    med_zoomin = bycountry_zoomin.loc[bycountry_zoomin['BeachRegionalSea'] == 'Mediterranean Sea']['totaltrash']
    baltic_zoomin = bycountry_zoomin.loc[bycountry_zoomin['BeachRegionalSea'] == 'Baltic Sea']['totaltrash']
    nea_zoomin = bycountry_zoomin.loc[bycountry_zoomin['BeachRegionalSea'] == 'North-east Atlantic Ocean']['totaltrash']
    
    st.markdown("## 3. Regional Sea")
    col1, col2 = st.beta_columns([1, 1])
    with col1:
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        opbeachtype = st.selectbox('', ('Black Sea', 'Mediterranean Sea', 'Baltic Sea', 'North-east Atlantic Ocean'))
        st.markdown("There are four regional seas in this dataset: Black, Mediterranean, Baltic, and North East Atlantic Sea. Select the select box above to see the distribution for each type of beach")
    with col2:
        beachsea = bycountry_noout.loc[bycountry['BeachRegionalSea'] == opbeachtype]['totaltrash']

        seahist= px.histogram(beachsea, x = 'totaltrash', nbins=50)
        seahist.update_layout(bargap=0.1)
        seahist.update_layout(width=800,height=500)
        st.plotly_chart(seahist)
    
    dis3 = st.selectbox("", ("Original Dataset  ", "No Outliers  ", "Zoom In  "))
    st.markdown("### Overlapping Distributions")
    #original dataset overlapping histogram 
    if dis3 == "Original Dataset  ":
        
        col1, col2 = st.beta_columns([1, 2])
        with col1:
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("Again, we can see that the shapes of these three distributions are very similar, all skewed to the right. The Mediterranean Sea has a few outliers, so we can infer that it might have a low mean. Oh the other hand, the Baltic sea has an extreme outlier, which increases its mean for a great deal. ")
        
        with col2: 
            beachtypefig = go.Figure()
            beachtypefig.add_trace(go.Histogram(name = "Mediterranean Sea", x = med, bingroup = "stack"))
            beachtypefig.add_trace(go.Histogram(name = "North-east Atlantic", x = nea, bingroup = "stack"))
            beachtypefig.add_trace(go.Histogram(name = "Black Sea", x = black, bingroup = "stack"))
            beachtypefig.add_trace(go.Histogram(name = "Baltic Sea", x = baltic, bingroup = "stack"))
            
            #beachtypefig.add_trace(go.Histogram(name = "Other", x = Other, bingroup = "stack"))
        
            beachtypefig.update_layout(barmode='overlay')
            beachtypefig.update_traces(opacity=0.50)
            beachtypefig.update_layout(width=900,height=600)
            st.plotly_chart(beachtypefig)
            
    if dis3 == "No Outliers  ":
        
        col1, col2 = st.beta_columns([1, 2])
        with col1:
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("This is the same distribution without outliers. If you look at the medians in the chart below, you can see that all the medians would be in the first bin in this distribution (you can hover your mouse above the bin to see the range). As a result, we can no longer explain the median from the shape of the distribution. ")
        
        with col2: 
            beachseafig2 = go.Figure()
            beachseafig2.add_trace(go.Histogram(name = "Mediterranean Sea", x = med_10k, bingroup = "stack"))
            beachseafig2.add_trace(go.Histogram(name = "North-east Atlantic", x = nea_10k, bingroup = "stack"))
            beachseafig2.add_trace(go.Histogram(name = "Black Sea", x = black_10k, bingroup = "stack"))
            beachseafig2.add_trace(go.Histogram(name = "Baltic Sea", x = baltic_10k, bingroup = "stack"))
            
            #beachtypefig.add_trace(go.Histogram(name = "Other", x = Other, bingroup = "stack"))
        
            beachseafig2.update_layout(barmode='overlay')
            beachseafig2.update_traces(opacity=0.50)
            beachseafig2.update_layout(width=900,height=600)
            st.plotly_chart(beachseafig2)
    
    if dis3 == "Zoom In  ":
        
        col1, col2 = st.beta_columns([1, 2])
        with col1:
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("Again, we can see that the shapes of these three distributions are very similar, all skewed to the right. We can see that rocky beaches have only a few outliers and is pretty compacted between 0 and 2k; so we can infer that is has a low mean. Also, Sandy beaches have about ten data points between 2k and 10k, while rocky beaches only have a few extreme outliers. We can therefore infer that the Sandy beaches would have a high mean. ")
        
        with col2: 
            beachseafig3 = go.Figure()
            beachseafig3.add_trace(go.Histogram(name = "Mediterranean Sea", x = med_zoomin, bingroup = "stack"))
            beachseafig3.add_trace(go.Histogram(name = "North-east Atlantic", x = nea_zoomin, bingroup = "stack"))
            beachseafig3.add_trace(go.Histogram(name = "Black Sea", x = black_zoomin, bingroup = "stack"))
            beachseafig3.add_trace(go.Histogram(name = "Baltic Sea", x = baltic_zoomin, bingroup = "stack"))
            
            #beachtypefig.add_trace(go.Histogram(name = "Other", x = Other, bingroup = "stack"))
        
            beachseafig3.update_layout(barmode='overlay')
            beachseafig3.update_traces(opacity=0.50)
            beachseafig3.update_layout(width=900,height=600)
            st.plotly_chart(beachseafig3)
    
    #maps
    st.markdown("### Maps")
    show_map = st.checkbox("Show maps")
    if show_map == True:
        col1, col2, col3 = st.beta_columns([5, 5, 1])
        with col1:
            st.image('Europe.jpg', caption = "European Map")
        with col2:
            st.image('IMG_1732.JPG', caption = "Different Seas")
        with col3:
            st.image('mapkey.JPG', width = 150)
    #mean median
    st.markdown("")
    st.markdown("")
    st.markdown("### Mean and Median")
    col1, col2 = st.beta_columns([1, 1])
    with col1:
        st.markdown("Median")
        medianbeachtype = bycountry.groupby('BeachRegionalSea')['totaltrash'].median().reset_index().sort_values('totaltrash', ascending = False).drop(0)
        st.dataframe(data = medianbeachtype)
        
    with col2:
        
        st.markdown("Mean")
        meanbeachtype = bycountry.groupby('BeachRegionalSea')['totaltrash'].mean().reset_index().sort_values('totaltrash', ascending = False).drop(0)
        st.dataframe(data = meanbeachtype)
        
    st.markdown("Within our expectations, The Baltic Sea has the highest median and mean. However, why is this, and is this true? Let us ask google…")
    st.image("balticsea.png")
    st.write("Fortunately, google proved us right. With further research, the Baltic sea is mainly polluted by industrial waste and contaminated air caused by traffic and agriculture. Therefore, the coastal waters and beaches are contaminated with poisonous and detrimental substances. For more information, see [https://pubmed.ncbi.nlm.nih.gov/9722964/](https://pubmed.ncbi.nlm.nih.gov/9722964/)")
    
if option == 'Results and Solution':
    st.markdown("# Results and Solution")
    st.markdown("Let us look back on what we covered in this case study. Our purpose for this case study is to find out which factors are related to the amount of trash on a beach. I proposed four hypotheses:")
    st.markdown('1. The size of the beach')
    st.markdown('2. The urbanization level of the beach')
    st.markdown('3. The type of beach')
    st.markdown('4. The regional sea that the beach is located.')
    st.markdown('Among these four factors, only the last one is related to the amount of trash on the beaches. All the others are proved wrong through either correlation plots or simulations.')
    
    st.markdown("Marine pollution impacts both animals and us humans. According to nrdc.org, 'It is estimated that beach pollution affects more than 800 species of wildlife...', and that 'Plastic pollution has become so overwhelming that it is even affecting sea turtles' reproduction rates...'. We are also part of this story. Some of the aquatic products end up in our stomaches. Therefore, we should manage our own litter footprints and assist the cleanup organizations to help these vunerable coastal habitats.")
    st.markdown("Last but not least, special thanks to the European Enviornment Agency for the data collection and user 'Maarten' for posting this dataset on Kaggle.")
   
if option == 'Bibliography':
    st.markdown("# Sources")
    st.markdown("[http://beachapedia.org/Beach_Ecology](http://beachapedia.org/Beach_Ecology) // All about beaches")
    st.markdown("[https://www.nrdc.org/stories/beach-pollution-101](https://www.nrdc.org/stories/beach-pollution-101) // beach pollution, its impact and solution")
    st.markdown("[https://pubmed.ncbi.nlm.nih.gov/9722964/](https://pubmed.ncbi.nlm.nih.gov/9722964/) // baltic sea pollution")
    st.markdown("[https://mysweetgreens.com/5-polluted-seas-world/](https://mysweetgreens.com/5-polluted-seas-world/) // most polluted seas in the world")
    st.markdown("[https://www.frontiersin.org/articles/10.3389/fmars.2018.00233/full](https://www.frontiersin.org/articles/10.3389/fmars.2018.00233/full) // another case study")
