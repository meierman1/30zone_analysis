import gpxpy
import gpxpy.gpx
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import os
import numpy as np

# Configurable parameters
DATA_FOLDER = 'data'
LAT_MIN = 47.447030
LAT_MAX = 47.451898
LON_MIN = 8.141421
LON_MAX = 8.146656
VMAX_KPH = 30  # Geschwindigkeit in km/h
PLOT_ENABLED = True

excess_delays = []

for file_name in os.listdir(DATA_FOLDER):
    if not file_name.endswith('.gpx'):
        continue

    GPX_FILE = os.path.join(DATA_FOLDER, file_name)
    with open(GPX_FILE, 'r') as f:
        gpx = gpxpy.parse(f)

    # Flatten and crop points
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for pt in segment.points:
                if ((LAT_MIN is None or pt.latitude >= LAT_MIN) and
                    (LAT_MAX is None or pt.latitude <= LAT_MAX) and
                    (LON_MIN is None or pt.longitude >= LON_MIN) and
                    (LON_MAX is None or pt.longitude <= LON_MAX)):
                    points.append({'lat': pt.latitude, 'lon': pt.longitude, 'time': pt.time})

    # Calculate speed
    data = []
    for i in range(1, len(points)):
        p1, p2 = points[i - 1], points[i]
        dt = (p2['time'] - p1['time']).total_seconds()
        if dt == 0:
            continue
        dist = geodesic((p1['lat'], p1['lon']), (p2['lat'], p2['lon'])).km
        speed = dist / (dt / 3600)
        data.append({
            'start_time': p1['time'],
            'end_time': p2['time'],
            'delta_s': (p2['time'] - points[0]['time']).total_seconds(),
            'duration_s': dt,
            'distance_km': dist,
            'speed_kph': speed
        })

    df = pd.DataFrame(data)

    # Build adjusted timeline
    adjusted_times = [0.0]  # in seconds
    excess_delay_s = 0.0

    for i, row in df.iterrows():
        duration_s = row['duration_s']
        speed = row['speed_kph']
        dist = row['distance_km']

        if speed > VMAX_KPH:
            vmax_mps = VMAX_KPH / 3.6
            actual_mps = speed / 3.6
            gained_distance_km = dist * (1 - (vmax_mps / actual_mps))
            extra_time_s = (gained_distance_km * 1000) / vmax_mps
            excess_delay_s += extra_time_s
            duration_s += extra_time_s

        adjusted_times.append(adjusted_times[-1] + duration_s)

    df['adjusted_delta_s'] = adjusted_times[1:]
    df['clipped_speed_kph'] = df['speed_kph'].clip(upper=VMAX_KPH)

    excess_delays.append(excess_delay_s)

    if PLOT_ENABLED:
        plt.figure(figsize=(12, 5))
        plt.axhline(VMAX_KPH, color='gray', linestyle='--', zorder=1, label=f'vmax = {VMAX_KPH} km/h')
        plt.fill_between(df['delta_s'], df['speed_kph'],
                         VMAX_KPH,
                         where=(df['speed_kph'] > VMAX_KPH),
                         color='red', alpha=0.3, label='Über vmax', zorder=2)
        plt.plot(df['delta_s'], df['speed_kph'], label='Originale Geschwindigkeit', zorder=3)
        plt.plot(df['adjusted_delta_s'], df['clipped_speed_kph'], label='Angepasste Geschwindigkeit', color='green', zorder=4)
        plt.xlabel('Zeit (Sekunden)')
        plt.ylabel('Geschwindigkeit (km/h)')
        plt.title(f'Geschwindigkeit vor und nach Anpassung ({file_name})')
        plt.legend()
        plt.tight_layout()
        plt.show()

    print(f"{file_name} - Erhöhte Fahrzeit: {excess_delay_s:.1f} Sekunden")

# Summary statistics
print("\nZusammenfassung der zusätzlichen Fahrzeiten (Sekunden):")
print([round(x, 1) for x in excess_delays])
print(f"Mittelwert: {np.mean(excess_delays):.1f} Sekunden")
print(f"Median: {np.median(excess_delays):.1f} Sekunden")

