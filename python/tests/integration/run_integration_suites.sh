#!/bin/bash
# Integration Test Orchestrator
# Runs integration tests in dependency-aware phases (0-8)
# This script ensures tests run in a deterministic order that reflects system behavior.

set -e  # Fail fast on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
DEBUG_MODE=false
PHASE_RANGE=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--debug)
            DEBUG_MODE=true
            shift
            ;;
        --range)
            if [[ -z "$2" ]] || [[ "$2" == -* ]]; then
                echo -e "${RED}Error: --range requires a range argument (e.g., 0-3 or 0)${NC}"
                exit 1
            fi
            PHASE_RANGE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -d, --debug         Enable debug mode (sets HOPX_TEST_DEBUG=true)"
            echo "                       This enables verbose logging, timing information,"
            echo "                       and warnings for long-running operations."
            echo "  --range RANGE       Run only specific phase(s) or range of phases"
            echo "                       Format: START-END (e.g., 0-3) or single phase (e.g., 0)"
            echo "                       Phases: 0-8 (0=Templates, 1=Auth, 2=Creation, etc.)"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Environment:"
            echo "  HOPX_API_KEY        API key for authentication (required for most tests)"
            echo "                       The script checks for the key in this order:"
            echo "                       1. Environment variable (HOPX_API_KEY)"
            echo "                       2. .env file in tests/integration/ directory"
            echo "                       3. Interactive prompt (if not found above)"
            echo "                       You can create tests/integration/.env with: HOPX_API_KEY=your_key"
            echo ""
            echo "Examples:"
            echo "  $0                      # Run all phases normally"
            echo "  $0 --debug              # Run all phases with debug output"
            echo "  $0 --range 0            # Run only phase 0 (Templates)"
            echo "  $0 --range 0-3          # Run phases 0 through 3"
            echo "  $0 --range 0 --debug    # Run phase 0 with debug output"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Set debug environment variable if flag is set
if [ "$DEBUG_MODE" = true ]; then
    export HOPX_TEST_DEBUG=true
    echo -e "${CYAN}Debug mode enabled (HOPX_TEST_DEBUG=true)${NC}"
    echo -e "${CYAN}Verbose logging and timing information will be shown${NC}\n"
fi

# Parse phase range if provided
PHASE_START=""
PHASE_END=""
if [ -n "$PHASE_RANGE" ]; then
    if [[ "$PHASE_RANGE" =~ ^([0-8])-([0-8])$ ]]; then
        PHASE_START="${BASH_REMATCH[1]}"
        PHASE_END="${BASH_REMATCH[2]}"
        if [ "$PHASE_START" -gt "$PHASE_END" ]; then
            echo -e "${RED}Error: Start phase (${PHASE_START}) must be <= end phase (${PHASE_END})${NC}"
            exit 1
        fi
        echo -e "${CYAN}Running phases ${PHASE_START} through ${PHASE_END}${NC}\n"
    elif [[ "$PHASE_RANGE" =~ ^([0-8])$ ]]; then
        PHASE_START="${BASH_REMATCH[1]}"
        PHASE_END="${BASH_REMATCH[1]}"
        echo -e "${CYAN}Running phase ${PHASE_START} only${NC}\n"
    else
        echo -e "${RED}Error: Invalid phase range format: ${PHASE_RANGE}${NC}"
        echo "Use format: START-END (e.g., 0-3) or single phase (e.g., 0)"
        exit 1
    fi
fi

