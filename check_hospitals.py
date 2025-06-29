#!/usr/bin/env python3
import pandas as pd

# Load the hospital masterlist
hospitals_df = pd.read_csv('hospitals_masterlist.csv', skiprows=2)

print(f"Total hospitals in masterlist: {len(hospitals_df)}")
print("\nAll hospitals in masterlist:")
for idx, row in hospitals_df.iterrows():
    print(f"  {idx+1}. {row['name']} - {row['city']}, {row['state']}")

# Check which cities are missing from our coordinates
city_coords = {
    'Madison, WI': (43.0731, -89.4012),
    'Milwaukee, WI': (43.0389, -87.9065),
    'Chicago, IL': (41.8781, -87.6298),
    'St. Louis, MO': (38.6270, -90.1994),
    'Oklahoma City, OK': (35.4676, -97.5164),
    'Janesville, WI': (42.6828, -89.0187),
    'Fond du Lac, WI': (43.7730, -88.4470),
    'Rockford, IL': (42.2711, -89.0940),
    'Freeport, IL': (42.2967, -89.6212),
    'Centralia, IL': (38.5250, -89.1334),
    'Mount Vernon, IL': (38.3173, -88.9031),
    'Columbia, IL': (38.4437, -90.2012),
    'Benton, IL': (37.9967, -88.9203),
    'Fenton, MO': (38.5139, -90.4432),
    'Salem, IL': (38.6269, -88.9456),
    'Lena, IL': (42.3794, -89.8223),
    'Durand, IL': (42.4336, -89.3318),
    'Maryville, IL': (38.7231, -89.9559),
    'Wentzville, MO': (38.8114, -90.8529),
    'O\'Fallon, MO': (38.8106, -90.6998),
    'Kirkwood, MO': (38.5834, -90.4068),
    'Chesterfield, MO': (38.6631, -90.5771),
    'Ballwin, MO': (38.5950, -90.5462),
    'Jefferson City, MO': (38.5767, -92.1735),
    'Tipton, MO': (38.6556, -92.7799),
    'Springfield, MO': (37.2090, -93.2923),
    'Shawnee, OK': (35.3273, -96.9253),
    'Edmond, OK': (35.6528, -97.4781),
    'Midwest City, OK': (35.4495, -97.3967),
    'Moore, OK': (35.3395, -97.4867),
    'Mustang, OK': (35.3842, -97.7245),
    'Purcell, OK': (35.0137, -97.3611),
    'El Reno, OK': (35.5323, -97.9550),
    'Blanchard, OK': (35.1378, -97.6589),
    'Pauls Valley, OK': (34.7401, -97.2211),
    'Tecumseh, OK': (35.2578, -96.9361),
    'Choctaw, OK': (35.4795, -97.2706),
    'Okemah, OK': (35.4326, -96.3056),
    'Chandler, OK': (35.7017, -96.8809),
    'Enid, OK': (36.3956, -97.8784),
    'Seminole, OK': (35.2245, -96.6706),
    'McLoud, OK': (35.4362, -97.0914),
    'Harrah, OK': (35.4895, -97.1636),
}

print("\nHospitals missing coordinates:")
missing_count = 0
for idx, row in hospitals_df.iterrows():
    key = f"{row['city']}, {row['state']}"
    if key not in city_coords:
        print(f"  {row['name']} - {key}")
        missing_count += 1

print(f"\nMissing coordinates for {missing_count} hospitals")
print(f"Available coordinates for {len(hospitals_df) - missing_count} hospitals") 