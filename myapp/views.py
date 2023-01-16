from django.shortcuts import render
import pandas as pd

# load the dengue dataset
dengueds = pd.read_csv('myapp/doh-epi-dengue-data-2016-2021.csv')

# drop the first row in the dataset because it is not necessary
dengueds = dengueds.drop(dengueds.index[0])
# drop all null rows
dengueds = dengueds.dropna()
# convert date column to datetime datatype
dengueds['date'] = pd.to_datetime(dengueds['date']).dt.date
# convert cases and deaths column to int datatype
dengueds['cases'] = dengueds['cases'].astype('int32')
dengueds['deaths'] = dengueds['deaths'].astype('int32')

# convert loc and region column to category datatype
dengueds['loc'] = dengueds['loc'].astype('category')
dengueds['Region'] = dengueds['Region'].astype('category')
# this will remove and merge all duplicates of loc, date, and region
dengueds = dengueds.groupby(['loc', 'date', 'Region']).agg({'cases': 'sum', 'deaths': 'sum'}).reset_index()

# group by date
denguedsDate = dengueds.groupby('date').agg({'cases': 'sum', 'deaths': 'sum'}).reset_index()

# sort values by date
dengueds = dengueds.sort_values(by = 'date')


# make dengue region name unique
dengueRegions = dengueds['Region']
dengueRegions = dengueRegions.unique()

# make dengue location names unique
dengueLocation = dengueds['loc']
dengueLocation = dengueLocation.unique()



#project 2
#ph cities dataset
ph = pd.read_csv('myapp/ph.csv')

#drop all null rows
ph = ph.dropna()

#convert the latitude and longitude to type float
ph['lat'] = ph['lat'].astype('float')
ph['lng'] = ph['lng'].astype('float')
#convert city to type category
ph['admin_name'] = ph['admin_name'].astype('category')
#convert population to type int
ph['population'] = ph['population'].astype('int64')


# Create your views here.

def index(request):
    date, cases, deaths = getDengueCasesByDate()
    region_names, rcases, rdeaths = getDengueCasesByRegion()
    loc_names, lcases, ldeaths = getDengueCasesByLoc()

    
    context = {'date': date, 'cases': cases, 'deaths': deaths, 'region_names': region_names, 'rcases': rcases, 'rdeaths': rdeaths, 'loc_names': loc_names, 'lcases': lcases, 'ldeaths': ldeaths}

    #casesbydate = {'dates': date, 'cases': cases, 'deaths': deaths, 'region': region_names, 'rcases': rcases, 'rdeaths': rdeaths}

    #return render(request, "myapp/index.html", casesbydate)
    return render(request, "myapp/index.html", context)
def project1(request):
    date, cases, deaths = getDengueCasesByDate()
    region_names, rcases, rdeaths = getDengueCasesByRegion()
    loc_names, lcases, ldeaths = getDengueCasesByLoc()

    
    context = {'date': date, 'cases': cases, 'deaths': deaths, 'region_names': region_names, 'rcases': rcases, 'rdeaths': rdeaths, 'loc_names': loc_names, 'lcases': lcases, 'ldeaths': ldeaths}

    #casesbydate = {'dates': date, 'cases': cases, 'deaths': deaths, 'region': region_names, 'rcases': rcases, 'rdeaths': rdeaths}

    #return render(request, "myapp/index.html", casesbydate)
    return render(request, "myapp/project1.html", context)
def project2(request):
    phcityData = getPopulationOfCities()
    context = {'phcityData': phcityData}
    return render(request, "myapp/project2.html", context)
def getPopulationOfCities():
    res = []
    for i in ph.index:
        res.append({'lng': ph['lng'][i], 'lat': ph['lat'][i], 'population': ph['population'][i], 'province': ph['admin_name'][i]})
    return res
def getDengueCasesByDate():
    date = []
    cases = []
    deaths = []

    for i in denguedsDate.index:
        date.append(str(denguedsDate['date'][i]))
        cases.append(denguedsDate['cases'][i])
        deaths.append(denguedsDate['deaths'][i])

    return date, cases, deaths

def getDengueCasesByRegion():
    regcases = []
    regdeaths = []
    region_names = []

    for i in dengueRegions:
        regcases.append(dengueds.loc[dengueds['Region'] == i]['cases'].sum())
        regdeaths.append(dengueds.loc[dengueds['Region'] == i]['deaths'].sum())
        region_names.append(i)

    return region_names, regcases, regdeaths

def getDengueCasesByLoc():
    loccases = []
    locdeaths = []
    loc_names = []
    for i in dengueLocation:
        loccases.append(dengueds.loc[dengueds['loc'] == i]['cases'].sum())
        locdeaths.append(dengueds.loc[dengueds['loc'] == i]['deaths'].sum())
        loc_names.append(i)
    return loc_names, loccases, locdeaths
