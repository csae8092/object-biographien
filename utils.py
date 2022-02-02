import jinja2
import json
import os
import pandas as pd
import requests
from slugify import slugify
from io import BytesIO


templateLoader = jinja2.FileSystemLoader(searchpath=".")
templateEnv = jinja2.Environment(loader=templateLoader)
template = templateEnv.get_template('./templates/index.html')

GDRIVE_URL = "https://docs.google.com/spreadsheet/ccc?key=1G5HRtHLrYGJkXj8s72KC6Uatuhy52hjBKFJpXDgQuP8"

def gsheet_to_df():
    url = f"{GDRIVE_URL}&output=csv"
    r = requests.get(url)
    print(r.status_code)
    data = r.content
    df = pd.read_csv(BytesIO(data))
    # df = pd.read_csv('./data_dump.csv')
    return df

# df.to_csv('data_dump.csv', index=False)


def make_index_html(df):
    os.makedirs('./html', exist_ok=True)
    items = []
    template = templateEnv.get_template('./templates/object.html')
    for gr, df in df.groupby('werk'):
        object_id = slugify(gr)
        file_name = f"{object_id}.html"
        data_src = f"data/{object_id}.geojson"
        item = {
            "object_id": object_id.replace('-', '_'),
            "url": file_name,
            "data_src": data_src, 
            "title": gr,
            "stations": []
        }
        for i, row in df.iterrows():
            station = {}
            for x in row.keys():
                station[x] = row[x]
            item['stations'].append(station)
        items.append(item)
        with open(f"./html/{file_name}", 'w') as f:
            f.write(template.render(**item))
    template = templateEnv.get_template('./templates/index.html')
    with open('./html/index.html', 'w') as f:
        f.write(template.render({"objects": items}))
    template = templateEnv.get_template('./templates/map.html')
    with open('./html/map.html', 'w') as f:
        f.write(template.render({"objects": items}))
    return items


def make_geojsons(df):
    items = []
    for gr, df in df.groupby('werk'):
        os.makedirs('./html/data', exist_ok=True)
        file_name = f"{(slugify(gr))}.geojson"
        item = {
            "type": "FeatureCollection",
            "features": []
        }
        feature_line = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": []
            },
            "properties": {
                    "title": f"{gr}"
                }
        }
        for i, row in df.iterrows():
            coords = list(reversed([float(x) for x in row['station_coords'].replace(' ', '').split(',')]))
            feature_line['geometry']['coordinates'].append(coords)
            feature_point = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": coords
                },
                "properties": {
                    "title": row['station_label']
                }
            }
            item["features"].append(feature_point)

        item["features"].append(feature_line)
        with open(f'./html/data/{file_name}', 'w', encoding='utf-8') as f:
            json.dump(item, f, ensure_ascii=False, indent=4)
        items.append(item)
    return items