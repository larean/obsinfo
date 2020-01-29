yaml_file="CAMPAIGN.FACILITY.network.yaml"
schema_file="network.schema.json"
echo ""
echo "=========================================================================="
echo "Validating $yaml_file against $schema_file"
java -jar ../metadata-validator/metadata-validator-1.0-all.jar $yaml_file -s $schema_file

yaml_file="CAMPAIGN.campaign.yaml"
schema_file="campaign.schema.json"
echo ""
echo "=========================================================================="
echo "Validating $yaml_file against $schema_file"
java -jar ../metadata-validator/metadata-validator-1.0-all.jar $yaml_file -s $schema_file

yaml_file="FACILITY.instrumentation.yaml"
schema_file="instrumentation.schema.json"
echo ""
echo "=========================================================================="
echo "Validating $yaml_file against $schema_file"
java -jar ../metadata-validator/metadata-validator-1.0-all.jar $yaml_file -s $schema_file

# yaml_file="FACILITY.components.yaml"
# schema_file="components.schema.json"
# echo ""
# echo "=========================================================================="
# echo "Validating $yaml_file against $schema_file"
# java -jar ../metadata-validator/metadata-validator-1.0-all.jar $yaml_file -s $schema_file
