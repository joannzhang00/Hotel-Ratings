import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict
from random import choice
import os
import numpy as np
color = ['pink','fuchsia','indigo','b','gold','cyan','coral','lightgreen']
plt.style.use('seaborn-whitegrid')
def pickStateAndCities(state,Hlistdir):
    SandC = pd.read_csv(Hlistdir)
    City = SandC.groupby('province').get_group(state).city.drop_duplicates().sort_values().reset_index(drop=True)
    City.index+=1
    return City

def selectHotelReviews(Scity,Hrdir):
    pd.set_option('display.max_columns', 100)
    Hre = pd.read_csv(Hrdir)
    totlreviews=pd.DataFrame()
    totlhotel = pd.DataFrame()
    for i in Scity:
        hotel= Hre.groupby('city').get_group(i).loc[:,['name','city','province','reviews_rating']]
        totlreviews = totlreviews.append(hotel)
        hotel1 = hotel.loc[:,['name','city','province']].drop_duplicates()
        totlhotel = totlhotel.append(hotel1)
    return totlreviews,totlhotel

def reviewsRatingsPlot(totlreviews,totlhotel,dir):
    totlhotel = totlhotel.reset_index(drop=True)
    totlhotel.set_index('name', inplace=True)
    avg = totlreviews.groupby('name').aggregate({'reviews_rating': 'mean'})
    num = totlreviews.groupby('name').aggregate({'reviews_rating': 'count'})
    num.columns = ['num']
    avg.columns = ['avg']
    totlhotel['avg'] = avg['avg']
    totlhotel['num'] = num['num']
    #print(totlhotel['city'])
    for n in totlhotel['city'].drop_duplicates():
        b = totlhotel[totlhotel['city']==n]
        b.insert(0,'color',choice(color))
        #print(b)
        for i in b.index:
            plt.plot(b.loc[i,'num'],b.loc[i,'avg'],'o',label=b.loc[i,'city'],color=b.loc[i,'color'])
            plt.text(b.loc[i,'num'],b.loc[i,'avg'],i,va='bottom')
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.xlim(0,250)
    plt.ylim(0,6)
    plt.title('Hotel ratings and number of reviews')
    plt.ylabel('Average rating')
    plt.xlabel('Number of reviews')
    plt.grid(False)
    plt.savefig(dir + '\\Hotel ratings and number of reviews.png')
    plt.show()

def ratingPercentageBarchart(hotelone,dir):
    pd.set_option('display.max_rows', 1000)
    hotelafter2 = pd.DataFrame(np.zeros(5),index=[1,2,3,4,5])
    hotelafter2.index.name = 'reviews_rating'
    hotelafter2.columns = ['reviews_rating']
    hotelafter = hotelone.groupby('reviews_rating').aggregate({'reviews_rating': 'count'})
    hotelafter['reviews_rating']=hotelafter['reviews_rating']/hotelone['name'].count()
    Hfinal = hotelafter2+hotelafter
    Hfinal = Hfinal.fillna(0)
    Hfinal.columns = ['Percentage']
    #print(Hfinal.index)
    for i in Hfinal.index:
        plt.bar(i,Hfinal.loc[i].values,color="fuchsia", align="edge")
        plt.text(i,Hfinal.loc[i].values, '{:.1f}%'.format(Hfinal.loc[i].values[0]*100),va='bottom')
    plt.xlim(0,6)
    #plt.ylim(0,1)
    plt.ylabel('"%"of reviews with rating')
    plt.xlabel('Rating value(1-5)')
    plt.yticks(np.arange(0,1.2,0.2),np.arange(0,120,20))
    plt.title("Percentage of reviews with ratings 1-5 out of %d reviews for %s %s" % (hotelone['name'].count(),hotelone['name'].drop_duplicates().values[0],hotelone['province'].drop_duplicates().values[0]))
    plt.grid(False)
    plt.savefig(dir+"\\%s.png"%(hotelone['name'].drop_duplicates().values[0]))
    plt.show()

def main():
    inplst = input("Please enter names of the subfolder and files :")
    inplst = inplst.split()
    folder = inplst[0]
    Hlistn = inplst[1]
    Hrn = inplst[2]
    cwd = os.getcwd()
    dir = os.path.join(cwd, folder)
    Hlistdir = os.path.join(dir,Hlistn)
    Hrdir = os.path.join(dir,Hrn)
    state = input("Please enter state, e.g. MA:")
    City = pickStateAndCities(state,Hlistdir)
    print(City)
    Citylst = input("Select cities from above list by entering up to four indices on the same line:")
    Citylst = Citylst.split()
    CitylstF = [int(i) for i in Citylst]
    chocity = City[CitylstF]
    #chocity.columns=['city']
    print("You have selected the following cities:")
    print(pd.DataFrame(chocity))
    totlreviews, totlhotel = selectHotelReviews(chocity,Hrdir)
    print("Displaying rating information for the following hotels:")
    print(totlhotel.reset_index(drop=True))
    reviewsRatingsPlot(totlreviews, totlhotel,dir)
    print("Exiting")
    for i in totlreviews['name'].drop_duplicates():
        hotelone = totlreviews.groupby('name').get_group(i)
        ratingPercentageBarchart(hotelone,dir)
#data hotels.csv hotelreviews.csv
main()
