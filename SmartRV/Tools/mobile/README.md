# README

# Instructions

1. Add these environment variables to your `.bashrc` and change the paths to point to your repositories.
```
export PI_SMART_RV_REPO_PATH=/home/guf/WinnConnect/SmartRV
export PI_FRONTEND_REPO_PATH=/home/guf/WinnConnect/Frontend
```

2. To run, run `build.sh` with the following options:
* -h Help
* -p Pulls each of the repositories current branches.
* -a Builds both services and frontend. If omitted, just builds services.