
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import Http404
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.admin.views.decorators import staff_member_required

import json
import pandas as pd
import  requests

pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 100)
from .forms import  adset

# Create your views here.


@staff_member_required
def home_view(request, *args, **kwargs):
    return render(request,"adset/home.html",{ } )
    #return JsonResponse({'foo':'bar'})

@staff_member_required
def contact_view(request, *args,**kwargs):
    return render(request,"adset/contact.html",{})

@staff_member_required
def update_view(request, *args,**kwargs):


    target_ids = get_all_local_target_ids
    del_msg = None
    load_msg = None


    if request.method == 'POST':
        view_local_data = request.POST.get("view", None)
        delete_id = request.POST.get("delete", None)
        load_data = request.POST.get("load", None)

        if load_data:
            #print("Load data= ", load_data)

            my_data = ""
            r = requests.get('https://app.wordstream.com/services/v1/wordstream/interview_data')
            my_data = r.json()
            # print(data)
           # with open("adset/Srini_single_source.json","r+") as fh:
             #   my_data = json.load(fh)
                
            with open('adset/local_data.json', 'w') as outfile:
                json.dump(my_data, outfile, indent=4)
            load_msg = "Loaded data successfully from Source"

        if delete_id:
            delete_id = request.POST.get("target_ids", None)

            delete_target_by_id(delete_id)
            if not delete_id == "":
                del_msg = "Deleted data successfully with target id " + delete_id
                #print(del_msg)

        if  view_local_data:

             #print("viewing json data")
             with open("adset/local_data.json", 'r') as f:
                     json_data = json.load(f)

             json_pretty = json.dumps(json_data, sort_keys=True, indent=4)
             
             return HttpResponse(json_pretty,content_type="application/json")
             
             return render(request, "json_output.html", context)
            #return HttpResponse(json.dumps(data_dict))
            #return render(request,'book.html', {'js': json.loads(js)})

        if 'subtype_to_delete' in request.POST:
            delete_type = request.POST.get("subtypedelete", None)

            #print("Subtype to delete =", delete_type)
            subtypeToDelete = "targeting.geo_locations." + delete_type

            #Delete subtype

            with open("adset/local_data.json", "r+") as fh:
                my_input = json.load(fh)

            my_data = my_input['data']
            final_modified_subtypes = []

            for d in my_data:
                for k, v in d.items():
                    if isinstance(v, dict):
                        if v.get('geo_locations'):
                            #print("Calling deletesubtype")
                            deleted_dict = (delete_subtype(d, subtypeToDelete.split(".")))
                            final_modified_subtypes.append(deleted_dict)
                        else:
                            #print("Not present for id=",d['id'])
                            continue

            out_data = {}
            out_data['data'] = []
            out_data['data'].extend(final_modified_subtypes)

            with open('adset/local_data.json', 'w') as outfile:
                json.dump(out_data, outfile, indent=4)

            if not delete_type == "":
                del_msg = "Deleted subtype " + delete_type + " from local data"

    context = {
            'del_msg' : del_msg,
            'load_msg': load_msg,
            'target_ids': target_ids,
    }

    #print(context)

    return render(request,"adset/update.html",context)


def delete_subtype(data, keyList):
    if len(keyList) > 1:
        data[keyList[0]] = delete_subtype(data[keyList[0]], keyList[1:])
    else:
        if keyList[0] in data:
            del data[keyList[0]]
        else:
            # print("Key not present",keyList[0])
            pass
    return data

@staff_member_required
def geo_locations_view(request, *args,**kwargs):

    subtype = request.POST.get("geo_subtypes", None)

    freq_value = request.POST.get("top_frequent", None)

    #print("SUBTYPE =",subtype)
    #print("TOP FREQ =",freq_value)


    #subtype ="cities"
    my_dict = {}
    df =""
    context ={}

    if subtype == None or freq_value== None:
        context = {
            'msg': 'No input selection'
        }
        return render(request, "adset/geo_locations.html", context)

    df = my_dataframe(subtype,freq_value)
    #print(df)
    #html = df.to_html()
    #print(html)

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame

    if not df.empty:

        #df.to_html(open('adset/geo_locations.html', 'a+'))
        my_dict = df.to_dict(orient='list')
        #my_dict = df.to_dict()
        #print(my_dict)


    # And render it!
    #return render(request, "adset/geo_locations.html", context)

    context = {
       'data':my_dict.items(),
        'subtype': subtype,
        'freq_value': freq_value
    }


    return render(request,"adset/geo_locations.html",context)
    #return render(request,"adset/geo_locations.html",{'data':(my_dict.items()) ,'subtype': subtype})
    #return render(request,"adset/geo_locations.html",{'data':df.to_html()})
   # return render(request,"adset/geo_locations.html",{ "table": table})


