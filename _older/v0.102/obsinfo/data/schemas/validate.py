#! env python3
instrumentation_dir="../instrumentation/INSU-IPGP.2018-06-01"
campaign_dir="../campaigns/MYCAMPAIGN"

from obsinfo.misc.validate import validate
 
print("")
print("=====================================================================")
print("TESTING MAIN FILES")
print("=====================================================================")
validate(f"{campaign_dir}/MYCAMPAIGN.INSU-IPGP.network.yaml")
validate(f"{campaign_dir}/MYCAMPAIGN.campaign.yaml")
validate(f"{instrumentation_dir}/instrumentation.yaml")
validate(f"{instrumentation_dir}/instrument-components.yaml")
# 
# echo ""
# echo "====================================================================="
# echo "TESTING RESPONSE FILES"
# echo "====================================================================="
# for f in $instrumentation_dir/responses/Dataloggers/*.yaml ; do
#     test_yaml "$f" "response.schema.json" "-v"
# done
# for f in  $instrumentation_dir/responses/Sensors/*.yaml ; do
#     test_yaml "$f" "response.schema.json" "-v"
# done
# for f in  $instrumentation_dir/responses/Preamplifiers/*.yaml ; do
#     test_yaml "$f" "response.schema.json" "-v"
# done
# echo ""
# echo "====================================================================="
# echo "TESTING FILTER FILES"
# echo "====================================================================="
# if test -d $instrumentation_dir/responses/_filters ; then
#     for f in $instrumentation_dir/responses/_filters/*/*.yaml ; do
#         test_yaml "$f" "filter_file.schema.json" "-v"
#     done
# fi
# 
#             
#     
