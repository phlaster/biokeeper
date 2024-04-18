import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from os import listdir
from os.path import join

import shutils
#import psycopg2

#DB_NAME = "postgres"# os.environ['POSTGRES_DB'] 
#DB_USER = "postgres"# os.environ['POSTGRES_USER'] 
#DB_PASSWORD = "root"# os.environ['POSTGRES_PASSWORD'] 
#DB_HOST =  'db_postgres'
#DB_PORT =  '8080'

app = FastAPI()

def get_researches_list():
    return [r for r in listdir('/researches/') if r.startswith('research_')]

#def get_research_qrcodes(research_id):
#    return [file for file in listdir(f'/researches/\{research_{research_id}\}') if file.endswith('svg')]

def get_research_details(research_id):
    csv_file = [file for file in listdir(f'/researches/research_{research_id}') if file.endswith('csv')][0]
    with open(f'/researches/research_{research_id}/{csv_file}', 'r') as f:
        data = f.readlines()
    result = []
    for row in data:
        if ',' in row:
            qrcode_id, qrcode_string = row.strip().split(',')
            result.append({"qrcode_id": qrcode_id, "qrcode_string": qrcode_string})
    return result
    

@app.get('/')
def get_adminpanel_index():
    return "Hello world!"

@app.get('/researches')
def api_get_researches_list():
    return JSONResponse(content={"researches": get_researches_list()}, status_code=200)    


@app.get('/researches/{research_id}')
def api_get_research_details(research_id: int):
    qrcodes = get_research_details(research_id)
    qrcodes_amount = len(qrcodes)
    return JSONResponse(content={"qrcodes_amount": qrcodes_amount, \
            'qrcodes': qrcodes}, status_code=200)    

@app.get('researches/{research_id}/download')
def api_download_research(research_id: int):
    research_dir = f'/researches/research_{research_id}/'
    zip_filepath = join(research_dir, f'{research_id}.zip')
    shutil.make_archive(zip_filepath, 'zip', research_dir)
    return FileResponse(zip_filepath, media_type="application/zip", filename=f'{research_id}.zip') 

if __name__ == "__main__":
    uvicorn.run(app, port=9999, host='0.0.0.0')


