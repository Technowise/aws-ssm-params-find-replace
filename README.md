# aws-ssm-parameters-find-replace
Find and replace AWS SSM parameters by value.
AWS Console and CLI do not currently provide easy way to filter out parameters by value, so this project is intended to help fill that gap. Using this, you can search parameters which contain the given search string as part of its value, and optionally replace the value with the given replacement string. The script takes care of decrypting the value as well to compare with the given search string.

## Usage/Syntax:
```
params-find.py [-h] [--profile NAME] [--region AWS::Region]
                      [--search-path SEARCH_PATH] --search SEARCH
                      [--replace REPLACE] [--dry-run]
```

**Optional arguments:**
```
  -h, --help            show this help message and exit
  --profile NAME        AWS Profile to use
  --region AWS::Region  AWS Region to use
  --search-path SEARCH_PATH
                        Parameter-path to search
  --search SEARCH, -s SEARCH
                        Value to search
  --replace REPLACE, -r REPLACE
                        Value to replace with searched string
  --dry-run, -N         Only show the matching parameters and what would be
                        the replaced value without actually replacing.
```

### Credits:
This project borrows code from https://github.com/PaddleHQ/python-aws-ssm for fetching parameter values. The code from this repo is slightly modified to the use case we have for find and replace, and hence we have a copy of parameterstore.py in this repo as well.
