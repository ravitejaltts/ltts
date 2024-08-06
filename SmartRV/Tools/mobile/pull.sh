#!/bin/bash

# Pull a git repository

# Fail if any command fails
set -e

branch=""
repo=""

while getopts b:r: opt
do
    case "$opt" in
        b)
            branch="$OPTARG"
            ;;
        r)
            repo="$OPTARG"
            ;;
        ?)
            exit 1
            ;;
    esac
done

if [[ -n $repo ]]
then
    echo "repo=$repo"
    cd $repo
fi

# Reset local changes
git reset --hard

# If argument is set, checkout new branch
if [ -z $branch ]
then
    printf "\n\nPulling current branch\n"
else
    printf "\n\nCheckout and pull $branch\n"
    git checkout $branch
fi

git pull