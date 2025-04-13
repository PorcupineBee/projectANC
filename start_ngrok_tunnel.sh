#!/bin/bash

# Define the file path
FILE_PATH="src/serverport.txt"

# Check if the file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File '$FILE_PATH' does not exist."
    exit 1
fi

# Read the PORTID from the file and assign it to a variable
PORTID=$(cat "$FILE_PATH")

# Validate that the content is actually an integer
if ! [[ "$PORTID" =~ ^-?[0-9]+$ ]]; then
    echo "Error: File does not contain a valid integer."
    exit 1
fi

# Display the PORTID
echo "Server local PORTID: $PORTID"

ngrok tcp $PORTID