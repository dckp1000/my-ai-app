# my-ai-app
Simple copilot 

## Features
- AI chatbot using OpenAI GPT
- NBA dataset downloader from Kaggle
- **Apache Spark integration for big data processing and analytics**

**📘 New to downloading from Kaggle? Check out the [Quick Start Guide](QUICKSTART.md)!**


## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

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

### Running Spark Analytics on NBA Data

**New!** Analyze NBA datasets at scale using Apache Spark.

#### Option 1: Quick Deploy (Recommended)

Use the deployment script for easy setup:

```bash
# Run in local mode (no cluster needed)
./deploy_spark.sh local

# Or submit to a Spark cluster
./deploy_spark.sh cluster --master spark://master-node:7077
```

The deployment script will:
- Check and install dependencies automatically
- Verify NBA data is available
- Run the Spark analysis application
- Display comprehensive analytics on your NBA datasets

#### Option 2: Manual Spark Execution

Run the Spark application directly:

```bash
# Local mode with all available cores
python spark_app.py

# Or use spark-submit with custom configuration
spark-submit \
  --master local[4] \
  --driver-memory 2g \
  --executor-memory 2g \
  --properties-file spark_config.conf \
  spark_app.py
```

#### Option 3: Deploy to Spark Cluster

For production deployments on a Spark cluster:

```bash
spark-submit \
  --master spark://master:7077 \
  --deploy-mode cluster \
  --driver-memory 2g \
  --executor-memory 2g \
  --executor-cores 2 \
  --properties-file spark_config.conf \
  spark_app.py
```

**Supported Cluster Managers:**
- Standalone Spark cluster
- Apache YARN
- Apache Mesos
- Kubernetes

#### What the Spark App Does

The Spark application (`spark_app.py`) performs:
- **Data Discovery**: Automatically finds and loads NBA CSV datasets
- **Statistical Analysis**: Calculates averages, min/max values, and distributions
- **Team Analytics**: Aggregates statistics by team
- **Season Trends**: Analyzes data across different seasons
- **Performance Optimization**: Uses Spark's adaptive query execution

#### Spark Configuration

Customize Spark settings by editing `spark_config.conf` or using environment variables:

```bash
# Set custom data path
export NBA_DATA_PATH=/path/to/nba/data

# Set Spark master URL
export SPARK_MASTER=spark://master:7077

# Run with custom settings
./deploy_spark.sh cluster
```

Key configuration options in `spark_config.conf`:
- Memory allocation (driver and executor)
- Adaptive query execution settings
- Shuffle and parallelism tuning
- Serialization and compression options

## Configuration

- **For the AI chatbot**: 
  - Recommended: Set the `OPENAI_API_KEY` environment variable with your OpenAI API key
  - Alternative: Replace `YOUR_API_KEY` in `app.py` with your OpenAI API key
- **For Kaggle downloads**: Set up `kaggle.json` as described above
- **For Spark analytics**:
  - Set `NBA_DATA_PATH` environment variable to specify data location (default: `./data`)
  - Set `SPARK_MASTER` environment variable for cluster deployments (default: `local[*]`)
  - Customize settings in `spark_config.conf` for advanced tuning

## Performance Improvements

This application has been optimized for better performance:
- **app.py**: OpenAI client is initialized once at module level, reducing overhead on each API call
- **download_nba_dataset.py**: Uses efficient file system operations (`os.scandir`) to reduce system calls when listing downloaded files 
