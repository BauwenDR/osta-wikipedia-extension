import axios

wikipedia_api = ""
api_headers = {}
batch_size = 50
bearer_token = ""

async def get_wikipedia_language():
    return getVariableFromStorage("language")

async def get_api_token():
    return getVariableFromStorage("api-token")

async def get_geosearch_results(top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon):
    params = {
        "action": "query",
        "format": "json",
        "list": "geosearch",
        "gsbbox": top_left_lat + "|" + top_left_lon + "|" + bottom_right_lat + "|" + bottom_right_lon,
        "gslimit": "max",
    }

    return axios.get(wikipedia_api, {params, headers: api_headers}).data

async def get_extract(page_ids, cont='', excont=''):
    page_ids_str = page_ids.join('|')

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "pageids": page_ids_str,
        "exintro": 1,
        "explaintext": 1,
        "exsectionformat": "plain",
        "continue": cont,
        "excontinue": excont
    }

    data = axios.get(wikipedia_api, {params, headers: api_headers}).data
    return_data = []

    Object.keys(data.query.pages).forEach(page_name =>
        page = data.query.pages[page_name]
        if page.extract:
            return_data.push(page)
    )

    if data.continue:
        return_data = return_data.concat(get_extract(page_ids, data.continue.continue, data.continue.excontinue))

    return return_data
    
# Main
wikipedia_api = "https://" + get_wikipedia_language() + ".wikipedia.org/w/api.php?origin=*"
bearer_token = get_api_token()
if bearer_token:
    api_headers['Authorization'] = "Bearer " + bearer_token
    batch_size = 500
    
geosearch_results = get_geosearch_results(boundingBox.topLeft.lat, boundingBox.topLeft.lng, boundingBox.bottomRight.lat, boundingBox.bottomRight.lng)
geodata = geosearch_results.query.geosearch

landmarks = []
page_ids = {}
geodata.forEach((location, index) =>
    landmarks[index] = {
        'lat': location.lat,
        'lng': location.lon,
        'name': location.title,
        'description': '',
        'types': []
    }
    page_ids[location.pageid] = index
)

for i in range(geodata.length/batch_size):
    batch = geodata.slice(i*batch_size, (i+1)*batch_size)
    batch_ids = batch.map(data => data.pageid)
    extract_data = get_extract(batch_ids)

    for batch_landmark in extract_data:
        landmarks[page_ids[batch_landmark.pageid]].description = batch_landmark.extract

return landmarks
