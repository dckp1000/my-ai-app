#!/bin/bash
#
# Spark Deployment Script for NBA AI App
#
# This script helps you deploy and run the NBA analysis app on Apache Spark.
#
# Usage:
#   ./deploy_spark.sh [local|cluster] [options]
#
# Modes:
#   local   - Run Spark in local mode (default)
#   cluster - Submit job to a Spark cluster
#
# Examples:
#   ./deploy_spark.sh local
#   ./deploy_spark.sh cluster --master spark://master-node:7077
#

set -e  # Exit on error

# Default configuration
MODE="${1:-local}"
SPARK_MASTER="${SPARK_MASTER:-local[*]}"
APP_NAME="NBA-Data-Analysis"
DRIVER_MEMORY="2g"
EXECUTOR_MEMORY="2g"
EXECUTOR_CORES="2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "NBA AI App - Spark Deployment Script"
echo "============================================================"
echo ""

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if PySpark is installed
check_dependencies() {
    print_info "Checking dependencies..."
    
    if ! python3 -c "import pyspark" 2>/dev/null; then
        print_error "PySpark is not installed!"
        print_info "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        print_info "PySpark is installed ✓"
    fi
}

# Check if data directory exists
check_data() {
    if [ ! -d "./data" ]; then
        print_warning "Data directory not found!"
        print_info "You may want to download NBA datasets first:"
        print_info "  python download_nba_dataset.py"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_info "Data directory found ✓"
        csv_count=$(find ./data -name "*.csv" | wc -l)
        print_info "Found $csv_count CSV file(s)"
    fi
}

# Run in local mode
run_local() {
    print_info "Running Spark application in LOCAL mode..."
    echo ""
    python3 spark_app.py
}

# Submit to cluster
run_cluster() {
    print_info "Submitting Spark application to CLUSTER..."
    
    # Parse additional arguments
    shift  # Remove first argument (mode)
    
    # Override master if provided
    if [[ "$@" == *"--master"* ]]; then
        for i in "$@"; do
            if [[ $i == spark://* ]] || [[ $i == yarn* ]] || [[ $i == mesos://* ]]; then
                SPARK_MASTER=$i
            fi
        done
    fi
    
    print_info "Spark Master: $SPARK_MASTER"
    print_info "Driver Memory: $DRIVER_MEMORY"
    print_info "Executor Memory: $EXECUTOR_MEMORY"
    print_info "Executor Cores: $EXECUTOR_CORES"
    echo ""
    
    # Check if spark-submit is available
    if ! command -v spark-submit &> /dev/null; then
        print_error "spark-submit command not found!"
        print_info "Please install Apache Spark or run in local mode."
        exit 1
    fi
    
    # Submit the job
    spark-submit \
        --master "$SPARK_MASTER" \
        --name "$APP_NAME" \
        --driver-memory "$DRIVER_MEMORY" \
        --executor-memory "$EXECUTOR_MEMORY" \
        --executor-cores "$EXECUTOR_CORES" \
        --conf spark.sql.adaptive.enabled=true \
        --conf spark.sql.adaptive.coalescePartitions.enabled=true \
        spark_app.py
}

# Show usage
show_usage() {
    echo "Usage: $0 [local|cluster] [options]"
    echo ""
    echo "Modes:"
    echo "  local   - Run Spark in local mode (default)"
    echo "  cluster - Submit job to a Spark cluster"
    echo ""
    echo "Environment Variables:"
    echo "  SPARK_MASTER       - Spark master URL (default: local[*])"
    echo "  NBA_DATA_PATH      - Path to NBA data (default: ./data)"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  $0 cluster --master spark://master-node:7077"
    echo "  SPARK_MASTER=yarn $0 cluster"
    exit 1
}

# Main execution
main() {
    # Check for help flag
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_usage
    fi
    
    # Run checks
    check_dependencies
    check_data
    
    echo ""
    print_info "Deployment mode: $MODE"
    echo ""
    
    # Execute based on mode
    case "$MODE" in
        local)
            run_local
            ;;
        cluster)
            run_cluster "$@"
            ;;
        *)
            print_error "Invalid mode: $MODE"
            show_usage
            ;;
    esac
    
    echo ""
    print_info "Deployment complete!"
}

# Run main function
main "$@"
