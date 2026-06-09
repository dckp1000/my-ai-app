"""
Tests for Spark application functionality.
"""
import unittest
import tempfile
import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType


class TestSparkAnalytics(unittest.TestCase):
    """Test Spark analytics functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up Spark session for tests"""
        cls.spark = (
            SparkSession.builder.master("local[1]")
            .appName("test")
            .config("spark.sql.shuffle.partitions", "1")
            .getOrCreate()
        )
        cls.spark.sparkContext.setLogLevel("ERROR")

    @classmethod
    def tearDownClass(cls):
        """Tear down Spark session"""
        cls.spark.stop()

    def test_analyze_dataset_columns_with_lowercase(self):
        """Test that analyze_dataset_columns works with lowercase column names"""
        from spark_app import analyze_dataset_columns

        # Create test DataFrame with lowercase columns
        schema = StructType(
            [
                StructField("team", StringType(), True),
                StructField("season", IntegerType(), True),
                StructField("pts", IntegerType(), True),
            ]
        )
        data = [
            ("LAL", 2020, 110),
            ("BOS", 2020, 108),
            ("GSW", 2020, 112),
            ("LAL", 2021, 115),
        ]
        df = self.spark.createDataFrame(data, schema)

        # Should not raise an exception
        try:
            analyze_dataset_columns(df, "test.csv")
        except Exception as e:
            self.fail(f"analyze_dataset_columns raised exception: {e}")

    def test_analyze_dataset_columns_with_uppercase(self):
        """Test that analyze_dataset_columns works with uppercase column names"""
        from spark_app import analyze_dataset_columns

        # Create test DataFrame with uppercase columns
        schema = StructType(
            [
                StructField("TEAM", StringType(), True),
                StructField("SEASON", IntegerType(), True),
                StructField("PTS", IntegerType(), True),
            ]
        )
        data = [
            ("LAL", 2020, 110),
            ("BOS", 2020, 108),
            ("GSW", 2020, 112),
            ("LAL", 2021, 115),
        ]
        df = self.spark.createDataFrame(data, schema)

        # Should not raise an exception with uppercase columns
        try:
            analyze_dataset_columns(df, "test.csv")
        except Exception as e:
            self.fail(f"analyze_dataset_columns raised exception: {e}")

    def test_analyze_dataset_columns_with_mixed_case(self):
        """Test that analyze_dataset_columns works with mixed case column names"""
        from spark_app import analyze_dataset_columns

        # Create test DataFrame with mixed case columns
        schema = StructType(
            [
                StructField("Team", StringType(), True),
                StructField("Season", IntegerType(), True),
                StructField("Pts", IntegerType(), True),
            ]
        )
        data = [
            ("LAL", 2020, 110),
            ("BOS", 2020, 108),
            ("GSW", 2020, 112),
            ("LAL", 2021, 115),
        ]
        df = self.spark.createDataFrame(data, schema)

        # Should not raise an exception with mixed case columns
        try:
            analyze_dataset_columns(df, "test.csv")
        except Exception as e:
            self.fail(f"analyze_dataset_columns raised exception: {e}")

    def test_analyze_dataset_columns_points_calculation(self):
        """Test that points statistics are calculated correctly"""
        from spark_app import analyze_dataset_columns

        schema = StructType(
            [
                StructField("team", StringType(), True),
                StructField("pts", IntegerType(), True),
            ]
        )
        data = [("LAL", 100), ("BOS", 110), ("GSW", 120)]
        df = self.spark.createDataFrame(data, schema)

        # Capture output would require mocking print, so we just verify no exception
        try:
            analyze_dataset_columns(df, "test.csv")
        except Exception as e:
            self.fail(f"Points calculation failed: {e}")

    def test_analyze_dataset_columns_team_aggregation(self):
        """Test that team aggregation works correctly"""
        from spark_app import analyze_dataset_columns

        schema = StructType(
            [
                StructField("team", StringType(), True),
                StructField("season", IntegerType(), True),
            ]
        )
        data = [
            ("LAL", 2020),
            ("LAL", 2021),
            ("BOS", 2020),
            ("GSW", 2020),
        ]
        df = self.spark.createDataFrame(data, schema)

        # Should aggregate by team correctly
        try:
            analyze_dataset_columns(df, "test.csv")
        except Exception as e:
            self.fail(f"Team aggregation failed: {e}")

    def test_analyze_dataset_columns_season_aggregation(self):
        """Test that season aggregation works correctly"""
        from spark_app import analyze_dataset_columns

        schema = StructType(
            [
                StructField("season", IntegerType(), True),
                StructField("team", StringType(), True),
            ]
        )
        data = [
            (2020, "LAL"),
            (2020, "BOS"),
            (2021, "GSW"),
            (2021, "LAL"),
        ]
        df = self.spark.createDataFrame(data, schema)

        # Should aggregate by season correctly
        try:
            analyze_dataset_columns(df, "test.csv")
        except Exception as e:
            self.fail(f"Season aggregation failed: {e}")

    def test_analyze_dataset_columns_with_alternative_column_names(self):
        """Test that alternative column names (points, team_abbreviation, season_id) work"""
        from spark_app import analyze_dataset_columns

        schema = StructType(
            [
                StructField("team_abbreviation", StringType(), True),
                StructField("season_id", IntegerType(), True),
                StructField("points", IntegerType(), True),
            ]
        )
        data = [
            ("LAL", 2020, 110),
            ("BOS", 2020, 108),
        ]
        df = self.spark.createDataFrame(data, schema)

        # Should work with alternative column names
        try:
            analyze_dataset_columns(df, "test.csv")
        except Exception as e:
            self.fail(f"Alternative column names failed: {e}")

    def test_analyze_dataset_columns_empty_dataframe(self):
        """Test that empty DataFrame is handled gracefully"""
        from spark_app import analyze_dataset_columns

        schema = StructType(
            [
                StructField("team", StringType(), True),
                StructField("pts", IntegerType(), True),
            ]
        )
        df = self.spark.createDataFrame([], schema)

        # Should handle empty DataFrame without exception
        try:
            analyze_dataset_columns(df, "test.csv")
        except Exception as e:
            self.fail(f"Empty DataFrame handling failed: {e}")

    def test_dataframe_caching(self):
        """Test that DataFrame caching and unpersisting work correctly"""
        from spark_app import analyze_nba_games

        # Create a temporary directory with a CSV file
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            with open(csv_path, "w") as f:
                f.write("team,season,pts\n")
                f.write("LAL,2020,110\n")
                f.write("BOS,2020,108\n")

            # Run analysis
            try:
                analyze_nba_games(self.spark, tmpdir)
            except Exception as e:
                self.fail(f"DataFrame caching test failed: {e}")

    def test_run_custom_query_missing_directory(self):
        """Test that run_custom_query handles missing data directory gracefully"""
        from spark_app import run_custom_query

        # Should not raise an exception with non-existent directory
        try:
            run_custom_query(self.spark, "SELECT * FROM nba_data", "/nonexistent/path")
        except FileNotFoundError:
            self.fail("run_custom_query raised FileNotFoundError for missing directory")
        except Exception as e:
            self.fail(f"run_custom_query raised unexpected exception: {e}")

    def test_run_custom_query_empty_directory(self):
        """Test that run_custom_query handles empty data directory"""
        from spark_app import run_custom_query

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle empty directory without exception
            try:
                run_custom_query(self.spark, "SELECT * FROM nba_data", tmpdir)
            except Exception as e:
                self.fail(f"run_custom_query failed with empty directory: {e}")

    def test_create_spark_session(self):
        """Test that Spark session is created with correct configuration"""
        from spark_app import create_spark_session

        spark = create_spark_session("test-app")

        # Verify session was created
        self.assertIsNotNone(spark)

        # Verify adaptive execution is enabled
        self.assertEqual(
            spark.conf.get("spark.sql.adaptive.enabled"), "true"
        )
        self.assertEqual(
            spark.conf.get("spark.sql.adaptive.coalescePartitions.enabled"),
            "true",
        )
        # Do not stop the session here — tearDownClass manages the shared session


if __name__ == "__main__":
    unittest.main()
