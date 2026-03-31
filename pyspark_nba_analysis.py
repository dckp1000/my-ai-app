"""
PySpark NBA Dataset Analysis

This script processes NBA datasets using Apache Spark.
It demonstrates best practices and common fixes for PySpark applications.

Usage:
    spark-submit pyspark_nba_analysis.py [--data-dir ./data]
"""

import os
import sys
import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)


# ---------------------------------------------------------------------------
# Schema definitions (explicit schemas avoid costly auto-inference on large
# files and make the contract with the data source clear).
# ---------------------------------------------------------------------------

GAMES_SCHEMA = StructType(
    [
        StructField("GAME_DATE_EST", StringType(), True),
        StructField("GAME_ID", IntegerType(), True),
        StructField("GAME_STATUS_TEXT", StringType(), True),
        StructField("HOME_TEAM_ID", IntegerType(), True),
        StructField("VISITOR_TEAM_ID", IntegerType(), True),
        StructField("SEASON", IntegerType(), True),
        StructField("PTS_home", IntegerType(), True),
        StructField("FG_PCT_home", DoubleType(), True),
        StructField("FT_PCT_home", DoubleType(), True),
        StructField("FG3_PCT_home", DoubleType(), True),
        StructField("AST_home", IntegerType(), True),
        StructField("REB_home", IntegerType(), True),
        StructField("PTS_away", IntegerType(), True),
        StructField("FG_PCT_away", DoubleType(), True),
        StructField("FT_PCT_away", DoubleType(), True),
        StructField("FG3_PCT_away", DoubleType(), True),
        StructField("AST_away", IntegerType(), True),
        StructField("REB_away", IntegerType(), True),
        StructField("HOME_TEAM_WINS", IntegerType(), True),
    ]
)

TEAMS_SCHEMA = StructType(
    [
        StructField("LEAGUE_ID", IntegerType(), True),
        StructField("TEAM_ID", IntegerType(), True),
        StructField("MIN_YEAR", IntegerType(), True),
        StructField("MAX_YEAR", IntegerType(), True),
        StructField("ABBREVIATION", StringType(), True),
        StructField("NICKNAME", StringType(), True),
        StructField("YEARFOUNDED", IntegerType(), True),
        StructField("CITY", StringType(), True),
        StructField("ARENA", StringType(), True),
        StructField("ARENACAPACITY", IntegerType(), True),
        StructField("OWNER", StringType(), True),
        StructField("GENERALMANAGER", StringType(), True),
        StructField("HEADCOACH", StringType(), True),
        StructField("DLEAGUEAFFILIATION", StringType(), True),
    ]
)


def build_spark_session(app_name: str = "NBA Analysis") -> SparkSession:
    """
    Build and return a configured SparkSession.

    Fix: Use getOrCreate() so that the session is reused when running in an
    environment that already has an active session (e.g., Jupyter, Databricks).
    """
    return (
        SparkSession.builder.appName(app_name)
        # Fix: Limit driver memory explicitly to avoid OOM on large datasets.
        .config("spark.driver.memory", "2g")
        # Fix: Enable Arrow-based columnar data transfers for pandas interop.
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        # Fix: Disable auto-broadcast for very large lookups; set a reasonable
        #      threshold instead of the default 10 MB.
        .config("spark.sql.autoBroadcastJoinThreshold", "20971520")
        .getOrCreate()
    )


def load_csv(spark: SparkSession, path: str, schema: StructType):
    """
    Load a CSV file with an explicit schema.

    Fix: Always supply a schema rather than relying on inferSchema=True.
    Inference triggers an extra full scan of the data and can produce
    incorrect types (e.g., integer columns inferred as strings).
    """
    return (
        spark.read.format("csv")
        .option("header", "true")
        .option("nullValue", "")
        .option("mode", "PERMISSIVE")
        .schema(schema)
        .load(path)
    )


def analyze_home_advantage(games_df):
    """
    Calculate home-team win percentage per season.

    Fix: Use DataFrame aggregation instead of collect() + Python loops.
    Collecting all rows to the driver is expensive and can cause OOM on large
    datasets.  Push the computation down to the Spark executors.
    """
    return (
        games_df.filter(F.col("HOME_TEAM_WINS").isNotNull())
        .groupBy("SEASON")
        .agg(
            F.count("*").alias("total_games"),
            F.sum("HOME_TEAM_WINS").alias("home_wins"),
            F.round(F.avg("HOME_TEAM_WINS") * 100, 2).alias("home_win_pct"),
        )
        .orderBy("SEASON")
    )


