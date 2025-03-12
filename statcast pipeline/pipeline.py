# Packages / Libraries
import os
from datetime import datetime, timedelta
import pandas as pd
import pybaseball
from pybaseball import statcast
from google.cloud import bigquery

#1. Determine date for which to pull data (here: yesterday)
today = datetime.today()
yesterday = today - timedelta(days=1)