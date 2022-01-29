import jinja2
import pandas as pd
import requests
from slugify import slugify
from io import BytesIO



templateLoader = jinja2.FileSystemLoader(searchpath=".")
templateEnv = jinja2.Environment(loader=templateLoader)
template = templateEnv.get_template('./templates/base.html')

GDRIVE_URL = "https://docs.google.com/spreadsheet/ccc?key=1G5HRtHLrYGJkXj8s72KC6Uatuhy52hjBKFJpXDgQuP8"

def gsheet_to_df():
    url = f"{GDRIVE_URL}&output=csv"
    r = requests.get(url)
    print(r.status_code)
    data = r.content
    df = pd.read_csv(BytesIO(data))
    return df

df = gsheet_to_df()
# df.to_csv('data_dump.csv', index=False)

items = []
for gr, df in df.groupby('werk'):
    file_name = f"{(slugify(gr))}.html"
    item = {
        "url": file_name,
        "title": gr,
        "stations": []
    }
    for i, row in df.iterrows():
        station = {}
        for x in row.keys():
            station[x] = row[x]
        item['stations'].append(station)
    items.append(item)

with open('./html/index.html', 'w') as f:
    f.write(template.render({"objects": items}))