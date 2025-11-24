#!/usr/bin/env python3
"""
Generate detailed test report for a phase following tester-agent.mdc guidelines.
"""

import xml.etree.ElementTree as ET
import os
import sys
from datetime import datetime
from collections import defaultdict

def parse_junit_xml(junit_file):
    """Parse JUnit XML and extract test data."""
    tree = ET.parse(junit_file)
    root = tree.getroot()
    
    # Extract summary
    total_tests = int(root.get("tests", 0))
    total_failures = int(root.get("failures", 0))
    total_errors = int(root.get("errors", 0))
    total_skipped = int(root.get("skipped", 0))
    total_time = float(root.get("time", 0))
    
    # Categorize tests
    tests_by_category = defaultdict(lambda: {"passed": [], "failed": [], "skipped": [], "errors": []})
    
    for testsuite in root.findall("testsuite"):
        for testcase in testsuite.findall("testcase"):
            classname = testcase.get("classname", "")
            testname = testcase.get("name", "")
            duration = float(testcase.get("time", 0))
            full_path = f"{classname}::{testname}"
            
            # Determine category from classname
            if "template" in classname.lower():
                category = "Template"
            elif "sandbox" in classname.lower() and "async" in classname.lower():
                category = "AsyncSandbox"
            elif "sandbox" in classname.lower():
                category = "Sandbox"
            elif "desktop" in classname.lower():
                category = "Desktop"
            elif "terminal" in classname.lower():
                category = "Terminal"
            else:
                category = "Other"
            
            # Determine status
            failure = testcase.find("failure")
            error = testcase.find("error")
            skipped = testcase.find("skipped")
            
            test_info = {
                "name": testname,
                "classname": classname,
                "full_path": full_path,
                "duration": duration,
                "file": classname.replace(".", "/") + ".py" if classname else "unknown"
            }
            
            if failure is not None:
                test_info["error_type"] = failure.get("type", "Failure")
                test_info["error_message"] = failure.text or ""
                tests_by_category[category]["failed"].append(test_info)
            elif error is not None:
                test_info["error_type"] = error.get("type", "Error")
                test_info["error_message"] = error.text or ""
                tests_by_category[category]["errors"].append(test_info)
            elif skipped is not None:
                test_info["skip_reason"] = skipped.get("message", "Skipped")
                tests_by_category[category]["skipped"].append(test_info)
            else:
                tests_by_category[category]["passed"].append(test_info)
    
    return {
        "total_tests": total_tests,
        "total_failures": total_failures,
        "total_errors": total_errors,
        "total_skipped": total_skipped,
        "total_time": total_time,
        "tests_by_category": dict(tests_by_category)
    }

