import os
import boto3
import glob
import sys
import time

print("Waiting 5 seconds for graceful shutdown...")
time.sleep(5)

# --- 1. SETTINGS ---
RECORDING_FOLDER = r"C:\scripts\temp_recordings"
S3_BUCKET = "elephant-bucket-ocap-recordings"

# --- 2. S3 UPLOAD FUNCTION ---
def upload_recordings_to_s3():
    s3_client = boto3.client('s3')
    
    # Find all .mcap and .mkv files
    mcap_files = glob.glob(os.path.join(RECORDING_FOLDER, "*.mcap"))
    mkv_files = glob.glob(os.path.join(RECORDING_FOLDER, "*.mkv"))
    
    files_to_upload = mcap_files + mkv_files
    file_count = len(files_to_upload)
    
    if file_count == 0:
        print("S3 Upload: No matching files found.")
        return

    print(f"S3 Upload: Found {file_count} file(s) to upload.")
    
    for file_path in files_to_upload:
        file_name = os.path.basename(file_path)
        print(f"Uploading {file_name} to S3 bucket {S3_BUCKET}...")
        try:
            s3_client.upload_file(file_path, S3_BUCKET, file_name)
            print(f"Upload complete for: {file_name}")
            
            # --- THIS IS THE NEW CODE ---
            os.remove(file_path)
            print(f"Successfully deleted local file: {file_name}")
            # --------------------------
            
        except Exception as e:
            # If upload or delete fails, it will be caught here
            print(f"ERROR processing {file_name}: {e}")
            
    print("S3 upload and local cleanup process finished.")

# --- 3. RUN THE UPLOAD ---
if __name__ == "__main__":
    try:
        upload_recordings_to_s3()
        print("Upload script finished.")
    except Exception as e:
        print(f"An error occurred during the upload process: {e}")
        sys.exit(1)