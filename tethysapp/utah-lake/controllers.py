from django.shortcuts import render, reverse
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import MapView, Button
from django.shortcuts import redirect
from django.contrib import messages
from tethys_sdk.gizmos import TextInput, DatePicker, SelectInput
from tethys_sdk.workspaces import app_workspace
from .model import add_new_station
from tethys_sdk.gizmos import DataTableView
from .model import get_all_stations
from tethys_sdk.gizmos import MVDraw, MVView
from tethys_sdk.gizmos import MVLayer

@app_workspace
@login_required()
def home(request, app_workspace):
    """
    Controller for the app home page.
    """

    # Get list of dams and create dams MVLayer:
    stations = get_all_stations(app_workspace.path)
    features = []
    lat_list = []
    lng_list = []

    # Define GeoJSON Features
    for station in stations:
        station_location = station.pop('location')
        lat_list.append(station_location['coordinates'][1])
        lng_list.append(station_location['coordinates'][0])

        station_feature = {
            'type': 'Feature',
            'geometry': {
                'type': station_location['type'],
                'coordinates': station_location['coordinates'],
            }
        }

        features.append(station_feature)

    # Define GeoJSON FeatureCollection
    stations_feature_collection = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        },
        'features': features
    }

    style = {'ol.style.Style': {
        'image': {'ol.style.Circle': {
            'radius': 10,
            'fill': {'ol.style.Fill': {
                'color':  '#d84e1f'
            }},
            'stroke': {'ol.style.Stroke': {
                'color': '#ffffff',
                'width': 1
            }}
        }}
    }}

    # Create a Map View Layer
    stations_layer = MVLayer(
        source='GeoJSON',
        options=stations_feature_collection,
        legend_title='Stations',
        layer_options={'style': style}
    )

    # Define view centered on dam locations
    try:
        view_center = [sum(lng_list) / float(len(lng_list)), sum(lat_list) / float(len(lat_list))]
    except ZeroDivisionError:
        view_center = [-98.6, 39.8]

    view_options = MVView(
        projection='EPSG:4326',
        center=view_center,
        zoom=4.5,
        maxZoom=18,
        minZoom=2
    )

    utah-lake_map = MapView(
        height='100%',
        width='100%',
        layers=[],
        basemap='OpenStreetMap',
    )


    add_station_button = Button(
        display_text='Add Station',
        name='add-station-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        href=reverse('utah-lake:add_station')
    )

    context = {
        'utah-lake_map': utah-lake_map,
        'add_station_button': add_station_button
    }

    return render(request, 'utah-lake/home.html', context)

@app_workspace
@login_required()
def add_station(request, app_workspace):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    name = ''
    owner = 'Reclamation'
    river = ''
    date_built = ''
    location = ''

    # Errors
    name_error = ''
    owner_error = ''
    river_error = ''
    date_error = ''
    location_error = ''

    # Handle form submission
    if request.POST and 'add-button' in request.POST:
        # Get values
        has_errors = False
        name = request.POST.get('name', None)
        owner = request.POST.get('owner', None)
        river = request.POST.get('river', None)
        date_built = request.POST.get('date-built', None)
        location = request.POST.get('geometry', None)

        # Validate
        if not name:
            has_errors = True
            name_error = 'Name is required.'

        if not owner:
            has_errors = True
            owner_error = 'Owner is required.'

        if not river:
            has_errors = True
            river_error = 'River is required.'

        if not date_built:
            has_errors = True
            date_error = 'Date Built is required.'

        if not location:
            has_errors = True
            location_error = 'Location is required.'

        if not has_errors:
            add_new_station(db_directory=app_workspace.path, location=location, name=name, owner=owner, river=river, date_built=date_built)
            return redirect(reverse('utah-lake:home'))

        messages.error(request, "Please fix errors.")

    # Define form gizmos
    name_input = TextInput(
        display_text='Name',
        name='name',
        initial=name,
        error=name_error
    )

    owner_input = SelectInput(
        display_text='Owner',
        name='owner',
        multiple=False,
        options=[('Reclamation', 'Reclamation'), ('Army Corp', 'Army Corp'), ('Other', 'Other')],
        initial=owner,
        error=owner_error
    )

    river_input = TextInput(
        display_text='River',
        name='river',
        placeholder='e.g.: Mississippi River',
        initial=river,
        error=river_error
    )

    date_built = DatePicker(
        name='date-built',
        display_text='Date Built',
        autoclose=True,
        format='MM d, yyyy',
        start_view='decade',
        today_button=True,
        initial=date_built,
        error=date_error
    )

    initial_view = MVView(
        projection='EPSG:4326',
        center=[-98.6, 39.8],
        zoom=3.5
    )

    drawing_options = MVDraw(
        controls=['Modify', 'Delete', 'Move', 'Point'],
        initial='Point',
        output_format='GeoJSON',
        point_color='#FF0000'
    )

    location_input = MapView(
        height='300px',
        width='100%',
        basemap='OpenStreetMap',
        draw=drawing_options,
        view=initial_view
    )

    add_button = Button(
        display_text='Add',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-station-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('utah-lake:home')
    )

    context = {
        'name_input': name_input,
        'owner_input': owner_input,
        'river_input': river_input,
        'date_built_input': date_built,
        'location_input': location_input,
        'location_error': location_error,
        'add_button': add_button,
        'cancel_button': cancel_button,
    }

    return render(request, 'utah-lake/add_station.html', context)


@app_workspace
@login_required()
def list_stations(request, app_workspace):
    """
    Show all stations in a table view.
    """
    stations = get_all_stations(app_workspace.path)
    table_rows = []

    for station in stations:
        table_rows.append(
            (
                station['name'], station['owner'],
                station['river'], station['date_built']
            )
        )

    stations_table = DataTableView(
        column_names=('Name', 'Owner', 'River', 'Date Built'),
        rows=table_rows,
        searching=False,
        orderClasses=False,
        lengthMenu=[ [10, 25, 50, -1], [10, 25, 50, "All"] ],
    )

    context = {
        'stations_table': stations_table
    }

    return render(request, 'utah-lake/list_stations.html', context)
