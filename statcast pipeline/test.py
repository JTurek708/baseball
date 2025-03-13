import io
import pandas as pd
from pybaseball import statcast
from google.cloud import storage

storage_client = storage.Client(project="Baseball")

def run_pipeline_for_date(target_date: str, bucket_name: str):
    """
    Runs the pipeline for a given date.
    
    Parameters:
      target_date (str): Date in 'YYYY-MM-DD' format.
      bucket_name (str): Name of the GCP bucket to upload the CSV.
    """
    print(f"Processing data for {target_date}...")
    
    # Retrieve the data using pybaseball
    try:
        data = statcast(start_dt=target_date, end_dt=target_date)
    except Exception as e:
        print(f"Error retrieving data for {target_date}: {e}")
        return
    
    if data.empty:
        print(f"No data retrieved for {target_date}")
        return

    print(f"Retrieved {len(data)} rows of data for {target_date}")

    # Convert the DataFrame to CSV in-memory using StringIO
    csv_buffer = io.StringIO()
    data.to_csv(csv_buffer, index=False)
    csv_contents = csv_buffer.getvalue()

    # Define the target filename in the bucket
    filename = f"pitch_by_pitch_{target_date}.csv"
    
    # Upload the CSV data to Google Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(csv_contents, content_type='text/csv')
    
    print(f"CSV data for {target_date} successfully uploaded to bucket '{bucket_name}' as {filename}.")

if __name__ == '__main__':
    # Replace with your actual GCP bucket name
    bucket_name = "baseball_data_jpt"
    
    # Define the test dates (e.g., two days in September 2024)
    test_dates = ["2024-09-15", "2024-09-16"]
    
    for date in test_dates:
        run_pipeline_for_date(date, bucket_name)
