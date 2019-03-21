#!/bin/bash
# Make data process scripts
# This is a first try, to imagine the console_script needed to do so:

network_file='../../Information_Files/campaigns/MYCAMPAIGN/MYCAMPAIGN.INSU-IPGP.network.yaml'
destination_folder='./process_scripts'

station_data_dir='/Volumes/PARC_OBS_Wayne/DATA_EXPERIMENTS/2017-18.AlpArray/2017-18.AlpArray'
sdpchain_dir='/opt/sdpchain'
lcheapo_dir='/opt/lcheapo'

##############################################################################
##############################################################################
# MAKE FOLDER FOR SCRIPTS
mkdir -p "$destination_folder"

obsinfo-make_process_scripts_LC2MS    "$network_file" "$station_data_dir" "$lcheapo_dir"  --input_dir "." --output_dir "miniseed_basic"     --suffix ""
obsinfo-make_process_scripts_SDPCHAIN "$network_file" "$station_data_dir" "$sdpchain_dir" --input_dir "miniseed_basic" --no_header --append --suffix ""
mv process_*.sh $destination_folder
