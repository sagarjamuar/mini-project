import pandas as pd
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
    df.dropna(subset=["Device_ID", "Location", "Energy_Consumption_kWh", "Carbon_Emissions_kgCO2e", "Date"], inplace=True)
    df.drop_duplicates(subset="Device_ID", inplace=True)
    df = df[df['Energy_Consumption_kWh'] >= 0]
    df = df[df['Carbon_Emissions_kgCO2e'] >= 0]
    df['Location'] = df['Location'].str.title()
    return df
