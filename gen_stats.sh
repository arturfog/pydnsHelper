#!/bin/bash
LINES=`find modules -type f -name '*.py' -exec cat {} \; | wc -l`
echo "Lines of code: $LINES"
