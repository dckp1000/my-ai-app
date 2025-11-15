# Quick Start Guide: Downloading NBA Datasets from Kaggle

## Step 1: Set up Kaggle API

1. **Get your Kaggle API token:**
   - Visit https://www.kaggle.com/account
   - Scroll to the "API" section
   - Click "Create New API Token"
   - This downloads `kaggle.json`

2. **Install the token:**
   
   **On Linux/Mac:**
   ```bash
   mkdir -p ~/.kaggle
   mv ~/Downloads/kaggle.json ~/.kaggle/
   chmod 600 ~/.kaggle/kaggle.json
   ```
   
   **On Windows:**
   ```cmd
   mkdir %USERPROFILE%\.kaggle
   move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\
   ```

## Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Download NBA Dataset

**Interactive mode (recommended for first-time users):**
```bash
python download_nba_dataset.py
```

You'll see a menu like this:
```
Popular NBA Datasets on Kaggle:
============================================================
1. nathanlauga/nba-games
   NBA Games Data (games, teams, players stats)

2. wyattowalsh/basketball
   Basketball Dataset (comprehensive NBA data)

3. justinas/nba-players-data
   NBA Players Data (1996-2021)

4. drgilermo/nba-players-stats
   NBA Players Stats (seasons data)

5. schmadam97/nba-regular-season-stats-20182019
   NBA Regular Season Stats 2018-2019

Enter the number of the dataset you want to download (or 'custom' to enter a custom dataset):
```

**Direct download (if you know the dataset name):**
```bash
python download_nba_dataset.py nathanlauga/nba-games
```

## Step 4: Access your data

All datasets are downloaded to the `./data` directory in your project.

## Troubleshooting

### "Error: kaggle package not installed"
Run: `pip install kaggle`

### "Could not find kaggle.json"
Make sure you've placed the kaggle.json file in the correct location (see Step 1)

### "403 - Forbidden"
You need to accept the dataset's terms on the Kaggle website first. Visit the dataset page and accept the terms.

### Permission errors (Linux/Mac)
Make sure you've set the correct permissions: `chmod 600 ~/.kaggle/kaggle.json`
