
from django import forms

geo_locations= [
    ('zips', 'Zips'),
    ('regions', 'Regions'),
    ('cities', 'Cities'),
    ('countries', 'Countries'),
    ('geo_markets', 'Geo_markets'),
    ]

class adset(forms.Form):
    first_name= forms.CharField(max_length=100)
    last_name= forms.CharField(max_length=100)
    email= forms.EmailField()
    age= forms.IntegerField()
    favorite_fruit= forms.CharField(label='Select geo location sub type', widget=forms.Select(choices=geo_locations))

