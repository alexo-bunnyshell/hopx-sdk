#!/bin/bash

# Test runner script for Hopx Python SDK
# Usage: ./run_tests.sh [options]

# Don't exit on error - we want to capture test results
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
VERBOSE=false
COVERAGE=false
PARALLEL=false
MARKERS=""
TEST_PATH=""
FAIL_FAST=false
OUTPUT_REPORT=false
REPORT_DIR="../local/reports"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -m|--marker)
            MARKERS="$2"
            shift 2
            ;;
        -k|--keyword)
            KEYWORD="$2"
            shift 2
            ;;
        -f|--fail-fast)
            FAIL_FAST=true
            shift
            ;;
        -r|--report)
            OUTPUT_REPORT=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -t, --type TYPE       Test type: all, integration, e2e (default: all)"
            echo "  -v, --verbose         Verbose output"
            echo "  -c, --coverage        Generate coverage report"
            echo "  -p, --parallel        Run tests in parallel"
            echo "  -m, --marker MARKER   Run tests with specific marker (e.g., 'integration')"
            echo "  -k, --keyword KEYWORD Run tests matching keyword"
            echo "  -f, --fail-fast       Stop on first failure"
            echo "  -r, --report          Generate test reports in local/reports"
            echo "  -h, --help            Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run all tests"
            echo "  $0 -t integration                    # Run only integration tests"
            echo "  $0 -t e2e                            # Run only E2E tests"
            echo "  $0 -m integration -k sandbox         # Run integration tests matching 'sandbox'"
            echo "  $0 -c -r                             # Run with coverage and reports"
            echo "  $0 -p -t integration                 # Run integration tests in parallel"
            exit 0
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Please run this script from the python/ directory.${NC}"
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed. Please install it with: pip install pytest${NC}"
    exit 1
fi

# Check for API key
if [ -z "$HOPX_API_KEY" ]; then
    echo -e "${YELLOW}Warning: HOPX_API_KEY environment variable is not set.${NC}"
    echo -e "${YELLOW}Some tests may be skipped.${NC}"
    echo ""
fi

# Build pytest command
PYTEST_CMD="pytest"

# Set test path based on type
case $TEST_TYPE in
    integration)
        TEST_PATH="tests/integration"
        RUN_E2E=false
        ;;
    e2e)
        TEST_PATH="tests/e2e"
        RUN_E2E=false
        ;;
    all)
        # When running all tests, integration tests run first, then E2E
        TEST_PATH="tests/integration"
        RUN_E2E=true
        ;;
    *)
        if [ -z "$TEST_PATH" ]; then
            TEST_PATH="tests"
            RUN_E2E=false
        else
            RUN_E2E=false
        fi
        ;;
esac

# Add custom test path if provided
if [ -n "$TEST_PATH" ] && [ "$TEST_TYPE" != "all" ] && [ "$TEST_TYPE" != "integration" ] && [ "$TEST_TYPE" != "e2e" ]; then
    TEST_PATH="tests/$TEST_PATH"
    RUN_E2E=false
fi

# Build pytest arguments
PYTEST_ARGS=()

# Verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS+=("-v")
else
    PYTEST_ARGS+=("-q")
fi

# Coverage
if [ "$COVERAGE" = true ]; then
    if ! python -c "import coverage" 2>/dev/null; then
        echo -e "${YELLOW}Warning: coverage package not installed. Installing...${NC}"
        pip install coverage pytest-cov
    fi
    PYTEST_ARGS+=("--cov=hopx_ai" "--cov-report=html" "--cov-report=term")
fi

# Parallel execution
if [ "$PARALLEL" = true ]; then
    if ! python -c "import xdist" 2>/dev/null; then
        echo -e "${YELLOW}Warning: pytest-xdist not installed. Installing...${NC}"
        pip install pytest-xdist
    fi
    PYTEST_ARGS+=("-n" "auto")
fi

# Markers
if [ -n "$MARKERS" ]; then
    PYTEST_ARGS+=("-m" "$MARKERS")
fi

# Keyword filter
if [ -n "$KEYWORD" ]; then
    PYTEST_ARGS+=("-k" "$KEYWORD")