def send_selected_region(request, *args,**kwargs):
     selected_region = request.POST.get("geo_subtypes", None)
     return selected_region

def my_dataframe(stype,f_value):

        subtype = stype
        freq_value = f_value
        class geo_locations(object):
            def __init__(self, *args):
                self.my_id = args[0];
                self.my_data = args[1];
                self.regions_list = ""
                self.zips_list = ""
                self.cities_list = ""
                self.countries_list = ""
                self.geo_markets_list = ""
                if 'regions' in self.my_data:
                    #print("printing regions list")
                    #print(self.regions_list)
                    #print(type(self.regions_list))
                    self.regions_list =  self.my_data.get("regions")
                    #print(regions_list[0]["name"])
                if 'zips' in self.my_data:
                    self.zips_list = self.my_data.get("zips")
                if 'cities' in self.my_data:
                    self.cities_list = self.my_data.get("cities")
                if 'countries' in self.my_data:
                    self.countries_list = self.my_data.get("countries")
                if 'geo_markets' in self.my_data:
                    self.geo_markets_list = self.my_data.get("geo_markets")
            def get_id(self):
                return self.my_id
            def get_zips(self):
                return self.zips_list
            def get_regions(self):
                return self.regions_list
            def get_cities(self):
                return self.cities_list
            def get_countries(self):
                return self.countries_list
            def get_geo_markets(self):
                return self.geo_markets_list
        ####################################################################################
        # Start of main program
        #my_file = "Srini_single.json"
        my_file = "adset/local_data.json"
        with open(my_file,"r+") as fh:
            #data = json.load(fh, object_pairs_hook=OrderedDict)
            my_input = json.load(fh)
            #print(data)
        my_data = my_input['data']
        final_zips = []
        final_regions = []
        final_cities =[]
        final_countries = []
        final_geo_markets = []
        # Iterate through individual elements
        for data in my_data:
            #print("Data=",data)
            #print(type(data))
            my_id = data['id']
            #print ("MYid =",my_id)
            req_data = {}
            for k, v in data.items():
                #print("Iterating items")
                #print(type(v))
                if isinstance(v, dict):
                    req_data = v.get('geo_locations')
                    #print("REQDATA=",req_data)
            if(req_data == None):
                #print("Geo Locations not present for the id = ",my_id)
                continue
            geo_obj = geo_locations(my_id,req_data)
            #print("id =",geo_obj.my_id)
            #print("regions=",geo_obj.get_regions())
            if (geo_obj.get_zips()):
                #print("id = {0}, zips = {1}".format(my_id,geo_obj.get_zips()))
                #print("zips = ",geo_obj.get_zips())
                final_zips.extend(geo_obj.get_zips())
            if(geo_obj.get_regions()):
                #print("regions=",geo_obj.get_regions())
                final_regions.extend(geo_obj.get_regions())
            if (geo_obj.get_cities()):
                #print("cities=",geo_obj.get_cities())
                final_cities.extend(geo_obj.get_cities())
            if (geo_obj.get_countries()):
                #print("countries=",geo_obj.get_countries())
                final_countries.extend(geo_obj.get_countries())
            if (geo_obj.get_geo_markets()):
                #print("geomarkets=",geo_obj.get_geo_markets())
                final_geo_markets.extend(geo_obj.get_geo_markets())

        # Get mapping for zips to regions
        def find_name_by_zip(zip):
            myzip = zip
            for regions in final_regions:
                if (str(myzip) in regions.values()):
                    return  str(myzip) +  " (mapping region => " + regions['name'] + ")"

        #print(final_regions)
        #print(final_zips)
        #print(final_geo_markets)
        #print(final_countries)

        if(freq_value):
            head_value = int(freq_value)
        else:
            head_value = 0

        regions_df = pd.DataFrame(final_regions)
        zips_df = pd.DataFrame(final_zips)
        cities_df = pd.DataFrame(final_cities)
        countries_df = pd.DataFrame(final_countries,columns=['country'])
        geo_markets_df = pd.DataFrame(final_geo_markets)

        if not regions_df.empty:
            regions_df.sort_values('name', inplace= True)
            top_regions = regions_df.groupby('name').size().sort_values(ascending=False).reset_index().head(head_value)
            top_regions.columns = ['Geo Locations by Regions', 'Count']
            top_regions.index += 1
            # top_regions.to_html(open('my_file.html', 'w'))

            if subtype == "regions":
                # print(top_regions)
                return top_regions

        if not zips_df.empty:
            zips_df.sort_values('region_id', inplace= True)

            top_zips = zips_df.groupby('region_id').size().sort_values(ascending=False).reset_index().head(head_value)
            top_zips.columns = ['Geo Locations by Zips', 'Count']
            top_zips.index += 1
            # top_zips.to_html(open('my_file.html', 'a+'))


            my_dict = {find_name_by_zip(row[0]): row[1] for row in top_zips.values}
            modified_zips_df = pd.DataFrame(list(my_dict.items()), columns=['Geo Locations by Zips', 'Count'])
            #print(modified_zips_df)

            if subtype == "zips":
                # print(top_regions)
                return modified_zips_df

        if not cities_df.empty:
            cities_df.sort_values('region', inplace= True)
            top_cities = cities_df.groupby('region').size().sort_values(ascending=False).reset_index().head(head_value)
            top_cities.columns = ['Geo Locations by Cities', 'Count']
            top_cities.index += 1
            # top_cities.to_html(open('my_file.html', 'a+'))

            if subtype == "cities":
                # print(top_regions)
                return top_cities

        if not countries_df.empty:
            countries_df.sort_values('country',inplace= True)
            top_countries = countries_df.groupby('country').size().sort_values(ascending=False).reset_index().head(head_value)
            top_countries.columns = ['Geo Locations by Countries', 'Count']
            top_countries.index += 1
            # top_countries.to_html(open('my_file.html', 'a+'))

            if subtype == "countries":
                # print(top_regions)
                return top_countries

        if not geo_markets_df.empty:
            geo_markets_df.sort_values('country', inplace= True)
            top_geo_markets = geo_markets_df.groupby('country').size().sort_values(ascending=False).reset_index().head(
                head_value)
            top_geo_markets.columns = ['Geo Locations by Geo markets', 'Count']
            top_geo_markets.index += 1
            # top_geo_markets.to_html(open('my_file.html', 'a+'))

            if subtype == "geo_markets":
                # print(top_regions)
                return top_geo_markets


def delete_target_by_id(delete_id):
    with open("adset/local_data.json", "r+") as fh:
        my_input = json.load(fh)
        # print(data)
    my_data = my_input['data']
    final_targets = []

    # Iterate through individual elements

    for data in my_data:

        #print("Data=", data)
        #print(type(data))

        my_id = data['id']
        #print("MYid =", my_id)
        req_data = {}
        if data['id'] == delete_id:
            #print("Deleting data with id=", my_id)
            continue
        final_targets.append(data)
        #print("Final targets = ", final_targets)

    #### write final json file
    out_data = {}
    out_data['data'] = []
    out_data['data'].extend(final_targets)

    with open('adset/local_data.json', 'w') as outfile:
        json.dump(out_data, outfile, indent=4)

def get_all_local_target_ids():
    with open("adset/local_data.json", "r+") as fh:
        my_input = json.load(fh)
    my_data = my_input['data']
    target_ids = []

    # Iterate through individual elements

    for data in my_data:
        #print("Data=", data)
        my_id = data['id']
        #print("MYid =", my_id)

        target_ids.append(my_id)

    #print("target_ids = ", target_ids)
    return  target_ids
