#!/bin/bash

CIF_PATH="$1"
TAG="$2"

echo "🔧 Simulating job for tag: $TAG"
echo "📄 CIF file path: $CIF_PATH"

# Simulate some processing time
sleep 30

# Create a result message (you can replace this with actual results)
RESULT="✅ Finished processing $CIF_PATH for tag $TAG"

# Post the result to the response channel
echo -e "🔖 Tag: $TAG\n\n$RESULT" | curl -s -H "Content-Type: text/plain" -d @- https://ntfy.sh/polarized-xes-response

echo "$RESULT"

