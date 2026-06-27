import os
import shutil
from datetime import datetime
import logging

# Set up independent logging for the backup process
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Define paths
PROJECT_DIR = r"C:\Users\anilk\ReelVault"
SOURCE_DB = os.path.join(PROJECT_DIR, "chroma_db")
BACKUP_DIR = os.path.join(PROJECT_DIR, "backups")

def run_backup():
    # Make sure the backup destination folder exists
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    if not os.path.exists(SOURCE_DB):
        logging.error("Backup failed: Source chroma_db folder does not exist yet!")
        return

    # Create a unique timestamped filename (e.g., vault_backup_20260627)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = os.path.join(BACKUP_DIR, f"vault_backup_{timestamp}")

    try:
        logging.info("Starting automated ChromaDB compression...")
        # Compresses the database folder into a clean .zip file safely
        shutil.make_archive(archive_name, 'zip', SOURCE_DB)
        logging.info(f"Backup successfully generated: {archive_name}.zip")
    except Exception as e:
        logging.error(f"Critical error during database duplication: {str(e)}")

if __name__ == "__main__":
    run_backup()