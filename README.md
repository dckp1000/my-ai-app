# my-ai-app
Simple copilot 

## Features
- AI chatbot using OpenAI GPT
- NBA dataset downloader from Kaggle

**📘 New to downloading from Kaggle? Check out the [Quick Start Guide](QUICKSTART.md)!**


## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the AI Chatbot
```bash
python app.py
```

### Downloading NBA Datasets from Kaggle

#### Setup Kaggle API Credentials

Before downloading datasets, you need to set up Kaggle API credentials:

1. Create a Kaggle account at https://www.kaggle.com
2. Go to your account settings: https://www.kaggle.com/account
3. Scroll to the "API" section and click "Create New API Token"
4. This will download a `kaggle.json` file
5. Place the file in the appropriate location:
   - **Linux/Mac**: `~/.kaggle/kaggle.json`
   - **Windows**: `C:\Users\<username>\.kaggle\kaggle.json`
6. Set proper permissions (Linux/Mac only):
   ```bash
   chmod 600 ~/.kaggle/kaggle.json
   ```

#### Download NBA Dataset

Run the download script:
```bash
python download_nba_dataset.py
```

The script will show you a list of popular NBA datasets to choose from:
1. NBA Games Data (games, teams, players stats)
2. Basketball Dataset (comprehensive NBA data)
3. NBA Players Data (1996-2021)
4. NBA Players Stats (seasons data)
5. NBA Regular Season Stats 2018-2019

You can also download a custom dataset by providing the dataset identifier:
```bash
python download_nba_dataset.py username/dataset-name
```

Downloaded datasets will be saved in the `./data` directory.

## Configuration

- For the AI chatbot: Replace `YOUR_API_KEY` in `app.py` with your OpenAI API key
- For Kaggle downloads: Set up `kaggle.json` as described above 