# Helper function to run a phase
run_phase() {
    local phase_num=$1
    local phase_name=$2
    shift 2
    local targets=("$@")

    if [ ${#targets[@]} -eq 0 ]; then
        echo -e "${YELLOW}Phase ${phase_num} – ${phase_name}: SKIPPED (no targets)${NC}"
        return 0
    fi

    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}Phase ${phase_num} – ${phase_name}${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "Running: ${targets[*]}"
    echo ""

    # Run pytest with JUnit XML output (one file per phase, will merge later)
    PHASE_JUNIT="$JUNIT_TEMP_DIR/phase_${phase_num}.xml"
    pytest "${targets[@]}" --junitxml="$PHASE_JUNIT" -v 2>&1 | tee -a "$PYTEST_OUTPUT" || {
        echo -e "\n${RED}Phase ${phase_num} failed!${NC}"
        exit 1
    }

    echo -e "\n${GREEN}Phase ${phase_num} completed successfully${NC}\n"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Change to python directory (parent of tests/integration)
PYTHON_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PYTHON_DIR" || exit 1

# Function to load .env file
load_env_file() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        # Read .env file and export variables
        # This handles comments and empty lines
        while IFS= read -r line || [ -n "$line" ]; do
            # Skip empty lines and comments
            [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
            # Remove leading/trailing whitespace
            line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            # Export the variable if it's in KEY=VALUE format
            if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
                local key="${BASH_REMATCH[1]}"
                local value="${BASH_REMATCH[2]}"
                # Remove quotes if present
                value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
                export "$key=$value"
            fi
        done < "$env_file"
        return 0
    fi
    return 1
}

# Try to load API key from .env file in tests/integration directory
ENV_FILE="$SCRIPT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    load_env_file "$ENV_FILE"
    if [ -n "$HOPX_API_KEY" ]; then
        echo -e "${GREEN}API key loaded from .env file${NC}\n"
    fi
fi

# Check for API key and prompt if not set
if [ -z "$HOPX_API_KEY" ]; then
    echo -e "${YELLOW}HOPX_API_KEY not found in environment or .env file.${NC}"
    echo -e "${YELLOW}Some integration tests require an API key to run.${NC}"
    echo ""
    read -p "Enter your HOPX API key (or press Enter to skip): " -s API_KEY_INPUT
    echo ""
    
    if [ -n "$API_KEY_INPUT" ]; then
        export HOPX_API_KEY="$API_KEY_INPUT"
        echo -e "${GREEN}API key set successfully${NC}\n"
    else
        echo -e "${YELLOW}No API key provided. Tests requiring API access will be skipped.${NC}\n"
    fi
else
    if [ -f "$ENV_FILE" ]; then
        # Already shown message above
        :
    else
        echo -e "${GREEN}API key found in environment (HOPX_API_KEY is set)${NC}\n"
    fi
fi

# Create reports directory if it doesn't exist
REPORTS_DIR="$(cd "$PYTHON_DIR/../local/reports" && pwd)"
mkdir -p "$REPORTS_DIR"

# Generate timestamp for reports
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
JUNIT_XML="$REPORTS_DIR/junit_integration_${TIMESTAMP}.xml"
PYTEST_OUTPUT="$REPORTS_DIR/pytest_output_${TIMESTAMP}.txt"
JUNIT_TEMP_DIR="$REPORTS_DIR/junit_phases_${TIMESTAMP}"
mkdir -p "$JUNIT_TEMP_DIR"

echo -e "${GREEN}Starting Integration Test Orchestration${NC}"
echo -e "Working directory: ${PYTHON_DIR}"
echo -e "Reports directory: ${REPORTS_DIR}"
echo -e "JUnit XML: ${JUNIT_XML}"
if [ "$DEBUG_MODE" = true ]; then
    echo -e "${CYAN}Debug mode: ENABLED${NC}"
fi
echo ""

# Helper function to check if a phase should be run
should_run_phase() {
    local phase=$1
    if [ -z "$PHASE_RANGE" ]; then
        return 0  # Run all phases if no range specified
    fi
    if [ "$phase" -ge "$PHASE_START" ] && [ "$phase" -le "$PHASE_END" ]; then
        return 0  # Phase is in range
    fi
    return 1  # Phase is not in range
}

# Phase 0 – Templates and static setup
if should_run_phase 0; then
    run_phase 0 "Templates and static setup" \
        tests/integration/template \
        tests/integration/sandbox/templates
fi

# Phase 1 – Authentication
if should_run_phase 1; then
    run_phase 1 "Authentication" \
        tests/integration/sandbox/auth \
        tests/integration/async_sandbox/auth
fi

# Phase 2 – Sandbox creation
if should_run_phase 2; then
    run_phase 2 "Sandbox creation" \
        tests/integration/sandbox/creation \
        tests/integration/async_sandbox/creation
fi

# Phase 3 – Connection
if should_run_phase 3; then
    run_phase 3 "Connection" \
        tests/integration/sandbox/connection \
        tests/integration/async_sandbox/connection
fi

# Phase 4 – Basic info and listing
if should_run_phase 4; then
    run_phase 4 "Basic info and listing" \
        tests/integration/sandbox/info \
        tests/integration/sandbox/listing \
        tests/integration/async_sandbox/listing
fi

# Phase 5 – Lifecycle
if should_run_phase 5; then
    run_phase 5 "Lifecycle" \
        tests/integration/sandbox/lifecycle \
        tests/integration/async_sandbox/lifecycle
fi

# Phase 6 – Resources
if should_run_phase 6; then
    run_phase 6 "Resources" \
        tests/integration/sandbox/resources/agent_info \
        tests/integration/sandbox/resources/cache \
        tests/integration/sandbox/resources/commands \
        tests/integration/sandbox/resources/env_vars \
        tests/integration/sandbox/resources/files \
        tests/integration/async_sandbox/resources/commands \
        tests/integration/async_sandbox/resources/env_vars \
        tests/integration/async_sandbox/resources/files
fi

# Phase 7 – Code execution
if should_run_phase 7; then
    run_phase 7 "Code execution" \
        tests/integration/sandbox/code_execution \
        tests/integration/async_sandbox/code_execution
fi

# Phase 8 – Terminal and desktop features
if should_run_phase 8; then
    run_phase 8 "Terminal and desktop features" \
        tests/integration/terminal \
        tests/integration/desktop
fi

# Merge all phase JUnit XML files into one
echo -e "\n${BLUE}Merging JUnit XML reports...${NC}"
python3 << EOF
import xml.etree.ElementTree as ET
import os
import glob

# Find all phase XML files
phase_range = "${PHASE_RANGE}"
junit_temp_dir = "${JUNIT_TEMP_DIR}"

if phase_range:
    # Only merge files for phases in range
    phase_start = int("${PHASE_START:-0}")
    phase_end = int("${PHASE_END:-8}")
    phase_files = []
    for phase in range(phase_start, phase_end + 1):
        phase_file = f"{junit_temp_dir}/phase_{phase}.xml"
        if os.path.exists(phase_file):
            phase_files.append(phase_file)
    phase_files = sorted(phase_files)
else:
    phase_files = sorted(glob.glob(f"{junit_temp_dir}/phase_*.xml"))

if not phase_files:
    print("No JUnit XML files found to merge")
    exit(1)

# Create root testsuites element
root = ET.Element("testsuites")
total_tests = 0
total_failures = 0
total_errors = 0
total_skipped = 0
total_time = 0.0

# Process each phase file
for phase_file in phase_files:
    try:
        tree = ET.parse(phase_file)
        phase_root = tree.getroot()
        
        # Handle both <testsuites> and <testsuite> roots
        if phase_root.tag == "testsuites":
            for testsuite in phase_root:
                root.append(testsuite)
                total_tests += int(testsuite.get("tests", 0))
                total_failures += int(testsuite.get("failures", 0))
                total_errors += int(testsuite.get("errors", 0))
                total_skipped += int(testsuite.get("skipped", 0))
                total_time += float(testsuite.get("time", 0))
        elif phase_root.tag == "testsuite":
            root.append(phase_root)
            total_tests += int(phase_root.get("tests", 0))
            total_failures += int(phase_root.get("failures", 0))
            total_errors += int(phase_root.get("errors", 0))
            total_skipped += int(phase_root.get("skipped", 0))
            total_time += float(phase_root.get("time", 0))
    except Exception as e:
        print(f"Warning: Could not parse {phase_file}: {e}")

# Set root attributes
root.set("tests", str(total_tests))
root.set("failures", str(total_failures))
root.set("errors", str(total_errors))
root.set("skipped", str(total_skipped))
root.set("time", f"{total_time:.2f}")

# Write merged XML
tree = ET.ElementTree(root)
ET.indent(tree, space="  ")
tree.write("${JUNIT_XML}", encoding="utf-8", xml_declaration=True)
print(f"Merged {len(phase_files)} phase files into ${JUNIT_XML}")
print(f"Total: {total_tests} tests, {total_failures} failures, {total_errors} errors, {total_skipped} skipped")
EOF

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}All integration test phases completed!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "Test artifacts saved:"
echo -e "  - JUnit XML: ${JUNIT_XML}"
echo -e "  - Pytest Output: ${PYTEST_OUTPUT}"
echo -e "  - Phase JUnit files: ${JUNIT_TEMP_DIR}\n"

