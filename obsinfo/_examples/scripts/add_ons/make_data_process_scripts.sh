#!/bin/bash
# Make data process scripts
# This is a first try, to imagine the console_script needed to do so:

network_file='../Information_Files/campaigns/MYCAMPAIGN/MYCAMPAIGN.INSU-IPGP.network.yaml'
destination_folder='./process_scripts'

station_data_path='/Volumes/PARC_OBS_Wayne/DATA_EXPERIMENTS/2017-18.AlpArray/2017-18.AlpArray'
sdpchain_path='/Users/crawford/_Work/Parc_OBS/3_Development/Data_and_Metadata/SDPCHAIN/Software_IPGP-INSU_v20170222_modWayne'

lc2ms_path="$sdpchain_path/LOCAL/LCHEAPO/lc2ms"
msmod_dir='/Users/crawford/bin'


##############################################################################
##############################################################################
# MAKE FOLDER FOR SCRIPTS
#echo "$destination_folder"
mkdir -p "$destination_folder"

obsinfo-make_process_scripts_LC2MS    "$network_file" "$station_data_path" "$lc2ms_path"    --input_dir "1_proprietary" --output_dir "2_miniseed_basic"
mv process_*.sh $destination_folder
obsinfo-make_process_scripts_SDPCHAIN "$network_file" "$station_data_path" "$sdpchain_path" --input_dir "2_miniseed_basic" --msdrift_dir "MSDRIFT" --ms2sds_dir "MS2SDS" --msmod_path $msmod_dir
mv process_*.sh $destination_folder