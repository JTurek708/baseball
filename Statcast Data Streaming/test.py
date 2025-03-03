from flask import Flask, jsonify
import datetime
import pytz
import logging
from pybaseball import statcast
from google.cloud import bigquery

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_statcast_data_for_yesterday():
    """
    Calculate yesterday's date in US/Central time and fetch Statcast data for that day.
    """
    central_tz = pytz.timezone('US/Central')
    now_central = datetime.datetime.now(central_tz)
    yesterday = now_central.date() - datetime.timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    logging.info(f"Fetching Statcast data for: {date_str}")
    
    # Fetch data for the specified day
    data = statcast(start_dt=date_str, end_dt=date_str)
    return data

def load_data_to_bigquery(dataframe, table_id):
    """
    Load a pandas DataFrame into a BigQuery table (append mode).
    """
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"  # Append data to your existing table
    )
    load_job = client.load_table_from_dataframe(dataframe, table_id, job_config=job_config)
    load_job.result()  # Wait for the job to complete
    logging.info(f"Successfully loaded {len(dataframe)} rows into {table_id}")

def run_pipeline():
    """
    Run the entire pipeline: fetch data and load it into BigQuery.
    """
    # Replace with your BigQuery table identifier in the format: "project.dataset.table"
    table_id = "baseball-450617.statcast_pitch_level"
    try:
        df = fetch_statcast_data_for_yesterday()
        load_data_to_bigquery(df, table_id)
        return f"Pipeline executed successfully, loaded {len(df)} rows."
    except Exception as e:
        logging.exception("Error during pipeline execution")
        raise e

@app.route("/", methods=["GET"])
def index():
    """
    HTTP endpoint that triggers the pipeline.
    """
    try:
        message = run_pipeline()
        return jsonify({"status": "success", "message": message}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Run the Flask app locally on port 8080
    app.run(host="0.0.0.0", port=8080)