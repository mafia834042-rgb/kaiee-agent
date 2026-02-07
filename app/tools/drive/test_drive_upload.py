import os
from app.tools.drive.drive_client import upload_file_to_drive

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

file_path = os.path.join(BASE_DIR, "README.md")

print("Using file path:", file_path)

result = upload_file_to_drive(
    file_path=file_path,
    filename="README_test_upload.md",
    folder_id="1CBBZt50pKncGUYIlt5v_JBtA8UP"
)

print(result)