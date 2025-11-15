"""
Script to download NBA datasets from Kaggle.

This script helps you download NBA datasets from Kaggle.
Before running, ensure you have:
1. A Kaggle account
2. Kaggle API credentials (kaggle.json) set up

Setup Instructions:
1. Go to https://www.kaggle.com/account
2. Scroll to API section and click "Create New API Token"
3. Place the downloaded kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\\Users\\<username>\\.kaggle\\ (Windows)
4. Run: chmod 600 ~/.kaggle/kaggle.json (Linux/Mac only)
"""

import os
import sys

def download_nba_dataset(dataset_name=None):
    """
    Download NBA dataset from Kaggle.
    
    Args:
        dataset_name: Kaggle dataset identifier (e.g., 'nathanlauga/nba-games')
                     If None, shows available popular NBA datasets
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("Error: kaggle package not installed.")
        print("Install it with: pip install kaggle")
        sys.exit(1)
    
    # Popular NBA datasets on Kaggle
    popular_datasets = {
        '1': {
            'name': 'nathanlauga/nba-games',
            'description': 'NBA Games Data (games, teams, players stats)'
        },
        '2': {
            'name': 'wyattowalsh/basketball',
            'description': 'Basketball Dataset (comprehensive NBA data)'
        },
        '3': {
            'name': 'justinas/nba-players-data',
            'description': 'NBA Players Data (1996-2021)'
        },
        '4': {
            'name': 'drgilermo/nba-players-stats',
            'description': 'NBA Players Stats (seasons data)'
        },
        '5': {
            'name': 'schmadam97/nba-regular-season-stats-20182019',
            'description': 'NBA Regular Season Stats 2018-2019'
        }
    }
    
    if dataset_name is None:
        print("\nPopular NBA Datasets on Kaggle:")
        print("=" * 60)
        for key, dataset in popular_datasets.items():
            print(f"{key}. {dataset['name']}")
            print(f"   {dataset['description']}")
            print()
        
        choice = input("Enter the number of the dataset you want to download (or 'custom' to enter a custom dataset): ").strip()
        
        if choice.lower() == 'custom':
            dataset_name = input("Enter the Kaggle dataset identifier (e.g., 'username/dataset-name'): ").strip()
        elif choice in popular_datasets:
            dataset_name = popular_datasets[choice]['name']
        else:
            print("Invalid choice.")
            sys.exit(1)
    
    print(f"\nDownloading dataset: {dataset_name}")
    print("=" * 60)
    
    try:
        # Initialize Kaggle API
        api = KaggleApi()
        api.authenticate()
        
        # Create data directory if it doesn't exist
        data_dir = './data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"Created directory: {data_dir}")
        
        # Download dataset
        print(f"Downloading to: {data_dir}")
        api.dataset_download_files(dataset_name, path=data_dir, unzip=True)
        
        print("\n✓ Dataset downloaded successfully!")
        print(f"Location: {os.path.abspath(data_dir)}")
        
        # List downloaded files
        print("\nDownloaded files:")
        for file in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  - {file} ({size:,} bytes)")
        
    except Exception as e:
        print(f"\n✗ Error downloading dataset: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you have set up Kaggle API credentials")
        print("2. Place kaggle.json in ~/.kaggle/ directory")
        print("3. Run: chmod 600 ~/.kaggle/kaggle.json (Linux/Mac)")
        print("4. Verify the dataset name is correct")
        sys.exit(1)

if __name__ == "__main__":
    # Check if dataset name is provided as command line argument
    if len(sys.argv) > 1:
        dataset_name = sys.argv[1]
        download_nba_dataset(dataset_name)
    else:
        download_nba_dataset()
