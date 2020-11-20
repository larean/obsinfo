#!/bin/bash
# TESTS ALL INFORMATION FILES IN AN INSU-IPGP STRUCTURE
#  Assumes campaign and network files are in CAMPAIGN_DIR
#  Assumes instrumnetation and responses are in INSTRUMENTATION_DIR with
#    the following structure:
#       {INSTRUMENTATION_DIR}/*.yaml
#       {INSTRUMENTATION_DIR}/responses/{Dataloggers,PreAmplifiers,Sensors}/*.response.yaml
#       {INSTRUMENTATION_DIR}/responses/_filters/*/*.filter.yaml

INSTRUMENTATION_DIR="../Information_Files/instrumentation/INSU-IPGP.2018-06-01"
CAMPAIGN_DIR="../Information_Files/campaigns/MYCAMPAIGN"

echo ""
echo "====================================================================="
echo "TESTING MAIN FILES"
echo "====================================================================="
for f in ${CAMPAIGN_DIR}/*.yaml; do
    obsinfo-validate "$f"
done
for f in ${INSTRUMENTATION_DIR}/*.yaml; do
    obsinfo-validate "$f"
done

echo ""
echo "====================================================================="
echo "TESTING RESPONSE FILES"
echo "====================================================================="
for f in $INSTRUMENTATION_DIR/responses/[!_]*/*.response.yaml ; do
    if test -f $f ; then
        obsinfo-validate "$f"
    fi
done

echo ""
echo "====================================================================="
echo "TESTING FILTER FILES"
echo "====================================================================="
if test -d $INSTRUMENTATION_DIR/responses/_filters ; then
    for f in $INSTRUMENTATION_DIR/responses/_filters/*/*.filter.yaml ; do
        if test -f $f ; then
            obsinfo-validate "$f"
        fi
    done
fi

            
    
