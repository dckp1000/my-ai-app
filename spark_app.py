"""
Spark application for processing NBA datasets.

This application demonstrates how to use Apache Spark to analyze NBA data.
It can be run locally or deployed to a Spark cluster.

Usage:
    # Run locally
    python spark_app.py

    # Submit to Spark cluster
    spark-submit --master spark://master:7077 spark_app.py
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, max as spark_max, min as spark_min


def create_spark_session(app_name="NBA Data Analysis"):
    """
    Create and configure Spark session.
    
    Args:
        app_name: Name of the Spark application
        
    Returns:
        SparkSession instance
    """
    spark = (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .getOrCreate()
    )
    
    return spark


def analyze_nba_games(spark, data_path="./data"):
    """
    Analyze NBA games data using Spark.
    
    Args:
        spark: SparkSession instance
        data_path: Path to the data directory
    """
    print("\n" + "=" * 60)
    print("NBA Data Analysis with Apache Spark")
    print("=" * 60)
    
    # Check if data directory exists
    if not os.path.exists(data_path):
        print(f"\nError: Data directory '{data_path}' not found.")
        print("Please run 'python download_nba_dataset.py' first to download NBA data.")
        return
    
    # Find CSV files in data directory
    csv_files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"\nNo CSV files found in '{data_path}'.")
        print("Please run 'python download_nba_dataset.py' to download NBA datasets.")
        return
    
    print(f"\nFound {len(csv_files)} CSV file(s) in '{data_path}':")
    for csv_file in csv_files:
        print(f"  - {csv_file}")
    
    # Process each CSV file
    for csv_file in csv_files:
        file_path = os.path.join(data_path, csv_file)
        print(f"\n{'=' * 60}")
        print(f"Analyzing: {csv_file}")
        print("=" * 60)
        
        try:
            # Read CSV file
            df = spark.read.csv(file_path, header=True, inferSchema=True)
            
            # Cache the DataFrame to avoid expensive multiple scans
            df.cache()
            
            try:
                # Basic statistics
                print(f"\nDataset Info:")
                print(f"  Total rows: {df.count():,}")
                print(f"  Total columns: {len(df.columns)}")
                
                print(f"\nColumns:")
                for column_name in df.columns:
                    print(f"  - {column_name}")
                
                # Show sample data
                print(f"\nSample Data (first 5 rows):")
                df.show(5, truncate=False)
                
                # Perform analysis based on available columns
                analyze_dataset_columns(df, csv_file)
            finally:
                # Unpersist the DataFrame after use, even if an error occurs
                df.unpersist()
            
        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")


def analyze_dataset_columns(df, filename):
    """
    Perform analysis based on available columns in the dataset.
    
    Args:
        df: Spark DataFrame
        filename: Name of the file being analyzed
    """
    # Create case-insensitive column mapping
    column_map = {col_name.lower(): col_name for col_name in df.columns}
    columns_lower = list(column_map.keys())
    
    # Analyze games data
    if 'pts' in columns_lower or 'points' in columns_lower:
        print("\n--- Points Analysis ---")
        pts_col_lower = 'pts' if 'pts' in columns_lower else 'points'
        pts_col = column_map[pts_col_lower]
        
        stats = df.select(
            avg(col(pts_col)).alias('avg_points'),
            spark_max(col(pts_col)).alias('max_points'),
            spark_min(col(pts_col)).alias('min_points')
        ).collect()[0]
        
        # Handle None values for empty DataFrames
        if stats['avg_points'] is not None:
            print(f"Average Points: {stats['avg_points']:.2f}")
            print(f"Maximum Points: {stats['max_points']}")
            print(f"Minimum Points: {stats['min_points']}")
        else:
            print("No data available for points analysis")
    
    # Analyze by team
    if 'team' in columns_lower or 'team_abbreviation' in columns_lower:
        team_col_lower = 'team' if 'team' in columns_lower else 'team_abbreviation'
        team_col = column_map[team_col_lower]
        print(f"\n--- Team Statistics ---")
        
        team_stats = (
            df.groupBy(team_col)
            .agg(count("*").alias("games"))
            .orderBy(col("games").desc())
            .limit(10)
        )
        
        print("Top 10 teams by number of records:")
        team_stats.show(truncate=False)
    
    # Analyze by season
    if 'season' in columns_lower or 'season_id' in columns_lower:
        season_col_lower = 'season' if 'season' in columns_lower else 'season_id'
        season_col = column_map[season_col_lower]
        print(f"\n--- Season Statistics ---")
        
        season_stats = (
            df.groupBy(season_col)
            .agg(count("*").alias("records"))
            .orderBy(season_col)
        )
        
        print("Records by season:")
        season_stats.show(truncate=False)


def run_custom_query(spark, query, data_path="./data"):
    """
    Run a custom Spark SQL query on NBA data.
    
    Args:
        spark: SparkSession instance
        query: SQL query string
        data_path: Path to the data directory
    """
    # Check if data directory exists
    if not os.path.exists(data_path):
        print(f"Error: Data directory '{data_path}' not found.")
        print("Please run 'python download_nba_dataset.py' first to download NBA data.")
        return
    
    csv_files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found.")
        return
    
    # Register first CSV as a temporary table
    csv_file = csv_files[0]
    file_path = os.path.join(data_path, csv_file)
    
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    df.createOrReplaceTempView("nba_data")
    
    print(f"\nExecuting query on '{csv_file}':")
    print(query)
    print("\nResults:")
    
    result = spark.sql(query)
    result.show()


def main():
    """Main function to run Spark NBA data analysis."""
    print("\n" + "=" * 60)
    print("NBA Data Analysis with Apache Spark")
    print("=" * 60)
    
    # Create Spark session
    print("\nInitializing Spark session...")
    spark = create_spark_session()
    
    print(f"Spark version: {spark.version}")
    print(f"Spark master: {spark.sparkContext.master}")
    
    # Analyze NBA data
    data_path = os.environ.get('NBA_DATA_PATH', './data')
    analyze_nba_games(spark, data_path)
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)
    
    # Stop Spark session
    spark.stop()


if __name__ == "__main__":
    main()
