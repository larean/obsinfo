#!/bin/bash
# TESTS ALL INFORMATION FILES IN AN INSU-IPGP STRUCTURE
#  Assumes campaign and network files are in campaign_dir
#  Assumes instrumnetation and responses are in INSTRUMENTATION_DIR with
#    the following structure:
#       {INSTRUMENTATION_DIR}/*.instrumentation.{yaml,json}
#       {INSTRUMENTATION_DIR}/*.instrumentat_components.{yaml,json}
#       {INSTRUMENTATION_DIR}/responses/{Dataloggers,PreAmplifiers,Sensors}/*.response.{yaml,json}
#       {INSTRUMENTATION_DIR}/responses/_filters/*/*.filter.{yaml,json}

INSTRUMENTATION_DIR="../Information_Files/instrumentation/INSU-IPGP.2018-06-01"
CAMPAIGN_DIR="../Information_Files/campaigns/MYCAMPAIGN"

echo ""
echo "====================================================================="
echo "VALIDATING MAIN FILES"
echo "====================================================================="
for f in ${CAMPAIGN_DIR}/*.yaml; do
    obsinfo-validate "$f"
done
for f in ${INSTRUMENTATION_DIR}/*.yaml; do
    obsinfo-validate "$f"
done

echo ""
echo "====================================================================="
echo "VALIDATING RESPONSE FILES"
echo "====================================================================="
for f in $INSTRUMENTATION_DIR/responses/[!_]*/*.yaml ; do
    if test -f $f ; then
        obsinfo-validate "$f"
    fi
done

echo ""
echo "====================================================================="
echo "VALIDATING FILTER FILES"
echo "====================================================================="
if test -d $INSTRUMENTATION_DIR/responses/_filters ; then
    for f in $INSTRUMENTATION_DIR/responses/_filters/*/*.yaml ; do
        if test -f $f ; then
            obsinfo-validate "$f"
        fi
    done
fi

            
    