fi

# Fail fast
if [ "$FAIL_FAST" = true ]; then
    PYTEST_ARGS+=("-x")
fi

# Output reports
if [ "$OUTPUT_REPORT" = true ]; then
    mkdir -p "$REPORT_DIR"
    PYTEST_ARGS+=("--tb=short" "--junitxml=$REPORT_DIR/junit.xml")
    REPORT_FILE="$REPORT_DIR/pytest_output.txt"
else
    REPORT_FILE="/dev/null"
fi

# Add test path
PYTEST_ARGS+=("$TEST_PATH")

# Print configuration
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Hopx Python SDK Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Test Type: ${GREEN}$TEST_TYPE${NC}"
echo -e "Test Path: ${GREEN}$TEST_PATH${NC}"
echo -e "Verbose: ${GREEN}$VERBOSE${NC}"
echo -e "Coverage: ${GREEN}$COVERAGE${NC}"
echo -e "Parallel: ${GREEN}$PARALLEL${NC}"
if [ -n "$MARKERS" ]; then
    echo -e "Markers: ${GREEN}$MARKERS${NC}"
fi
if [ -n "$KEYWORD" ]; then
    echo -e "Keyword: ${GREEN}$KEYWORD${NC}"
fi
if [ "$OUTPUT_REPORT" = true ]; then
    echo -e "Reports: ${GREEN}$REPORT_DIR${NC}"
fi
echo ""

# Run tests
echo -e "${BLUE}Running tests...${NC}"
echo ""

START_TIME=$(date +%s)
INTEGRATION_RESULT=0
E2E_RESULT=0

