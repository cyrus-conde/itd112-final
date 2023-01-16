from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse, JsonResponse
from json import dumps

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
dengueds = dengueds.drop_duplicates(keep='first')

# sort values by date
dengueds = dengueds.sort_values(by = 'date')

# Dropping the outliers of cases and deaths using Standard Deviation
dengueds_upper_cases = dengueds['cases'].mean() + 3 * dengueds['cases'].std ()
dengueds_lower_cases = dengueds['cases'].mean() - 3 * dengueds['cases'].std () 
dengueds = dengueds[(dengueds['cases'] < dengueds_upper_cases) & (dengueds['cases'] > dengueds_lower_cases)]

dengueds_upper_deaths = dengueds['deaths'].mean() + 3 * dengueds['deaths'].std ()
dengueds_lower_deaths = dengueds['deaths'].mean() - 3 * dengueds['deaths'].std () 
dengueds = dengueds[(dengueds['deaths'] < dengueds_upper_deaths) & (dengueds['deaths'] > dengueds_lower_deaths)]


# group by date, merge also the duplicates of date (way labot loc and region)
denguedsDate = dengueds.groupby('date').agg({'cases': 'sum', 'deaths': 'sum'}).reset_index()


# make dengue region name unique
dengueRegions = dengueds['Region']
dengueRegions = dengueRegions.unique()

# make dengue location names unique
dengueLocation = dengueds['loc']
dengueLocation = dengueLocation.unique()

# get month_year
denguedsNewDate = pd.to_datetime(dengueds['date'])
dengueds['month_year'] = denguedsNewDate.dt.strftime('%Y-%m')

dengueds['year'] = denguedsNewDate.dt.strftime('%Y')



#project 2
#ph cities dataset
ph = pd.read_csv('myapp/ph.csv')


#drop all null rows in population, city, lat, lng only
ph = ph.dropna(subset=['population','city','lat','lng'])

#convert the latitude and longitude to type float
ph['lat'] = ph['lat'].astype('float')
ph['lng'] = ph['lng'].astype('float')
#convert city to type category
ph['admin_name'] = ph['admin_name'].astype('category')
#convert population to type int
ph['population'] = ph['population'].astype('int64')
# Dropping the outliers of cases and deaths using Standard Deviation
ph_upper_cases = ph['population'].mean() + 3 * ph['population'].std ()
ph_lower_cases = ph['population'].mean() - 3 * ph['population'].std () 
ph = ph[(ph['population'] < ph_upper_cases) & (ph['population'] > ph_lower_cases)]


# Create your views here.

def index(request):
    return render(request, "myapp/index.html")

def project1(request):
    date, cases, deaths = getDengueCasesByDate()
    region_names, rcases, rdeaths = getDengueCasesByRegion()
    loc_names, lcases, ldeaths = getDengueCasesByLoc()

    
    context = {'date': date, 'cases': cases, 'deaths': deaths, 'region_names': region_names, 'rcases': rcases, 'rdeaths': rdeaths, 'loc_names': loc_names, 'lcases': lcases, 'ldeaths': ldeaths}

    #casesbydate = {'dates': date, 'cases': cases, 'deaths': deaths, 'region': region_names, 'rcases': rcases, 'rdeaths': rdeaths}

    #return render(request, "myapp/index.html", casesbydate)
    return render(request, "myapp/project1.html", context)

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

