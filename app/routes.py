from flask import render_template, request, redirect, url_for
from app import app
import requests
import json
import ipinfo
import polyline


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/sos', methods=['POST', 'GET'])
def sos():
    data = []
    with open('data.json') as f:
        data = json.load(f)
    return render_template('sos.html', data=data)


@app.route('/personal')
def personal_info():
    return render_template('personal_info.html')


@app.route('/visualise', methods=['GET', 'POST'])
def map_visualise():
    if request.method == "GET":
        return render_template('visualise.html', places={"req_places": {}, "nearby_fitness": {},
                                                         "nearby_health": {}, "nearby_nutrition": {}})
    elif request.method == "POST":
        health_facet = ["pharmacy", "hospital"]
        fitness_facet = ["gym"]
        nutrition_facet = ["ration", "supermarket"]

        data = request.form.to_dict()
        url = 'http://apis.mapmyindia.com/advancedmaps/v1/e1tna7j5crfpczjmdhffmzpugyy9pr44/geo_code?'
        PARAMS_GEOCODE = {"addr": data['search']}
        resp = requests.get(url=url, params=PARAMS_GEOCODE)
        data = resp.json()
        places_list = data['results']
        #print(json.dumps(places_list, indent=4))
        req_places = []
        for items in places_list:
            if "Bengaluru;Bangalore" in items['city']:
                req_places.append([items['street'], items['lat'], items['lng']])
                nearby_fitness = nearby_info(fitness_facet, items['lat'], items['lng'])
                nearby_health = nearby_info(health_facet, items['lat'], items['lng'])
                nearby_nutrition = nearby_info(nutrition_facet, items['lat'], items['lng'])
                break
        try:
            nearby_fitness
        except UnboundLocalError:
            nearby_fitness = {}
        try:
            nearby_health
        except UnboundLocalError:
            nearby_health = {}
        try:
            nearby_nutrition
        except UnboundLocalError:
            nearby_nutrition = {}
        places = {"req_places": req_places, "nearby_fitness": nearby_fitness,
                  "nearby_health": nearby_health, "nearby_nutrition": nearby_nutrition}
        return render_template('visualise.html', places=places)


@app.route('/print_info', methods=['POST', 'GET'])
def print_info():
    if request.method == 'POST':
        data = request.form
        with open('data.json', 'w') as file:
            x = {}
            for key, value in data.items():
                x[key] = value
                # print(value)
            json.dump(x, file)
        # return render_template('print_info.html', print_info = request.form)
        return redirect(url_for('index'))


@app.route('/rating', methods=['GET', 'POST'])
def rating():
    nearby_data = nearby_info()
    if request.method == "POST":
        sum_ = 0
        avg_dict = {}
        form_dict = request.form.to_dict()
        for key in nearby_data['nearby_places']:
            avg = 0
            sum_ = 0
            sum_ += int(form_dict[key + '1'])
            sum_ += int(form_dict[key + '2'])
            sum_ += int(form_dict[key + '3'])
            sum_ += int(form_dict[key + '4'])
            sum_ += int(form_dict[key + '0'])
            avg += sum_ / 5
            avg_dict['Rating for ' + key] = avg
        nearby_data['average'] = avg_dict
        return render_template('rating.html', title='MSHack', nearby_data=nearby_data)
    else:
        return render_template('rating.html', title='MSHack', nearby_data=nearby_data)


def nearby_info(keyword=["hospital"], lat=None, lng=None):
    # get current location public ip
    ip_addr = str(requests.get('http://ip.42.pl/raw').text)

    if lat == None and lng == None:
        access_token = '346f1e66e85358'
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails(ip_addr)
        lat_long = details.loc
    else:
        lat_long = lat + "," + lng
    # separate lat and long
    curr_lat, curr_long = lat_long.split(",")
    # get nearby location json
    TOKEN = 'c7e57e36-43f9-438f-a2b7-0f3096a03710'
    HEADERS = {'Authorization': 'Bearer {}'.format(TOKEN)}
    if len(keyword) > 1:
        PARAMS_NEARBY = {"keywords": keyword[0] + ";" + keyword[1], "refLocation": str(lat_long)}
    else:
        PARAMS_NEARBY = {"keywords": keyword[0], "refLocation": str(lat_long)}
    url = 'https://atlas.mapmyindia.com/api/places/nearby/json?'
    with requests.Session() as s:
        s.headers.update(HEADERS)
        resp = s.get(url=url, params=PARAMS_NEARBY)
        data = resp.json()
    nearby_list_cords = []
    nearby_places = []
    for loc in data['suggestedLocations']:
        lat = loc['entryLatitude']
        lon = loc['entryLongitude']
        place_name = loc['placeName']
        nearby_places.append(place_name)
        temp = [place_name, str(lat), str(lon)]
        nearby_list_cords.append(temp)

    if len(keyword) > 1 and keyword[0] != "hospital":
        return nearby_list_cords
    else:
        # get route to nearby location json
        license_key = "awgwtfu8vtq5cv3zkqat1o7m9b15v3a6"
        PARAMS_ROUTE = {"start": lat_long,
                        "destination": nearby_list_cords[0][1] + "," + nearby_list_cords[0][2], "alternatives": True}
        resp_route = requests.get(
            url="https://apis.mapmyindia.com/advancedmaps/v1/" + license_key + "/route?", params=PARAMS_ROUTE)
        route_data = resp_route.json()
        nearest_route_points_list = polyline.decode(
            route_data['results']['trips'][0]['pts'])
        # print(route_data['results']['trips'][0]['pts')
        nearest_route_points_list_list = []
        for each in nearest_route_points_list:
            nearest_route_points_list_list.append(
                [str(each[0] / 10.), str(each[1] / 10.)])

        return {"nearby_list": nearby_list_cords, "nearby_places": nearby_places, "curr_lat": curr_lat, "curr_long": curr_long, "nearest_route_points_list_list": nearest_route_points_list_list}