def generate_report(junit_file, output_file, pytest_output, phase_num, phase_name):
    """Generate detailed test report."""
    data = parse_junit_xml(junit_file)
    
    # Calculate percentages
    total = data["total_tests"]
    passed = sum(len(cat["passed"]) for cat in data["tests_by_category"].values())
    failed = data["total_failures"]
    errors = data["total_errors"]
    skipped = data["total_skipped"]
    
    success_rate = (passed / total * 100) if total > 0 else 0
    
    with open(output_file, "w") as f:
        # Header
        f.write(f"# Phase {phase_num} Integration Test Report - {phase_name}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Phase:** {phase_num} - {phase_name}\n")
        f.write(f"**Test Run ID:** {os.path.basename(junit_file).replace('junit_integration_', '').replace('.xml', '')}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        status_emoji = "✅" if failed == 0 and errors == 0 else "❌"
        status_text = "PASSED" if failed == 0 and errors == 0 else "FAILED"
        f.write(f"- **Overall status:** {status_emoji} **{status_text}**\n")
        f.write(f"- **Total tests:** {total}\n")
        f.write(f"- **Passed:** {passed} ✅\n")
        f.write(f"- **Failed:** {failed} ❌\n")
        f.write(f"- **Errors:** {errors} ⚠️\n")
        f.write(f"- **Skipped:** {skipped} ⏭️\n")
        f.write(f"- **Duration:** {data['total_time']:.2f}s\n")
        f.write(f"- **Success rate:** {success_rate:.1f}%\n\n")
        f.write("---\n\n")
        
        # Test Execution Details
        f.write("## Test Execution Details\n\n")
        f.write(f"- **Command used:** `./run_integration_suites.sh --range {phase_num} --debug`\n")
        f.write(f"- **JUnit XML:** `{junit_file}`\n")
        if pytest_output:
            f.write(f"- **Pytest Output:** `{pytest_output}`\n")
        f.write("\n")
        
        # Individual Test Results by Category
        f.write("## Individual Test Results\n\n")
        
        for category in sorted(data["tests_by_category"].keys()):
            cat_data = data["tests_by_category"][category]
            cat_total = len(cat_data["passed"]) + len(cat_data["failed"]) + len(cat_data["errors"]) + len(cat_data["skipped"])
            
            if cat_total == 0:
                continue
            
            f.write(f"### {category} Tests\n\n")
            f.write("| Status | Test Name | File | Duration | Notes |\n")
            f.write("|--------|-----------|------|----------|-------|\n")
            
            # Passed tests
            for test in cat_data["passed"][:20]:  # Limit to first 20
                f.write(f"| ✅ | `{test['name']}` | `{test['file']}` | {test['duration']:.3f}s | |\n")
            if len(cat_data["passed"]) > 20:
                f.write(f"| | ... and {len(cat_data['passed']) - 20} more passed tests | | | |\n")
            
            # Failed tests
            for test in cat_data["failed"]:
                error_msg = test.get("error_message", "")[:100].replace("\n", " ")
                f.write(f"| ❌ | `{test['name']}` | `{test['file']}` | {test['duration']:.3f}s | **Error:** {error_msg} |\n")
            
            # Error tests
            for test in cat_data["errors"]:
                error_msg = test.get("error_message", "")[:100].replace("\n", " ")
                f.write(f"| ⚠️ | `{test['name']}` | `{test['file']}` | {test['duration']:.3f}s | **Error:** {error_msg} |\n")
            
            # Skipped tests (show first 10)
            for test in cat_data["skipped"][:10]:
                reason = test.get("skip_reason", "Skipped")[:50]
                f.write(f"| ⏭️ | `{test['name']}` | `{test['file']}` | {test['duration']:.3f}s | **Reason:** {reason} |\n")
            if len(cat_data["skipped"]) > 10:
                f.write(f"| | ... and {len(cat_data['skipped']) - 10} more skipped tests | | | |\n")
            
            f.write("\n")
            
            # Detailed failures
            if cat_data["failed"] or cat_data["errors"]:
                f.write("**Detailed failures:**\n\n")
                for idx, test in enumerate(cat_data["failed"] + cat_data["errors"], 1):
                    f.write(f"{idx}. **Test:** `{test['full_path']}`\n")
                    f.write(f"   - **File:** `{test['file']}`\n")
                    f.write(f"   - **Status:** {'❌ FAILED' if test in cat_data['failed'] else '⚠️ ERROR'}\n")
                    f.write(f"   - **Duration:** {test['duration']:.3f}s\n")
                    f.write(f"   - **Error Type:** {test.get('error_type', 'Unknown')}\n")
                    if test.get("error_message"):
                        f.write(f"   - **Error Message:**\n")
                        f.write(f"     ```\n")
                        f.write(f"     {test['error_message'][:500]}\n")
                        f.write(f"     ```\n")
                    f.write("\n")
                f.write("\n")
        
        # Test Status Summary by Category
        f.write("## Test Status Summary by Category\n\n")
        f.write("| Category | Total | Passed | Failed | Errors | Skipped | Pass Rate |\n")
        f.write("|----------|-------|--------|--------|--------|---------|-----------|\n")
        
        for category in sorted(data["tests_by_category"].keys()):
            cat_data = data["tests_by_category"][category]
            cat_total = len(cat_data["passed"]) + len(cat_data["failed"]) + len(cat_data["errors"]) + len(cat_data["skipped"])
            cat_passed = len(cat_data["passed"])
            cat_failed = len(cat_data["failed"])
            cat_errors = len(cat_data["errors"])
            cat_skipped = len(cat_data["skipped"])
            cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            
            f.write(f"| {category} | {cat_total} | {cat_passed} | {cat_failed} | {cat_errors} | {cat_skipped} | {cat_rate:.1f}% |\n")
        
        f.write("\n")
        
        # Skipped Tests Analysis
        if skipped > 0:
            f.write("## Skipped Tests Analysis\n\n")
            f.write(f"Total skipped: {skipped}\n\n")
            skip_reasons = defaultdict(list)
            for category, cat_data in data["tests_by_category"].items():
                for test in cat_data["skipped"]:
                    reason = test.get("skip_reason", "Unknown")
                    skip_reasons[reason].append(test["full_path"])
            
            for reason, tests in skip_reasons.items():
                f.write(f"### {reason}\n\n")
                for test_path in tests[:5]:
                    f.write(f"- `{test_path}`\n")
                if len(tests) > 5:
                    f.write(f"- ... and {len(tests) - 5} more\n")
                f.write("\n")
        
        # Slowest Tests
        all_tests = []
        for cat_data in data["tests_by_category"].values():
            all_tests.extend(cat_data["passed"] + cat_data["failed"] + cat_data["errors"])
        
        if all_tests:
            f.write("## Slowest Tests\n\n")
            f.write("| Test Name | File | Duration | Status |\n")
            f.write("|-----------|------|----------|--------|\n")
            
            sorted_tests = sorted(all_tests, key=lambda x: x["duration"], reverse=True)[:10]
            for test in sorted_tests:
                status = "✅" if test in [t for cat in data["tests_by_category"].values() for t in cat["passed"]] else "❌"
                f.write(f"| `{test['name']}` | `{test['file']}` | {test['duration']:.3f}s | {status} |\n")
            f.write("\n")
        
        # Artifacts
        f.write("## Artifacts & References\n\n")
        f.write(f"- **JUnit XML:** `{junit_file}`\n")
        if pytest_output:
            f.write(f"- **Pytest Output:** `{pytest_output}`\n")
        f.write(f"- **Report:** `{output_file}`\n")
        f.write(f"- **Reports Directory:** `{os.path.dirname(output_file)}`\n\n")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: generate_phase_report.py <junit_xml> <output_md> <phase_num> <phase_name> [pytest_output]")
        sys.exit(1)
    
    junit_file = sys.argv[1]
    output_file = sys.argv[2]
    phase_num = sys.argv[3]
    phase_name = sys.argv[4]
    pytest_output = sys.argv[5] if len(sys.argv) > 5 else None
    
    generate_report(junit_file, output_file, pytest_output, phase_num, phase_name)
    print(f"Report generated: {output_file}")

