import joblib
import gseapy as gp
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')

sc_samples = joblib.load(os.path.join(DATA_PATH, 'sc_samples.pkl'))

degs = joblib.load(os.path.join(DATA_PATH, 'degs.pkl'))

libraries = gp.get_library_name(organism="Human")
