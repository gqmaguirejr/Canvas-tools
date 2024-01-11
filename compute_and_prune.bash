#!/bin/bash
# recursively compute the unique words and prune them
#
# example when in the directory Course_41668/course file
#   ../../compute_and_prune.bash .
# 
#
shopt -s nullglob
#IFS=$'\n'
echo "$1"
dir="$1"

function fakeprocessFile() {
    local f="$1"
    if [[ "$f" == *.pdf ]] && [ -f "$f" ]; then
      echo "$f"
    fi
}


function processFile() {
    local f="$1"
    if [[ "$f" == *.pdf ]] && [ -f "$f" ]; then
      echo "$f"

      # do something on $f
      /z3/maguire/Canvas/Canvas-tools/compute_unique_words_for_pages_in_course.py --config /z3/maguire/Canvas/Canvas-tools/config.json 41668 --ligature --dir "." -P "$f"
      /z3/maguire/Canvas/Canvas-tools/prune_unique_words.py 41668 --dir "." -P "$f"
    fi
}


function processDir() {
    local dir="$1"
    echo "processDir $file"

    for file in "$dir"/*; do
	if [ -f "$file" ]; then
	    #echo "$file"
	    processFile "$file"
	    #fakeprocessFile "$file"
	fi

	if [ -d "$file" ]; then
	    processDir "$file"
	fi
    done
}

processDir "$dir"

# unset it now 
shopt -u nullglob
