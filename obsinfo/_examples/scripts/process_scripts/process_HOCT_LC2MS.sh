#!/bin/bash

#============================================================
echo "Running LC2MS processes on station HOCT"
#============================================================

# ============================================================
# LCHEAPO STEPS
# ============================================================
echo "============================================================"
echo "Running LC2MS"
echo "------------------------------------------------------------"
#  - Set up paths to data and executables
LC2MS_DIR=/Users/crawford/_Work/Parc_OBS/3_Development/Data_and_Metadata/SDPCHAIN/Software_IPGP-INSU_v20170222_modWayne/LOCAL/LCHEAPO/lc2ms
STATION_DIR=/Volumes/PARC_OBS_Wayne/DATA_EXPERIMENTS/2017-18.AlpArray/2017-18.AlpArray/HOCT

# - Configure properties file
command cd $LC2MS_DIR/config/
rm lc2ms.properties
echo "# Text encoding : ISO 8859-1 (Latin 1)" >> lc2ms.properties
echo "binaryDirpath=$LC2MS_DIR/bin" >> lc2ms.properties
echo "workingDirpath=$LC2MS_DIR/working" >> lc2ms.properties
echo "applicationComment=This is a comment" >> lc2ms.properties
echo "obsConfigFilepath=$LC2MS_DIR/config/obs-config.csv" >> lc2ms.properties
command cd -

# - Set up environment variables
InJava_Par=$LC2MS_DIR/config/
Config_lc2ms_Path=$LC2MS_DIR/config/
Execut_dir_lc2ms=$LC2MS_DIR/bin
export JAVA_TOOL_OPTIONS=-Djava.util.logging.config.file=$InJava_Par/JULogging.properties

# - Collect input filenames
command cd $STATION_DIR/1_proprietary
lchfile=$(ls *.fix.lch)
command cd -

# - Create output directory
mkdir $STATION_DIR/2_miniseed_basic

# - Copy process-steps.json file down to station directory
cp $STATION_DIR/1_proprietary/process-steps.json $STATION_DIR

# - Run executable
echo "Running lc2ms: converts LCHEAPO file(s) to miniSEED"
(command cd $Execut_dir_lc2ms 
./lc2ms $lchfile -d "$STATION_DIR" -i "1_proprietary" -o "2_miniseed_basic" -m ":%E.%S.00.%C.%Y.%D.%T.%H_%I.mseed" --experiment "4G" --sitename "HOCT" --obstype "HydroOctopus" --sernum "01" -p $Config_lc2ms_Path/lc2ms.properties 
)

# -Forcing data quality to D in miniseed files
echo ""
echo "============================================================"
echo "Forcing data quality to D"
echo "------------------------------------------------------------"
command cd $STATION_DIR
sdp-process -c="Forcing data quality to D" --cmd="msmod --quality D -i 2_miniseed_basic/*.mseed"
command cd -

# - Copy process-steps.json file up to new miniseed directory
cp $STATION_DIR/process-steps.json $STATION_DIR/2_miniseed_basic


