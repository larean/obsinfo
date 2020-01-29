#!/bin/bash
metadata_validator="./metadata-validator/metadata-validator-1.0-all.jar"
response_dir="../INSU-IPGP_RESPONSES"

test_yaml()
{
    YAML_FILE=$1
    SCHEMA_FILE=$2
    ARGS=$3
    echo ""
    echo "====================================================================="
    echo "Validating $YAML_FILE against $SCHEMA_FILE"
    java -jar $metadata_validator $YAML_FILE -s $SCHEMA_FILE $ARGS
}

test_yaml "../CAMPAIGN.FACILITY.network.yaml" "network.json" "-v"
test_yaml "../CAMPAIGN.campaign.yaml" "campaign.json" "-v"
test_yaml "../FACILITY.instrumentation.yaml" "instrumentation.json" "-v"
test_yaml "../FACILITY.instrument-components.yaml" "instrument-components.json" "-v"
# TEST RESPONSE-STAGES.YAML AND RESPONSE.YAML FILES
    for f in $response_dir/Dataloggers/*.yaml ; do
        test_yaml "$f" "response.json"
    done
    for f in $response_dir/Sensors/*.yaml ; do
        test_yaml "$f" "response.json"
    done
    for f in $response_dir/Preamplifiers/*.yaml ; do
        test_yaml "$f" "response.json"
    done
    if test -d $response_dir/_filters ; then
        for f in $response_dir/_filters/*/*.yaml ; do
            test_yaml "$f" "filter.json"
        done
    fi
    
            
    
