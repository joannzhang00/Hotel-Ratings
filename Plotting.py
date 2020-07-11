import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os 

statename = 'province'
cityname = 'city'
hotelname = 'name'


def pickStateAndCities(state, hotelsdf):
    '''this function will return a sorted city list according to the input state.
    It has two parameters, state and a dataframe including hotel information'''
    dg = hotelsdf.groupby(by = statename)
    
    #get unique city names and store them in an array
    cities = dg[cityname].unique()[state]
    cities.sort()
    
    return cities



def displayRatingInfo(state, hotelsdf, citylst):
    '''this function generate a dataframe including the hotel names and their corresponding\
    cities and states, it has three parameters, the input state, the dataframe including\
    hotel information, and a chosen cities in a list'''
    
    #select the hotel names for the input state 
    statedf = hotelsdf.loc[hotelsdf[statename] == state, [hotelname, cityname, statename]]
    
    ratinginfo = pd.DataFrame()
    
    #select the hotel names for the input cities and append them in the empty df
    for c in citylst:
        ratinginfo = ratinginfo.append(statedf.loc[statedf[cityname] == c])
    
    #reset the index starting from 0
    ratinginfo.reset_index(drop = True, inplace = True)
    #return the df for the third interaction
    return ratinginfo


def selectHotelReviews(reviewdf, ratinginfo):
    '''this function returns a dataframe on the basis of last function. It contains the total number\
    of reviews and average review rating for each hotel, also the proportion of ratings from 1-5 in\
    terms of all the ratings. It has two parameters, the hotel review information dataframe, and the\
    rating information dataframe including the hotel names and their corresponding cities and states'''
    
    #get the input state name
    state = ratinginfo[statename].unique()[0]
    
    #filter the review dataframe by this input state
    statereviewdf = reviewdf[reviewdf[statename] == state]

    #get target cities in a Series
    cities = ratinginfo[cityname].drop_duplicates()
    
    #group review dataframe by city
    gbcity = statereviewdf.groupby(by = cityname)
    
    #create an empty dataframe to store the aggregate review data
    ratingNum = pd.DataFrame()
    
    
    for i in range(len(cities)):
        #get every city group by unique city names
        citydf = gbcity.get_group(cities.iloc[i])
        #for the number i city, group by hotel name
        gbhotel = citydf.groupby(by = hotelname)
        #get the count of reviews and average of ratings of all hotel names in this city group
        agghotel = gbhotel.aggregate({'reviews_text':'count', 'reviews_rating':'mean'})
        
        agghotel = agghotel.reset_index()

        ratingNum = ratingNum.append(agghotel)
    
    #merge the ratingNum df and the ratinginfo df together to the the city as well as ratings information of each hotel
    reviewinfo = pd.merge(ratingNum, ratinginfo, how = 'inner', on = 'name').\
    sort_values(by = 'reviews_rating', ascending = False)
    
    reviewinfo.set_index(hotelname, inplace = True)
    
        
    for j in range(len(cities)):
        city = cities.iloc[j]

        #get every city group by unique city names
        citydf = gbcity.get_group(city)
        #get hotel name inside this city
        hotelnames = citydf[hotelname].drop_duplicates()
        
        #for the number i city, group by hotel name
        gbhotel = citydf.groupby(by = hotelname)
          
        
        #group the review dataframe by each hotel name
        for k in range(len(hotelnames)):
            hotel = hotelnames.iloc[k]
  
            hoteldf = gbhotel.get_group(hotel)
            
            #for each hotel, generate a new column and the proportion of each rating number
            for m in range(1, 6):
                reviewinfo.loc[hotel, m] = hoteldf.loc[hoteldf['reviews_rating'] == m, \
                                             'reviews_rating'].count()/hoteldf['reviews_rating'].count()        
            
            
             
    reviewinfo = reviewinfo.reset_index()       
             
    return reviewinfo



def reviewsRatingsPlot(reviewinfo, newcwd):
    '''For each of the hotels in the selected cities, draw a plot, which visualizes the number \
    of reviews as a coordinate on the x axis and the average rating, as a coordinate on the y axis.'''
    
    #create color list for later index
    colors = ['b', 'm', 'r', 'c']
    
    #drop duplicates and make it into a list
    selectedCities = reviewinfo[cityname].drop_duplicates().tolist() 

    for i in range(len(selectedCities)):
        cvalue = colors[i] #assign it based on city
        
        #select rows from reviewinfo corresponding to city
        dataForCityDF = reviewinfo.loc[reviewinfo[cityname] == selectedCities[i]]
        
        hotellst = dataForCityDF[hotelname].tolist()
        
        #draw the plot
        plt.plot(dataForCityDF['reviews_text'], dataForCityDF['reviews_rating'], 'o', \
                 color = cvalue, label = selectedCities[i])
        
        #add annotations
        for j in range(len(hotellst)):
              
            xpos = dataForCityDF.loc[dataForCityDF[hotelname] == hotellst[j],'reviews_text'] + 1
            ypos = dataForCityDF.loc[dataForCityDF[hotelname] == hotellst[j],'reviews_rating'] + 0.1
            
            plt.annotate(hotellst[j], (xpos, ypos))
    
    #adjust the format
    plt.legend()
    plt.xticks(np.arange(0, 250, 50))
    plt.ylim(0, 6)
    plt.title('Hotel ratings and number of reviews.')
    plt.xlabel('Number of reviews')
    plt.ylabel('Average of rating')
    
    plt.savefig(newcwd + '/plot1.jpg')
    plt.show()



