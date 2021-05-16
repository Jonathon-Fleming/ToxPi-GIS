import pandas as pd
df = pd.read_csv(r'C:\Users\Jonathon\Documents\Reif Research\ToxPiGIS\Github and Paper\Vignette2_Full.csv')
df[['Latitude','Longitude']] = df.Source.str.split(",",expand = True,)
del df['Source']
df.to_csv(r'C:\Users\Jonathon\Documents\Reif Research\ToxPiGIS\Github and Paper\Vignette2_Full.csv', index = False)