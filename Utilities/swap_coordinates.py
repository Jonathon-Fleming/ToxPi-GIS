import pandas as pd
import sys

def swap_coordinates(path):
    df = pd.read_csv(path)
    df[['Longitude','Latitude']] = df.Source.str.split(",",expand = True,)
    df['Source'] = df['Latitude'].str.strip() + ", " + df['Longitude'].str.strip()
    del df["Latitude"]
    del df["Longitude"]
    df.to_csv(path, index = False)
if __name__ == '__main__':
    swap_coordinates(sys.argv[1])