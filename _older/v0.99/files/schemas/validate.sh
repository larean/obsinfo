#!/bin/bash
metadata_validator="../../../../metadata-validator/metadata-validator-1.0-all.jar"
instrumentation_dir="../instrumentation/MYFACILITY.yyyy-mm-dd"
campaign_dir="../campaigns/MYCAMPAIGN"

test_yaml()
{
    YAML_FILE=$1
    SCHEMA_FILE=$2
    ARGS=$3
    INFOFILE="5678temp"
    # echo ""
    # echo "====================================================================="
    echo "Validating $YAML_FILE against $SCHEMA_FILE"
    java -jar $metadata_validator $YAML_FILE -s $SCHEMA_FILE $ARGS > $INFOFILE
    if [ $? -eq 0 ]
    then
        echo "Sucessfully validated"
    else
        echo "Failed validation"
        cat $INFOFILE
    fi   
    rm $INFOFILE     
}

test_yaml "$campaign_dir/MYCAMPAIGN.FACILITY.network.yaml" "network.schema.json" "-v"
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

            
    