def ratingPercentageBarchart(reviewinfo, newcwd):
    '''this function generates 3 barcharts for three of the top-rated hotels. Each barchart\
    showing what percentage of all reviews have the specific rating (1 through 5). This \
    percentage is computed by calculating the total number of reviews with the rating and \
    dividing it by the total number of reviews for the hotel.'''
    
    #get the hotels with top 3 highest average rating scores
    hotelratingdf = reviewinfo.iloc[0:3]
    hotelratingdf.set_index(hotelname, inplace = True)

    #get hotel names and convert hotel names into a list
    hotellst = list(hotelratingdf.index.values)
    
    for i in range(len(hotellst)):
        #get the dataframe of this specific hotel
        hoteldf = hotelratingdf.loc[hotelratingdf.index == hotellst[i]]
        
        reviewCount = str(hoteldf.loc[hotellst[i],'reviews_text'])
        
        #generate the titlename for this barchart
        titlename = str('Percentage of reviews with ratings 1 - 5 out of ' + reviewCount + ' reviews' + '\nfor ' + \
                  hotellst[i] + ' in ' + hoteldf.loc[hotellst[i], cityname] + ', ' + hoteldf.loc[hotellst[i],statename])

        #get the rating numbers to create the barchart
        ratingNum = hoteldf.iloc[:, 4:] * 100
        
        #create the barchart
        plt.bar(list(ratingNum.columns), ratingNum.loc[hotellst[i]], color = 'm', align = 'edge')
        
        #add text on the top of each bar
        for x in range(len(list(ratingNum.columns))):
            plt.text(list(ratingNum.columns)[x], ratingNum.loc[hotellst[i]][x + 1], \
                     "{:.1f}%".format(ratingNum.loc[hotellst[i]][ x + 1]), va='bottom')
         
        #adjust the format   
        plt.ylim(1, 100)
        plt.xlabel('Rating value(1-5)')
        plt.ylabel('% of reviews with rating')
        plt.title(titlename)
        
        
        plt.savefig(newcwd + '/barchart%s.jpg'%(i + 1))
        plt.show()
    


    
def main():
    '''Created by Joann on Dec 4, 2019.
    This program creates a plot showing mean ratings and number of reviews for a selection \
    of hotels in a chosen state, and three barcharts that shows percentage of reviews for \
    each of the top three rating hotels.'''
    
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', 1000) 
    pd.set_option('display.max_rows', 1000)
    
    subfolder, hotelfile, hotelreviewfile = input('Please enter names of the subfolder and files: ').strip().split()
    #change the working directory into the input subfolder
    newcwd = os.path.join(os.getcwd(), subfolder)
    os.chdir(newcwd)
    
    #get the hotel and hotel review dataframe
    hotelst = pd.read_csv(hotelfile)
    reviewt = pd.read_csv(hotelreviewfile)
         
    #get the state name and store them in a list
    statelst = hotelst[statename].unique().tolist()
    
    #get the state name
    stateinput = input('\nPlease enter state, e.g. MA: ')
    
    #ask the state name again if the previous input is not in the dataframe
    while stateinput not in statelst:
        print('We have no data on hotels in', stateinput)
        stateinput = input('Please enter state, e.g. MA:')
    
    #get the cities of that input state and store them in a list
    cities = pickStateAndCities(stateinput, hotelst)
    
    #print out the cities inside the designated state
    citieslen = [len(i) for i in cities]
    maxcitieslen = max(citieslen)
    for i in range(len(cities)):
        print(i+1, '   ', cities[i].rjust(maxcitieslen))
        
    '''for invalid input'''
    inputcitylength = False
    
    while not inputcitylength:
        #get the user input city numbers and put them in a list
        cityNumlst = input('\nSelect cities from above list by entering up to four indices on the same line: ').strip().split()
        citylstlen = len(cities)
    
        if int(max(cityNumlst)) > citylstlen:
            print('Selection must range from 1 to', str(citylstlen))
    
        elif len(cityNumlst) > 4:
            print('You selected', len(cityNumlst), 'items, must select up to four')
            
        else:
            inputcitylength = True
    
    #display the selected cities
    print('\nYou have selected the following cities:')
    print(cityname.rjust(max(citieslen) + 4))
    
    inputcitylst = []
    for num in cityNumlst:
        print(num, '  ', cities[eval(num) - 1].rjust(max(citieslen)))
        inputcitylst.append(cities[eval(num) - 1])
     
    #Identify all hotels that are located in the selected city(s)
    print('\nDisplaying rating information for the following hotels: ')
    ratinginfo = displayRatingInfo(stateinput, hotelst, inputcitylst)

    print(ratinginfo)
    
    print('\nExiting...')    
    
    #generate and save plots
    reviewinfo = selectHotelReviews(reviewt, ratinginfo)
    reviewsRatingsPlot(reviewinfo, newcwd)
    ratingPercentageBarchart(reviewinfo, newcwd)
    
main()


