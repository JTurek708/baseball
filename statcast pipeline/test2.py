import io
import pandas as pd
from pybaseball import statcast
from google.cloud import storage

def run_pipeline_for_date(target_date: str, bucket_name: str, master_filename: str = "pitch_by_pitch_master.csv"):
    """
    Processes the data for a given date, appends it to a master CSV file stored in GCP,
    and uploads the updated master file back to the bucket.
    """
    print(f"Processing data for {target_date}...")
    
    # 1. Retrieve today's data using pybaseball
    try:
        data = statcast(start_dt=target_date, end_dt=target_date)
    except Exception as e:
        print(f"Error retrieving data for {target_date}: {e}")
        return
    
    if data.empty:
        print(f"No data retrieved for {target_date}")
        return

    print(f"Retrieved {len(data)} rows of data for {target_date}")

    # 2. Initialize the Cloud Storage client and target bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    master_blob = bucket.blob(master_filename)
    
    # 3. Try to download the existing master CSV file from the bucket
    try:
        master_csv_contents = master_blob.download_as_string().decode("utf-8")
        master_df = pd.read_csv(io.StringIO(master_csv_contents))
        print("Existing master file found. Appending new data.")
        # Append today's data to the master data
        combined_df = pd.concat([master_df, data], ignore_index=True)
    except Exception as e:
        # If the master file doesn't exist or there's an error reading it, create a new one.
        print("Master file not found or error reading it; creating a new master file.")
        combined_df = data

    # 4. Convert the combined DataFrame to CSV (in-memory)
    combined_csv_buffer = io.StringIO()
    combined_df.to_csv(combined_csv_buffer, index=False)
    combined_csv_contents = combined_csv_buffer.getvalue()

    # 5. Upload the combined CSV data back to the bucket as the master file
    master_blob.upload_from_string(combined_csv_contents, content_type='text/csv')
    print(f"Master CSV file successfully updated in bucket '{bucket_name}' as {master_filename}.")

if __name__ == '__main__':
    # Replace with your actual GCP bucket name
    bucket_name = "baseball_data_jpt"
    
    # Define the test dates (for example, two days in September 2024)
    test_dates = ["2024-09-15", "2024-09-16"]
    
    for date in test_dates:
        run_pipeline_for_date(date, bucket_name)
