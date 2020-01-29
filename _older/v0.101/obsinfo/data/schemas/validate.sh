#!/bin/bash
#validator_command="java -jar ../../../../../metadata-validator/metadata-validator-1.0-all.jar"
validator_command="../../../../../metadata-validator/metadata-validator-1.0/bin/metadata-validator"
validator_command="../../../../../metadata-validator/everit-validator/bin/everit-validator"
instrumentation_dir="../instrumentation/INSU-IPGP.2018-06-01"
campaign_dir="../campaigns/MYCAMPAIGN"
stop_on_error=1

test_yaml()
{
    YAML_FILE=$1
    SCHEMA_FILE=$2
    ARGS=$3
    INFOFILE="45678temp"
    # echo ""
    # echo "====================================================================="
    echo -n "Validating $YAML_FILE against $SCHEMA_FILE: "
    # $validator_command $YAML_FILE -s $SCHEMA_FILE $ARGS > $INFOFILE
    $validator_command $SCHEMA_FILE $YAML_FILE > $INFOFILE
    if [ $? -eq 0 ]
    then
        echo "SUCCESS"
    else
        echo "FAILED"
        cat $INFOFILE
        if [ $stop_on_error -eq 1 ]; then
            exit 1
        fi
    fi   
    rm $INFOFILE     
}

echo ""
echo "====================================================================="
echo "TESTING MAIN FILES"
echo "====================================================================="
test_yaml "$campaign_dir/MYCAMPAIGN.INSU-IPGP.network.yaml" "network.schema.json" "-v"
test_yaml "$campaign_dir/MYCAMPAIGN.campaign.yaml" "campaign.schema.json" "-v"
test_yaml "$instrumentation_dir/instrumentation.yaml" "instrumentation.schema.json" "-v"
test_yaml "$instrumentation_dir/instrument-components.yaml" "instrument-components.schema.json" "-v"

echo ""
echo "====================================================================="
echo "TESTING RESPONSE FILES"
echo "====================================================================="
for f in $instrumentation_dir/responses/Dataloggers/*.yaml ; do
    test_yaml "$f" "response.schema.json" "-v"
done
for f in  $instrumentation_dir/responses/Sensors/*.yaml ; do
    test_yaml "$f" "response.schema.json" "-v"
done
for f in  $instrumentation_dir/responses/Preamplifiers/*.yaml ; do
    test_yaml "$f" "response.schema.json" "-v"
done
echo ""
echo "====================================================================="
echo "TESTING FILTER FILES"
echo "====================================================================="
if test -d $instrumentation_dir/responses/_filters ; then
    for f in $instrumentation_dir/responses/_filters/*/*.yaml ; do
        test_yaml "$f" "filter_file.schema.json" "-v"
    done
fi

            
    
