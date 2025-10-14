import pandas as pd
from flask_restx import Resource, Namespace, abort
from threading import Lock

# --- Setup ---
public_ns = Namespace('public', description='Publicly accessible data resources like vehicle brands and colors')

# --- In-Memory Data Cache ---
VEHICLE_DATA = {}
data_load_lock = Lock()

def load_vehicle_data():
    """
    Loads vehicle and color data from CSV files into the VEHICLE_DATA cache.
    This function is thread-safe to prevent race conditions during initial load.
    """
    global VEHICLE_DATA
    # Check if data is already loaded without acquiring the lock first for performance
    if 'brands' in VEHICLE_DATA:
        return

    with data_load_lock:
        # Double-check if another thread loaded the data while this one was waiting for the lock
        if 'brands' in VEHICLE_DATA:
            return

        try:
            # Note: Place Cars.csv and colors.csv in the root of your backend project folder.
            cars_df = pd.read_csv('Cars.csv', encoding='latin1')
            colors_df = pd.read_csv('colors.csv', encoding='latin1')
            
            # --- Process Car Data ---
            cars_df['Company Names'] = cars_df['Company Names'].str.strip().str.title()
            
            models_by_brand = cars_df.groupby('Company Names')['Cars Names'].apply(
                lambda x: sorted(list(x.unique()))
            ).to_dict()
            
            # --- Store Processed Data in Cache ---
            VEHICLE_DATA['brands'] = sorted(list(models_by_brand.keys()))
            VEHICLE_DATA['models_by_brand'] = models_by_brand
            VEHICLE_DATA['colors'] = sorted(list(colors_df['name'].unique()))

            print("✅ Successfully loaded vehicle and color data from CSV files.")

        except FileNotFoundError as e:
            print(f"❌ CRITICAL ERROR: {e}. Make sure 'Cars.csv' and 'colors.csv' are in the root of your backend project.")
            VEHICLE_DATA = {'brands': [], 'models_by_brand': {}, 'colors': []}
        except Exception as e:
            print(f"❌ An error occurred while loading CSV data: {e}")
            VEHICLE_DATA = {'brands': [], 'models_by_brand': {}, 'colors': []}

# --- Service Layer for Accessing Vehicle Data ---
class VehicleDataService:
    @staticmethod
    def get_brands():
        load_vehicle_data()
        return VEHICLE_DATA.get('brands', [])

    @staticmethod
    def get_models_for_brand(brand_name):
        load_vehicle_data()
        brand_key = brand_name.strip().title()
        return VEHICLE_DATA.get('models_by_brand', {}).get(brand_key, [])

    @staticmethod
    def get_colors():
        load_vehicle_data()
        return VEHICLE_DATA.get('colors', [])

# --- API Endpoints ---
@public_ns.route('/brands')
class BrandListResource(Resource):
    def get(self):
        """Get a list of all unique vehicle brands."""
        brands = VehicleDataService.get_brands()
        return {'brands': brands}, 200

@public_ns.route('/models/<string:brand_name>')
@public_ns.param('brand_name', 'The name of the vehicle brand (e.g., Ford)')
class ModelListResource(Resource):
    def get(self, brand_name):
        """Get a list of models for a specific brand."""
        models = VehicleDataService.get_models_for_brand(brand_name)
        if not models:
            abort(404, f'No models found for brand "{brand_name}". Please check the brand name.')
        return {'models': models}, 200

@public_ns.route('/colors')
class ColorListResource(Resource):
    def get(self):
        """Get a list of all vehicle colors."""
        colors = VehicleDataService.get_colors()
        return {'colors': colors}, 200
