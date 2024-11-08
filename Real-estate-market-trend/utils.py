import pandas as pd
from sqlalchemy.exc import IntegrityError
import requests

def fetch_json(file_path):
    return pd.read_json(file_path)

def fetch_xml(file_path):
    return pd.read_xml(file_path)

def fetch_excel(file_path):
    return pd.read_excel(file_path)

def fetch_from_api(url):
    response = requests.get(url)
    return pd.DataFrame(response.json()) if response.status_code == 200 else None

def fetch_csv(file_path):
    return pd.read_csv(file_path)

def fetch_html(file_path):
    return pd.read_html(file_path)[0]

def validate_and_transform(df):
    df.dropna(subset=["Property_ID", "Location", "Price"], inplace=True)
    df.drop_duplicates(subset="Property_ID", inplace=True)
    df = df[(df['Price'] >= 50000) & (df['Price'] <= 10000000)]
    df['Price'] = df['Price'].astype(float)
    df['Location'] = df['Location'].str.upper()
    return df
