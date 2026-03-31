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

> **Note:** `requirements.txt` is a generated pinned lock file. Do not edit it directly — edit `requirements.in` instead (see [Updating Dependencies](#updating-dependencies) below).

## Updating Dependencies

`requirements.in` is the source of truth for top-level dependencies. `requirements.txt` is auto-generated from it using [pip-tools](https://pip-tools.readthedocs.io/).

To update dependencies after editing `requirements.in`:

```bash
pip install pip-tools
pip-compile requirements.in -o requirements.txt --no-emit-index-url --strip-extras
```

Commit both `requirements.in` and the updated `requirements.txt`.

## Usage

### Running the AI Chatbot

Set your OpenAI API key as an environment variable (recommended for better security):
```bash
export OPENAI_API_KEY="your-api-key-here"
python app.py
```

Alternatively, you can edit `app.py` and replace `YOUR_API_KEY` with your actual key.

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

- **For the AI chatbot**: 
  - Recommended: Set the `OPENAI_API_KEY` environment variable with your OpenAI API key
  - Alternative: Replace `YOUR_API_KEY` in `app.py` with your OpenAI API key
- **For Kaggle downloads**: Set up `kaggle.json` as described above

## Performance Improvements

This application has been optimized for better performance:
- **app.py**: OpenAI client is initialized once at module level, reducing overhead on each API call
- **download_nba_dataset.py**: Uses efficient file system operations (`os.scandir`) to reduce system calls when listing downloaded files 
