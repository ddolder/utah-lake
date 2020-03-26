import os
import uuid
import json


def add_new_station(db_directory, location, name, owner, river, date_built):
    """
    Persist new station.
    """

    # Convert GeoJSON to Python dictionary
    location_dict = json.loads(location)


    # Serialize data to json
    new_station_id = uuid.uuid4()
    station_dict = {
        'id': str(new_station_id),
        'location':location_dict['geometries'][0],
        'name': name,
        'owner': owner,
        'river': river,
        'date_built': date_built
    }

    station_json = json.dumps(station_dict)

    # Write to file in {{db_directory}}/dams/{{uuid}}.json
    # Make dams dir if it doesn't exist
    stations_dir = os.path.join(db_directory, 'stations')
    if not os.path.exists(stations_dir):
        os.mkdir(stations_dir)

    # Name of the file is its id
    file_name = str(new_station_id) + '.json'
    file_path = os.path.join(stations_dir, file_name)

    # Write json
    with open(file_path, 'w') as f:
        f.write(station_json)

def get_all_stations(db_directory):
    """
    Get all persisted stations.
    """
    # Write to file in {{db_directory}}/dams/{{uuid}}.json
    # Make dams dir if it doesn't exist
    stations_dir = os.path.join(db_directory, 'stations')
    if not os.path.exists(stations_dir):
        os.mkdir(stations_dir)

    stations = []

    # Open each file and convert contents to python objects
    for station_json in os.listdir(stations_dir):
        # Make sure we are only looking at json files
        if '.json' not in station_json:
            continue

        station_json_path = os.path.join(stations_dir, station_json)
        with open(station_json_path, 'r') as f:
            station_dict = json.loads(f.readlines()[0])
            stations.append(station_dict)

    return stations