def getDateValuesData(request):
    if request.method == "GET":
        
        cname = request.GET['cname']
        if cname == "MonthYear":
            
            denguedsNewDate = dengueds.groupby('month_year').agg({'cases': 'sum', 'deaths': 'sum'}).reset_index()

            date = []
            cases = []
            deaths = []
            subtitle = "The monthly data visualization of the dengue dataset clearly illustrates the trend of higher reported cases compared to deaths, with a notable decrease in cases during the mid of 2020."
            for i in denguedsNewDate.index:
                date.append(str(denguedsNewDate['month_year'][i]))
                cases.append(str(denguedsNewDate['cases'][i]))
                deaths.append(str(denguedsNewDate['deaths'][i]))
            context = {'new_date' : date, 'cases' : cases, 'deaths': deaths, 'subtitle': subtitle}
            return JsonResponse(context, content_type='application/json')
        elif cname == "Year":
            denguedsNewDate = dengueds.groupby('year').agg({'cases': 'sum', 'deaths': 'sum'}).reset_index()
            subtitle = "The yearly data visualization of the dengue dataset clearly illustrates the trend of higher reported cases compared to deaths, with a notable increase in cases from 2017 to 2019 and a decrease from 2019 to 2021."
            date = []
            cases = []
            deaths = []
            for i in denguedsNewDate.index:
                date.append(str(denguedsNewDate['year'][i]))
                cases.append(str(denguedsNewDate['cases'][i]))
                deaths.append(str(denguedsNewDate['deaths'][i]))
            context = {'new_date' : date, 'cases' : cases, 'deaths': deaths, 'subtitle': subtitle}
            return JsonResponse(context, content_type='application/json')
        elif cname == "Daily":
            date = []
            cases = []
            deaths = []
            subtitle = "The daily data visualization of the dengue dataset clearly illustrates the trend of higher reported cases compared to deaths, with a notable decrease in cases during the mid of 2020."
            for i in denguedsDate.index:
                date.append(str(denguedsDate['date'][i]))
                cases.append(str(denguedsDate['cases'][i]))
                deaths.append(str(denguedsDate['deaths'][i]))

            context = {'new_date' : date, 'cases' : cases, 'deaths': deaths, 'subtitle': subtitle}
            return JsonResponse(context, content_type='application/json')

def getCategoryValues(request):
    if request.method == 'GET':
        cname = request.GET['cname']
        if cname == "City":
            loc_names = []
            for i in dengueLocation:
                loc_names.append(i)
            return HttpResponse(dumps(loc_names), content_type='application/json')
        
            
        elif cname == "Region":
            region_names = []
            
            for i in dengueRegions:
                region_names.append(i)
            return HttpResponse(dumps(region_names), content_type='application/json')
        else:
            return HttpResponse(0)

def getCategoryValuesData(request):
    if request.method == 'GET':
        cname = request.GET['cname']
        if cname == "City":
            vname = request.GET['vname']
            myData = dengueds[dengueds['loc'] == vname]

            date = []
            cases = []
            deaths = []
            subtitle = "The graph displays the incidence of dengue in " + vname + " over a chosen time frame, showcasing the variation in reported cases and deaths."
            for i in myData.index:
                date.append(str(myData['date'][i]))
                cases.append(str(myData['cases'][i]))
                deaths.append(str(myData['deaths'][i]))
            context = {'date' : date, 'cases' : cases, 'deaths': deaths, 'subtitle': subtitle}
            return JsonResponse(context, content_type='application/json')
        elif cname == "Region":
            vname = request.GET['vname']
            myData = dengueds[dengueds['Region'] == vname]
            subtitle = "The graph displays the incidence of dengue in " + vname + " over a chosen time frame, showcasing the variation in reported cases and deaths."
            date = []
            cases = []
            deaths = []

            for i in myData.index:
                date.append(str(myData['date'][i]))
                cases.append(str(myData['cases'][i]))
                deaths.append(str(myData['deaths'][i]))
            context = {'date' : date, 'cases' : cases, 'deaths': deaths, 'subtitle': subtitle}
            return JsonResponse(context, content_type='application/json')


def project2(request):
    phcityData = getPopulationOfCities()
    context = {'phcityData': phcityData}
    return render(request, "myapp/project2.html", context)
    
def getPopulationOfCities():
    res = []
    for i in ph.index:
        res.append({'lng': ph['lng'][i], 'lat': ph['lat'][i], 'population': ph['population'][i], 'province': ph['admin_name'][i]})
    return res







        


