from flask import render_template, request
from app import app
import requests
import json
import ipinfo
import polyline


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/personal', methods=['GET', 'POST'])
def personal_info():
    return render_template('personal_info.html')


@app.route('/visualise', methods=['GET', 'POST'])
def map_visualise():
    return "What a wow"


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


def nearby_info():
    # get current location public ip
    ip_addr = str(requests.get('http://ip.42.pl/raw').text)

    # get latitude and longitude of ip
    access_token = '346f1e66e85358'
    handler = ipinfo.getHandler(access_token)
    details = handler.getDetails(ip_addr)
    lat_long = details.loc
    # separate lat and long
    curr_lat, curr_long = lat_long.split(",")
    lat_long = "12.8311,77.5129"
    # get nearby location json
    TOKEN = '4623d44a-5b8d-40bf-a866-57b48c129aad'
    HEADERS = {'Authorization': 'Bearer {}'.format(TOKEN)}
    PARAMS_NEARBY = {"keywords": "hospital", "refLocation": str(lat_long)}
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