# Run integration tests first (or specified test type)
if [ "$TEST_TYPE" = "all" ] || [ "$TEST_TYPE" = "integration" ] || [ -z "$TEST_TYPE" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running Integration Tests${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Build integration test args (replace last element with integration path)
    INTEGRATION_ARGS=()
    for i in "${!PYTEST_ARGS[@]}"; do
        if [ $i -eq $((${#PYTEST_ARGS[@]} - 1)) ]; then
            INTEGRATION_ARGS+=("tests/integration")
        else
            INTEGRATION_ARGS+=("${PYTEST_ARGS[$i]}")
        fi
    done
    
    if [ "$OUTPUT_REPORT" = true ]; then
        INTEGRATION_REPORT="$REPORT_DIR/integration_pytest_output.txt"
        if $PYTEST_CMD "${INTEGRATION_ARGS[@]}" 2>&1 | tee "$INTEGRATION_REPORT"; then
            INTEGRATION_RESULT=0
        else
            INTEGRATION_RESULT=$?
        fi
    else
        if $PYTEST_CMD "${INTEGRATION_ARGS[@]}"; then
            INTEGRATION_RESULT=0
        else
            INTEGRATION_RESULT=$?
        fi
    fi
    
    echo ""
    if [ $INTEGRATION_RESULT -eq 0 ]; then
        echo -e "${GREEN}✓ Integration tests passed${NC}"
    else
        echo -e "${RED}✗ Integration tests failed${NC}"
        if [ "$FAIL_FAST" = true ]; then
            echo -e "${YELLOW}Stopping due to --fail-fast flag${NC}"
            TEST_RESULT=$INTEGRATION_RESULT
            END_TIME=$(date +%s)
            DURATION=$((END_TIME - START_TIME))
            # Skip to results section
            RUN_E2E=false
        fi
    fi
    echo ""
fi

# Run E2E tests after integration tests (if running all tests)
if [ "$RUN_E2E" = true ] && [ $INTEGRATION_RESULT -eq 0 ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running E2E Tests${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Build E2E test args (replace last element with e2e path)
    E2E_ARGS=()
    for i in "${!PYTEST_ARGS[@]}"; do
        if [ $i -eq $((${#PYTEST_ARGS[@]} - 1)) ]; then
            E2E_ARGS+=("tests/e2e")
        else
            E2E_ARGS+=("${PYTEST_ARGS[$i]}")
        fi
    done
    
    if [ "$OUTPUT_REPORT" = true ]; then
        E2E_REPORT="$REPORT_DIR/e2e_pytest_output.txt"
        if $PYTEST_CMD "${E2E_ARGS[@]}" 2>&1 | tee "$E2E_REPORT"; then
            E2E_RESULT=0
        else
            E2E_RESULT=$?
        fi
    else
        if $PYTEST_CMD "${E2E_ARGS[@]}"; then
            E2E_RESULT=0
        else
            E2E_RESULT=$?
        fi
    fi
    
    echo ""
    if [ $E2E_RESULT -eq 0 ]; then
        echo -e "${GREEN}✓ E2E tests passed${NC}"
    else
        echo -e "${RED}✗ E2E tests failed${NC}"
    fi
    echo ""
elif [ "$RUN_E2E" = true ] && [ $INTEGRATION_RESULT -ne 0 ]; then
    echo -e "${YELLOW}Skipping E2E tests due to integration test failures${NC}"
    echo ""
fi

# Determine overall result
if [ "$TEST_TYPE" = "all" ]; then
    if [ $INTEGRATION_RESULT -eq 0 ] && [ $E2E_RESULT -eq 0 ]; then
        TEST_RESULT=0
    else
        TEST_RESULT=1
    fi
elif [ "$TEST_TYPE" = "integration" ]; then
    TEST_RESULT=$INTEGRATION_RESULT
elif [ "$TEST_TYPE" = "e2e" ]; then
    TEST_RESULT=$E2E_RESULT
else
    # For custom paths, run normally
    if [ "$OUTPUT_REPORT" = true ]; then
        if $PYTEST_CMD "${PYTEST_ARGS[@]}" 2>&1 | tee "$REPORT_FILE"; then
            TEST_RESULT=0
        else
            TEST_RESULT=$?
        fi
    else
        if $PYTEST_CMD "${PYTEST_ARGS[@]}"; then
            TEST_RESULT=0
        else
            TEST_RESULT=$?
        fi
    fi
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${BLUE}========================================${NC}"

# Print results
if [ "$TEST_TYPE" = "all" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Test Summary${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    if [ $INTEGRATION_RESULT -eq 0 ]; then
        echo -e "Integration Tests: ${GREEN}✓ PASSED${NC}"
    else
        echo -e "Integration Tests: ${RED}✗ FAILED${NC}"
    fi
    if [ "$RUN_E2E" = true ]; then
        if [ $E2E_RESULT -eq 0 ]; then
            echo -e "E2E Tests:         ${GREEN}✓ PASSED${NC}"
        else
            echo -e "E2E Tests:         ${RED}✗ FAILED${NC}"
        fi
    fi
    echo ""
fi

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo -e "Duration: ${GREEN}${DURATION}s${NC}"
    
    if [ "$OUTPUT_REPORT" = true ]; then
        echo -e "Reports saved to: ${GREEN}$REPORT_DIR${NC}"
        
        # Generate summary report if report generation script exists
        if [ -f "$REPORT_DIR/generate_reports.py" ]; then
            echo -e "${BLUE}Generating detailed reports...${NC}"
            cd "$REPORT_DIR"
            python generate_reports.py 2>/dev/null || true
            cd "$SCRIPT_DIR"
        fi
    fi
else
    echo -e "${RED}✗ Some tests failed!${NC}"
    echo -e "Duration: ${RED}${DURATION}s${NC}"
    
    if [ "$OUTPUT_REPORT" = true ]; then
        echo -e "Reports saved to: ${GREEN}$REPORT_DIR${NC}"
        if [ "$TEST_TYPE" = "all" ]; then
            if [ $INTEGRATION_RESULT -ne 0 ]; then
                echo -e "Integration test report: ${YELLOW}$REPORT_DIR/integration_pytest_output.txt${NC}"
            fi
            if [ "$RUN_E2E" = true ] && [ $E2E_RESULT -ne 0 ]; then
                echo -e "E2E test report: ${YELLOW}$REPORT_DIR/e2e_pytest_output.txt${NC}"
            fi
        else
            echo -e "Check ${YELLOW}$REPORT_FILE${NC} for details"
        fi
    fi
fi

echo -e "${BLUE}========================================${NC}"
echo ""

exit $TEST_RESULT

