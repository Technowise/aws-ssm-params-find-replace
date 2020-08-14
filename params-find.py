#Compare parameters (keys and types) between two environments(lower and higher) prior to deployment/promotion of application.
## USAGE:
# Example: python3 params-find.py -s staging-rds.invalid.us-west-2.rds.amazonaws.com -r staging-rds-new.invalid.us-west-2.rds.amazonaws.com
import boto3
import sys
import argparse
from parameterstore import ParameterStore
from datetime import datetime
from datetime import timezone
from datetime import timedelta

parser = argparse.ArgumentParser(description="Find and replace parameter store values")
parser.add_argument(
    "--profile",
    dest="profile",
    help="AWS Profile to use",
    metavar="NAME"
)
parser.add_argument(
    "--region",
    dest="region",
    help="AWS Region to use",
    metavar="AWS::Region"
)
parser.add_argument(
    "--search-path",
    dest="search_path",
    help="Parameter-path to search",
    default='/'
)
parser.add_argument(
    "--search",
    "-s",
    dest="search",
    help="Value to search",
    required=True
)
parser.add_argument(
    "--replace",
    "-r",
    dest="replace",
    help="Value to replace with searched string",
)
parser.add_argument(
    "--dry-run",
    "-N",
    dest="dry_run",
    action="store_true",
    help="Only show the matching parameters and what would be the replaced value.",
    default=False
)

options = parser.parse_args()

kwargs = {}
if options.profile is not None:
    kwargs["profile_name"] = options.profile
if options.region is not None:
    kwargs["region_name"] = options.region

session = boto3.Session(**kwargs)
param_store = ParameterStore(session=session)
ssm_client = session.client('ssm')
search_path = options.search_path
current_environment_params = param_store.get_parameters_by_path(search_path, recursive=True)
search_string = options.search
replace_string = options.replace
replaced_count = 0
found_count = 0

for current_param in current_environment_params:
    if( current_param['value'].find(search_string) != -1 ):
        print("Path: ", current_param['full_path'])
        print("Value: ", current_param['value'])
        found_count += 1
        if( replace_string != None ):
            print("Replacement Value: ", current_param['value'].replace(search_string, replace_string))
            if( options.dry_run != True ):
                ssm_client.put_parameter( Name=current_param['full_path'], Value=current_param['value'].replace(search_string, replace_string), Overwrite=True, Type=current_param['type'])
                replaced_count += 1
            else:
                print("No replacement done (--dry-run enabled)")
        print("\n")

print("Total matches found: ", found_count)
if( replace_string != None ):
    print("Total replacements done: ", replaced_count)
