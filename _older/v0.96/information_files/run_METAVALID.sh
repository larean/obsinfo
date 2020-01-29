#!/bin/sh

BINDIR="../../metadata-validator"
INFODIR="."

METADATA_VALIDATOR_OPTS="-Djava.util.logging.config.file=./JULogging.properties"

#java -jar ${BINDIR}/metadata-validator-1.0-all.jar -h
echo "===================================================================="
java -jar ${BINDIR}/metadata-validator-1.0-all.jar -v $INFODIR/CAMPAIGN.campaign.yaml -s $INFODIR/schemas/campaign.schema.json
echo "===================================================================="
java -jar ${BINDIR}/metadata-validator-1.0-all.jar -v $INFODIR/CAMPAIGN.FACILITY.network.yaml -s $INFODIR/schemas/network.schema.json
echo "===================================================================="
java -jar ${BINDIR}/metadata-validator-1.0-all.jar -v $INFODIR/FACILITY.instrumentation.yaml -s $INFODIR/schemas/instrumentation.schema.json
echo "===================================================================="
java -jar ${BINDIR}/metadata-validator-1.0-all.jar -v  $INFODIR/FACILITY.instrument_components.yaml -s $INFODIR/schemas/instrument_components.schema.json

