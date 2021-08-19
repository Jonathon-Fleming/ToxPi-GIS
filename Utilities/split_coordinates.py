import pandas as pd
import sys

def split_coordinates(path):
    df = pd.read_csv(path)
    df[['Latitude','Longitude']] = df.Source.str.split(",",expand = True,)
    del df['Source']
    df.to_csv(path, index = False)
if __name__ == '__main__':
    split_coordinates(sys.argv[1])