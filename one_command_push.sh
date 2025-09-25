#!/bin/bash

# Ultra-simple one command to push botv3 branch only
git checkout botv3 && git add . && git commit -m "botv3 final commit - $(date)" && echo "# botv3" > README.md && git add README.md && git commit -m "Add README" && git remote remove origin 2>/dev/null || true && git remote add origin https://github.com/deepakchaudharigit/botv3.git && git push -u origin botv3:main