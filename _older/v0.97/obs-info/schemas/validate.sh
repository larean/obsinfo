#!/bin/bash
metadata_validator="./metadata-validator/metadata-validator-1.0-all.jar"
response_dir="../RESPONSE_YAML_INSU-IPGP"

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

test_yaml "../CAMPAIGN.FACILITY.network.yaml" "network.schema.json" "-v"
test_yaml "../CAMPAIGN.campaign.yaml" "campaign.schema.json" "-v"
test_yaml "../FACILITY.instrumentation.yaml" "instrumentation.schema.json" "-v"
test_yaml "../FACILITY.instrument-components.yaml" "instrument-components.schema.json" "-v"
# TEST RESPONSE-STAGES.YAML AND RESPONSE.YAML FILES
for d in $response_dir/* ; do 
    echo $d
    for f in $d/*.yaml ; do
        test_yaml "$f" "response-stages.schema.json"
    done
    if test -d $d/include ; then
        for f in $d/include/*.yaml ; do
            test_yaml "$f" "response.schema.json"
        done
    fi
done
    
            
    
