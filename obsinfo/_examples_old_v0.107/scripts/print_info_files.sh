#!/bin/bash
INSTRUMENTATION_DIR="../Information_Files/instrumentation/INSU-IPGP.2018-06-01"
CAMPAIGN_DIR="../Information_Files/campaigns/MYCAMPAIGN"

echo "====== FILES IN CAMPAIGN DIRECTORY: $CAMPAIGN_DIR ======"
for f in ${CAMPAIGN_DIR}/*.yaml; do
    obsinfo-print "$f"
done

echo "== FILES IN INSTRUMENTATION DIRECTORY: $INSTRUMENTATION_DIR =="
for f in ${INSTRUMENTATION_DIR}/*.yaml; do
    obsinfo-print "$f"
done
