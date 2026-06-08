# -*- coding: utf-8 -*-
import arcpy
import subprocess
import ctypes

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox in the Catalog pane)."""
        self.label = "GIS Online Assistant"
        self.alias = "GISOnlineAssistant"
        # List of tool classes associated with this toolbox
        self.tools = [BasemapAndDNSTool]

class BasemapAndDNSTool(object):
    def __init__(self):
        """Define the tool (tool name and description)."""
        self.label = "Add Online Basemaps & Set DNS"
        self.description = "Sets DNS to bypass restrictions and adds various online XYZ tile services."
        self.canRunInBackground = False
        
        # Dictionary of map sources (Add or remove URLs here)
        self.map_sources = {
            # --- FEATURED ---
            'Snap Map (Iran)': 'https://raster.snappmaps.ir/styles/snapp-style/{z}/{x}/{y}.png',
            'Balad tehran satellite (Iran)':'https://tiles.raah.ir/tiles/satellite_tehran_v4_super_resolution/{z}/{x}/{y}.png',
            'Balad (Iran)':'https://tiles.raah.ir/tiles/satellite_iran_v2_super_resolution/{z}/{x}/{y}.png',
            'Google Maps (Road)': 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            'Google Satellite': 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            'Google Satellite (Bypass)': 'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
            'Google Hybrid': 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            'Google Terrain': 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
            
            # --- OSM & TOPO ---
            'OpenStreetMap Standard': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            'OpenStreetMap HOT': 'https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            'OpenTopoMap': 'https://a.tile.opentopomap.org/{z}/{x}/{y}.png',
            'CyclOSM': 'https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
            'MtbMap': 'http://tile.mtbmap.cz/mtbmap_tiles/{z}/{x}/{y}.png',
            
            # --- ESRI (ArcGIS Online) ---
            'Esri World Imagery': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            'Esri World Street Map': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
            'Esri World Topo': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
            'Esri NatGeo World Map': 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
            'Esri World Gray Canvas': 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
            'Esri Ocean Basemap': 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
            'Esri Boundaries and Places': 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
            
            # --- CARTODB ---
            'CartoDB DarkMatter': 'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            'CartoDB Positron (Light)': 'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
            'CartoDB Voyager': 'https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
            
            # --- OTHER GLOBAL ---
            'Bing VirtualEarth': 'http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1',
            'Yandex Satellite': 'https://sat04.maps.yandex.net/tiles?l=sat&x={x}&y={y}&z={z}',
            '2GIS Map': 'https://tile2.maps.2gis.com/tiles?x={x}&y={y}&z={z}&v=1.1',
            'Natural Earth Tiles': 'https://naturalearthtiles.roblabs.com/tiles/natural_earth_cross_blended_hypso_shaded_relief.raster/{z}/{x}/{y}.png',
            
            # --- SPECIALTY ---
            'NASA BlueMarble': 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg',
            'NASA Night Lights': 'https://map1.vis.earthdata.nasa.gov/wmts-webmerc/VIIRS_CityLights_2012/default//GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg',
            'OpenRailwayMap': 'https://a.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png',
            'WaymarkedTrails Hiking': 'https://tile.waymarkedtrails.org/hiking/{z}/{x}/{y}.png',
            'Strava Heatmap (All)': 'https://heatmap-external-a.strava.com/tiles/all/hot/{z}/{x}/{y}.png'
        }


    def getParameterInfo(self):
        """Define parameter definitions"""
        
        # Parameter 0: Select Layers (Multi-value string)
        param0 = arcpy.Parameter(
            displayName="Select Online Basemaps",
            name="layers",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        # Populate the dropdown list with sorted dictionary keys
        param0.filter.list = sorted(list(self.map_sources.keys()))

        # Parameter 1: DNS Configuration
        param1 = arcpy.Parameter(
            displayName="DNS Provider Configuration",
            name="dns_provider",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["No Change", "Default (DHCP)", "Shecan", "403 Online"]
        param1.value = "No Change"

        # Parameter 2: Network Interface Selection
        param2 = arcpy.Parameter(
            displayName="Network Interface Name",
            name="interface",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param2.filter.list = ["Wi-Fi", "Ethernet"]
        param2.value = "Wi-Fi"

        return [param0, param1, param2]

    def is_admin(self):
        """Check if the current user has administrative privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def execute(self, parameters, messages):
        """The source code of the tool."""
        selected_layers = parameters[0].valueAsText.split(";")
        dns_choice = parameters[1].valueAsText
        interface = parameters[2].valueAsText

        # --- PART 1: DNS Configuration ---
        if dns_choice != "No Change":
            # DNS modification requires Admin rights
            if not self.is_admin():
                arcpy.AddError("Error: ArcGIS Pro must be 'Run as Administrator' to change DNS settings.")
                return

            try:
                if dns_choice == "Default (DHCP)":
                    # Reset DNS to automatic (DHCP)
                    cmd = f'netsh interface ip set dns "{interface}" dhcp'
                    subprocess.run(cmd, shell=True, check=True)
                    arcpy.AddMessage(f"DNS for {interface} has been reset to DHCP.")
                else:
                    # Specific DNS Providers (Primary and Secondary)
                    dns_dict = {
                        "Shecan": ["178.22.122.100", "185.51.200.2"],
                        "403 Online": ["10.202.10.202", "10.202.10.102"]
                    }
                    primary, secondary = dns_dict[dns_choice]
                    
                    # Apply primary DNS
                    cmd1 = f'netsh interface ip set dns "{interface}" static {primary}'
                    # Add secondary DNS
                    cmd2 = f'netsh interface ip add dns "{interface}" {secondary} index=2'
                    
                    subprocess.run(cmd1, shell=True, check=True)
                    subprocess.run(cmd2, shell=True, check=True)
                    arcpy.AddMessage(f"DNS successfully set to {dns_choice} on {interface}.")
            except Exception as e:
                arcpy.AddWarning(f"Failed to apply DNS settings: {e}")

        # --- PART 2: Adding Layers to the Map ---
        aprx = arcpy.mp.ArcGISProject('CURRENT')
        active_map = aprx.activeMap

        # Check if a map view is open
        if not active_map:
            arcpy.AddError("No active map found. Please open a map in your project first.")
            return

        for layer_name in selected_layers:
            # Clean string (remove quotes from multi-value input)
            clean_name = layer_name.strip("'")
            url = self.map_sources[clean_name]
            
            try:
                arcpy.AddMessage(f"Connecting to: {clean_name}...")
                # Add the XYZ service to the map
                new_lyr = active_map.addDataFromPath(url)
                # Rename the layer for clarity in the Table of Contents
                new_lyr.name = clean_name
            except Exception as e:
                arcpy.AddWarning(f"Could not add layer {clean_name}: {e}")

        return