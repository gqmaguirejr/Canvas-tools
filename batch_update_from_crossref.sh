#!/bin/bash

# Define the name of the final spreadsheet
OUTPUT_SPREADSHEET="/tmp/combined_bibliography.xlsx"

# Check if the python script exists
PYTHON_SCRIPT="/z3/maguire/Canvas/Canvas-tools/Crossref_HTML-to-spreadsheet.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: $PYTHON_SCRIPT not found."
    exit 1
fi

echo "Starting batch processing of HTML files..."

# Loop through all .html files in the current directory
for html_file in *.html; do
    # Skip if no html files are found
    [[ -e "$html_file" ]] || continue
    
    echo "Processing: $html_file"
    
    # Call the python script with the HTML file and the shared output file
    python3 "$PYTHON_SCRIPT" "$html_file" "$OUTPUT_SPREADSHEET"
done

echo "Batch processing complete. Results saved to $OUTPUT_SPREADSHEET."
