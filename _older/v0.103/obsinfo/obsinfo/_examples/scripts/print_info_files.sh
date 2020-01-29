#!/bin/bash
INSTRUMENTATION_DIR="../Information_Files/instrumentation/INSU-IPGP.2018-06-01"
CAMPAIGN_DIR="../Information_Files/campaigns/MYCAMPAIGN"

echo "=============================================================="
echo "== FILES IN CAMPAIGN DIRECTORY: $CAMPAIGN_DIR"
echo "=============================================================="
for f in ${CAMPAIGN_DIR}/*.yaml; do
    echo "___________________________________________________________"
    obsinfo-print "$f"
    echo "-----------------------------------------------------------"
    echo "|"; echo "|"; echo "|"
done
echo ""
echo "=============================================================="
echo "== FILES IN INSTRUMENTATION DIRECTORY: $INSTRUMENTATION_DIR"
echo "=============================================================="
for f in ${INSTRUMENTATION_DIR}/*.yaml; do
    echo "___________________________________________________________"
    obsinfo-print "$f"
done