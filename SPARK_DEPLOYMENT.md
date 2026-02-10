# Spark Deployment Examples

This document provides comprehensive examples for deploying and using the NBA AI App with Apache Spark.

## Table of Contents
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Cluster Deployment](#cluster-deployment)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download NBA Data (Optional)

```bash
python download_nba_dataset.py
```

Select a dataset from the menu or provide a custom dataset identifier.

### 3. Run Spark Analysis

**Using the deployment script (recommended):**

```bash
./deploy_spark.sh local
```

**Or run directly:**

```bash
python spark_app.py
```

## Local Development

### Run in Local Mode

The easiest way to get started is to run Spark in local mode on your machine:

```bash
# Run with deployment script
./deploy_spark.sh local

# Or run Python script directly
python spark_app.py
```

### Custom Data Path

Specify a custom data directory:

```bash
export NBA_DATA_PATH=/path/to/your/nba/data
python spark_app.py
```

### Run with spark-submit

For more control over Spark configuration:

```bash
spark-submit \
  --master local[4] \
  --driver-memory 2g \
  --conf spark.sql.adaptive.enabled=true \
  spark_app.py
```

## Cluster Deployment

### Standalone Spark Cluster

Deploy to a standalone Spark cluster:

```bash
# Using deployment script
./deploy_spark.sh cluster --master spark://master-node:7077

# Or use spark-submit directly
spark-submit \
  --master spark://master-node:7077 \
  --deploy-mode client \
  --driver-memory 2g \
  --executor-memory 2g \
  --executor-cores 2 \
  --properties-file spark_config.conf \
  spark_app.py
```

### YARN Cluster

Deploy to a Hadoop YARN cluster:

```bash
# Set SPARK_MASTER environment variable
export SPARK_MASTER=yarn
./deploy_spark.sh cluster

# Or use spark-submit directly
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --driver-memory 2g \
  --executor-memory 4g \
  --num-executors 4 \
  --executor-cores 2 \
  spark_app.py
```

### Mesos Cluster

Deploy to an Apache Mesos cluster:

```bash
spark-submit \
  --master mesos://mesos-master:5050 \
  --deploy-mode cluster \
  --driver-memory 2g \
  --executor-memory 2g \
  spark_app.py
```

### Kubernetes Cluster

Deploy to a Kubernetes cluster:

```bash
spark-submit \
  --master k8s://https://kubernetes-master:8443 \
  --deploy-mode cluster \
  --name nba-spark-analysis \
  --conf spark.executor.instances=3 \
  --conf spark.kubernetes.container.image=spark:latest \
  spark_app.py
```

## Advanced Configuration

### Using Configuration File

Apply custom Spark settings using the configuration file:

```bash
spark-submit \
  --properties-file spark_config.conf \
  --master local[*] \
  spark_app.py
```

### Environment Variables

Control deployment with environment variables:

```bash
# Set Spark master
export SPARK_MASTER=spark://master:7077

# Set data path
export NBA_DATA_PATH=/data/nba

# Run deployment
./deploy_spark.sh cluster
```

### Memory Configuration

Adjust memory settings for large datasets:

```bash
spark-submit \
  --master local[*] \
  --driver-memory 4g \
  --executor-memory 8g \
  --conf spark.memory.fraction=0.8 \
  spark_app.py
```

### Performance Tuning

Optimize for large-scale data processing:

```bash
spark-submit \
  --master spark://master:7077 \
  --driver-memory 4g \
  --executor-memory 8g \
  --executor-cores 4 \
  --num-executors 10 \
  --conf spark.sql.shuffle.partitions=500 \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.sql.adaptive.coalescePartitions.enabled=true \
  --conf spark.serializer=org.apache.spark.serializer.KryoSerializer \
  spark_app.py
```

### Dynamic Allocation

Enable dynamic executor allocation for better resource utilization:

```bash
spark-submit \
  --master yarn \
  --conf spark.dynamicAllocation.enabled=true \
  --conf spark.dynamicAllocation.minExecutors=2 \
  --conf spark.dynamicAllocation.maxExecutors=20 \
  --conf spark.dynamicAllocation.initialExecutors=5 \
  spark_app.py
```

## Example Output

When you run the Spark application with NBA data, you'll see output like:

```
============================================================
NBA Data Analysis with Apache Spark
============================================================

Initializing Spark session...
Spark version: 4.1.1
Spark master: local[*]

============================================================
NBA Data Analysis with Apache Spark
============================================================

Found 3 CSV file(s) in './data':
  - games.csv
  - players.csv
  - teams.csv

============================================================
Analyzing: games.csv
============================================================

Dataset Info:
  Total rows: 26,496
  Total columns: 15

Columns:
  - game_id
  - team
  - season
  - pts
  - fg_pct
  - ft_pct
  - ...

Sample Data (first 5 rows):
[Shows sample data]

--- Points Analysis ---
Average Points: 105.67
Maximum Points: 186
Minimum Points: 54

--- Team Statistics ---
Top 10 teams by number of records:
[Shows team statistics]

--- Season Statistics ---
Records by season:
[Shows season breakdown]
```

## Troubleshooting

### Issue: "PySpark not installed"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Data directory not found"

**Solution:**
Download NBA data first:
```bash
python download_nba_dataset.py
```

### Issue: "Unable to load native-hadoop library"

This is a warning that can be safely ignored for local development. Spark will use Java implementations instead.

### Issue: "Connection refused to Spark master"

**Solution:**
- Verify the Spark master is running
- Check the master URL is correct
- Ensure network connectivity to the master node

### Issue: "Out of memory errors"

**Solution:**
Increase memory allocation:
```bash
spark-submit \
  --driver-memory 4g \
  --executor-memory 8g \
  spark_app.py
```

### Issue: "Job fails with shuffle errors"

**Solution:**
- Increase shuffle partitions
- Enable adaptive query execution

```bash
spark-submit \
  --conf spark.sql.shuffle.partitions=500 \
  --conf spark.sql.adaptive.enabled=true \
  spark_app.py
```

## Best Practices

1. **Start Local:** Test your application locally before deploying to a cluster
2. **Monitor Resources:** Use Spark UI (typically at http://localhost:4040) to monitor job execution
3. **Optimize Partitions:** Adjust `spark.sql.shuffle.partitions` based on data size
4. **Use Configuration Files:** Keep cluster-specific settings in `spark_config.conf`
5. **Enable Adaptive Execution:** Let Spark optimize queries automatically
6. **Cache Wisely:** Cache DataFrames that are used multiple times
7. **Clean Up:** Always stop the Spark session when done

## Additional Resources

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [PySpark API Reference](https://spark.apache.org/docs/latest/api/python/)
- [Spark Configuration Guide](https://spark.apache.org/docs/latest/configuration.html)
- [Spark Performance Tuning](https://spark.apache.org/docs/latest/tuning.html)