def top_scoring_teams(games_df, teams_df, season: int, top_n: int = 10):
    """
    Return the top-N highest-scoring home teams for a given season.

    Fix: Broadcast the small teams lookup table so Spark avoids a costly
    shuffle-based join.  teams_df is typically a few KB; broadcasting it
    eliminates the shuffle entirely.
    """
    season_games = games_df.filter(
        F.col("SEASON") == season
    ).select(
        "HOME_TEAM_ID",
        F.col("PTS_home").alias("pts"),
    )

    avg_pts = season_games.groupBy("HOME_TEAM_ID").agg(
        F.round(F.avg("pts"), 2).alias("avg_pts_home"),
        F.count("*").alias("games_played"),
    )

    # Fix: Broadcast the small DataFrame; avoids a full shuffle join.
    result = avg_pts.join(
        F.broadcast(teams_df.select("TEAM_ID", "NICKNAME", "CITY")),
        avg_pts["HOME_TEAM_ID"] == teams_df["TEAM_ID"],
        how="left",
    ).select(
        "CITY",
        "NICKNAME",
        "avg_pts_home",
        "games_played",
    ).orderBy(
        F.desc("avg_pts_home")
    ).limit(top_n)

    return result


def shooting_efficiency(games_df, season: int):
    """
    Compare average FG%, 3P%, and FT% between home and away teams.

    Fix: Filter out rows where percentage columns are null before averaging.
    A null percentage means the stat was not recorded (e.g. game postponed),
    which is different from a 0% value (all shots missed).  Dropping those
    rows keeps the averages meaningful rather than deflating them.
    """
    season_df = games_df.filter(F.col("SEASON") == season)

    # Fix: Drop rows with null shooting percentages so averages are not
    #      artificially deflated.  This is preferable to filling with 0,
    #      which would conflate "no data" with "all attempts missed".
    filled = season_df.dropna(
        subset=[
            "FG_PCT_home", "FT_PCT_home", "FG3_PCT_home",
            "FG_PCT_away", "FT_PCT_away", "FG3_PCT_away",
        ],
    )

    return filled.agg(
        F.round(F.avg("FG_PCT_home"), 4).alias("avg_fg_pct_home"),
        F.round(F.avg("FG3_PCT_home"), 4).alias("avg_fg3_pct_home"),
        F.round(F.avg("FT_PCT_home"), 4).alias("avg_ft_pct_home"),
        F.round(F.avg("FG_PCT_away"), 4).alias("avg_fg_pct_away"),
        F.round(F.avg("FG3_PCT_away"), 4).alias("avg_fg3_pct_away"),
        F.round(F.avg("FT_PCT_away"), 4).alias("avg_ft_pct_away"),
    )


def save_results(df, output_path: str, fmt: str = "parquet") -> None:
    """
    Persist a DataFrame to disk.

    Fix: Use coalesce(1) only for small result sets.  On large DataFrames,
    repartition to an appropriate number of files and avoid collecting
    everything to a single partition.
    """
    df.write.mode("overwrite").format(fmt).save(output_path)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="PySpark NBA Analysis")
    parser.add_argument(
        "--data-dir",
        default="./data",
        help="Directory containing NBA CSV files (default: ./data)",
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Directory to write analysis results (default: ./output)",
    )
    parser.add_argument(
        "--season",
        type=int,
        default=2019,
        help="Season year to analyze (default: 2019)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    data_dir = args.data_dir
    output_dir = args.output_dir
    season = args.season

    # Fix: Always wrap the main logic in try/finally so that the SparkSession
    #      is stopped even if an exception is raised.  Leaving a session open
    #      leaks resources and can block subsequent runs.
    spark = build_spark_session()
    games_df = None
    teams_df = None
    try:
        games_path = os.path.join(data_dir, "games.csv")
        teams_path = os.path.join(data_dir, "teams.csv")

        if not os.path.exists(games_path):
            print(
                f"Error: games.csv not found at '{games_path}'.\n"
                "Run download_nba_dataset.py first to fetch the data.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Load data
        games_df = load_csv(spark, games_path, GAMES_SCHEMA)
        teams_df = (
            load_csv(spark, teams_path, TEAMS_SCHEMA)
            if os.path.exists(teams_path)
            else None
        )

        # Fix: Cache DataFrames that are reused in multiple actions.  Without
        #      caching, Spark re-reads and re-parses the CSV on every action.
        games_df.cache()
        if teams_df is not None:
            teams_df.cache()

        print("\n=== Home Advantage by Season ===")
        home_adv = analyze_home_advantage(games_df)
        home_adv.show(truncate=False)
        save_results(home_adv, os.path.join(output_dir, "home_advantage"))

        print(f"\n=== Shooting Efficiency (Season {season}) ===")
        efficiency = shooting_efficiency(games_df, season)
        efficiency.show(truncate=False)
        save_results(efficiency, os.path.join(output_dir, "shooting_efficiency"))

        if teams_df is not None:
            print(f"\n=== Top-10 Scoring Teams (Season {season}) ===")
            top_teams = top_scoring_teams(games_df, teams_df, season)
            top_teams.show(truncate=False)
            save_results(top_teams, os.path.join(output_dir, "top_scoring_teams"))

        print(f"\nResults written to: {os.path.abspath(output_dir)}")

    finally:
        # Fix: Unpersist cached DataFrames before stopping the session to free
        #      executor memory promptly, which matters in shared cluster envs.
        if games_df is not None:
            games_df.unpersist()
        if teams_df is not None:
            teams_df.unpersist()
        # Fix: Stop the session explicitly to release cluster / local resources.
        spark.stop()


if __name__ == "__main__":
    main()
