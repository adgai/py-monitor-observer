import os
import json
import time
import requests
import datetime

from bs4 import BeautifulSoup

dashboard_id = 'dds8i1mqqa680e'
dashboard_name = 'new-dashboard'
www = 'http://localhost:3000'
data_url = f'{www}/api/dashboards/uid/{dashboard_id}'
render_url = 'http://localhost:8081/render'
data = []
origin_id = 1
from_time = 'now-5m'
to_time = 'now'
theme = 'light'
width = 1200
height = 400
cbbfbe_ = 'Bearer glsa_5y1sSxJxR9hNEks2cbtAJnYfQEBuAkk6_cbbfbe80'

panel = {
    1: 3,
    5: 6
}


def generate_grafana_dashboard_data():
    ar = []
    index = 0
    end = 0
    last_type = data[0]['type'] if data and 'type' in data[0] else ''

    for j in range(len(data)):
        if last_type == (data[j]['type'] if 'type' in data[j] else ''):
            end = j
        else:
            ar.append(data[index:end + 1])
            index = j
            end = j
            last_type = data[j]['type'] if 'type' in data[j] else ''

    ar.append(data[index:end + 1])  # Add the last slice
    print(json.dumps(ar))
    return ar


def gen_html(ar):
    original_index_file_path = os.path.join('DashBoardTemplate.html')
    with open(original_index_file_path, 'r', encoding='utf-8') as f:
        index_html = f.read()

    soup = BeautifulSoup(index_html, 'html.parser')
    container = soup.new_tag('div')
    container['class'] = 'dashboard-container'

    height_unit = 40
    width_unit = 100

    for d in ar:
        if d[0]['type'] == 'row':
            for di in d:
                row_div = soup.new_tag('div')
                span = soup.new_tag('span')
                span.string = di['title']
                row_div.append(span)
                row_div['class'] = 'row'

                widths = di['gridPos']['x'] * width_unit

                heights = di['gridPos']['y'] * height_unit
                row_div[
                    'style'] = f"transform: translate({widths}px, {heights}px);"

                container.append(row_div)
        else:
            for dx in d:
                widths = dx['gridPos']['w'] * width_unit
                heights = dx['gridPos']['h'] * height_unit

                panel_div = soup.new_tag('div')
                panel_content = soup.new_tag('div')
                panel_content['class'] = 'panel-content'

                panel_id = dx['id']
                path1 = f"../disk/img-{panel_id}.png"

                panel_url = f"{www}/d-solo/{dashboard_id}/{dashboard_name}?panelId={panel_id}&orgId=1&render=1&viewPanel=&from={from_time}&to={to_time}&theme=light"
                print(panel_url)
                render_img(panel_url, path1, widths, heights)

                img = soup.new_tag('img')
                img['src'] = path1
                img['class'] = ['panel-img', 'data-zoomable']
                panel_content.append(img)

                panel_div.append(panel_content)
                panel_div['style'] = 'position: absolute'
                panel_div['class'] = 'panel'

                panel_div[
                    'style'] = f"width: {widths}px; height: {heights}px; transform: translate({dx['gridPos']['x'] * width_unit}px, {dx['gridPos']['y'] * height_unit}px);"

                container.append(panel_div)

    article_element = soup.find(id='article')
    if article_element:
        article_element.clear()  # 清空之前的内容
        article_element.append(container)

    disk_directory = '../disk'
    output_index_file_path = os.path.join(disk_directory, 'index.html')
    with open(output_index_file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))


def gen_d():
    data1 = get_data()
    data1 = data1 if data1 else []
    data.extend(data1['dashboard']['panels'] if 'dashboard' in data1 and 'panels' in data1['dashboard'] else [])
    ar = generate_grafana_dashboard_data()
    # 获取当前日期和时间
    current_time = datetime.datetime.now()

    # 打印当前日期和时间
    print("当前时间:", current_time)
    gen_html(ar)

    # 获取当前日期和时间
    current_time = datetime.datetime.now()

    # 打印当前日期和时间
    print("当前时间:", current_time)


def fetch_data(url):
    headers = {
        'Authorization': cbbfbe_
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f'Requests error: {e}')
        return None


def get_data():
    return fetch_data(data_url)


def render_img(url, path1, width, height):
    params = {
        'url': url,
        'domain': 'localhost',
        'width': width,
        'height': height
    }
    download_image_sync(render_url, params, path1)
    # time.sleep(2)


def download_image_sync(url, params, output_path):
    # full_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    # print(full_url)
    try:
        response = requests.get(url, params=params, headers={'X-Auth-Token': '-'})
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
                print('Image downloaded and saved to', output_path)
        else:
            print(f'Error downloading image: {response.status_code} - {response.reason}')
    except requests.exceptions.RequestException as e:
        print(f'Requests error: {e}')


gen_d()
