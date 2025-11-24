#!/bin/bash
# Run integration test phases one by one and generate reports for each

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_BASE_DIR="$(cd "$SCRIPT_DIR/../../../local/reports" && pwd)"
mkdir -p "$REPORTS_BASE_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running Integration Tests Phase by Phase${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Phase definitions
declare -a PHASES=(
    "0:Templates and static setup"
    "1:Authentication"
    "2:Sandbox creation"
    "3:Connection"
    "4:Basic info and listing"
    "5:Lifecycle"
    "6:Resources"
    "7:Code execution"
    "8:Terminal and desktop features"
)

for phase_info in "${PHASES[@]}"; do
    IFS=':' read -r phase_num phase_name <<< "$phase_info"
    
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}Phase ${phase_num}: ${phase_name}${NC}"
    echo -e "${CYAN}========================================${NC}\n"
    
    # Run the phase
    if ./run_integration_suites.sh --range "$phase_num" --debug; then
        echo -e "${GREEN}Phase ${phase_num} completed successfully${NC}"
        
        # Find the most recent JUnit XML file for this phase
        LATEST_JUNIT=$(ls -t "$REPORTS_BASE_DIR"/junit_integration_*.xml 2>/dev/null | head -1)
        LATEST_OUTPUT=$(ls -t "$REPORTS_BASE_DIR"/pytest_output_*.txt 2>/dev/null | head -1)
        
        if [ -n "$LATEST_JUNIT" ] && [ -f "$LATEST_JUNIT" ]; then
            echo -e "${BLUE}Generating report for Phase ${phase_num}...${NC}"
            
            # Generate report using the Python script
            REPORT_PATH="$REPORTS_BASE_DIR/phase_${phase_num}_test_report.md"
            python3 "$SCRIPT_DIR/generate_phase_report.py" \
                "$LATEST_JUNIT" \
                "$REPORT_PATH" \
                "$phase_num" \
                "$phase_name" \
                "$LATEST_OUTPUT"
            
            if [ -f "$REPORT_PATH" ]; then
                echo -e "${GREEN}Report generated for Phase ${phase_num}: ${REPORT_PATH}${NC}"
            else
                echo -e "${YELLOW}Warning: Report generation may have failed${NC}"
            fi
        else
            echo -e "${YELLOW}Warning: Could not find JUnit XML file for Phase ${phase_num}${NC}"
        fi
    else
        echo -e "${RED}Phase ${phase_num} failed!${NC}"
        echo -e "${YELLOW}Skipping remaining phases...${NC}"
        exit 1
    fi
    
    echo ""
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All phases completed!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "Reports saved in: ${REPORTS_BASE_DIR}"

