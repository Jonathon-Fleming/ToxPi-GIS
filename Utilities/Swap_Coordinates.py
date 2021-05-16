import pandas as pd
df = pd.read_csv(r'C:\Users\Jonathon\Documents\Reif Research\ToxPiGIS\Github and Paper\Vignette2_Full.csv')
tmp = df.Source.str.split(",",expand = True,)
final = tmp[1] + "," + tmp[0]
df['Source'] = final
df.to_csv(r'C:\Users\Jonathon\Documents\Reif Research\ToxPiGIS\Github and Paper\Vignette2_Full.csv', index = False)