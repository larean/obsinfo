#!/bin/bash

#============================================================
echo "Running SDPCHAIN processes on station BB_1"
#============================================================

# ============================================================
# SDPCHAIN STEPS
# ============================================================
#  This script assumes that you have SDPCHAIN installed
#  SDPCHAIN includes the executables:
#           msdrift (applies a drift correction to miniseed data)
#           ms2sds  (converts miniseed data to sds format)
#           sdp-process (creates/appends a process-step.json file for any command)

#  - Set up paths to data and executables
MSDRIFT_DIR=/Users/crawford/_Work/Parc_OBS/3_Development/Data_and_Metadata/SDPCHAIN/Software_IPGP-INSU_v20170222_modWayne/MSDRIFT
MS2SDS_DIR=/Users/crawford/_Work/Parc_OBS/3_Development/Data_and_Metadata/SDPCHAIN/Software_IPGP-INSU_v20170222_modWayne/MS2SDS
STATION_DIR=/Volumes/PARC_OBS_Wayne/DATA_EXPERIMENTS/2017-18.AlpArray/2017-18.AlpArray/BB_1

# ============================================================
# - MS2SDS: TRANSFORM DATA TO SDS FORMAT
echo ""
echo "============================================================"
echo "Running MS2SDS"
echo "------------------------------------------------------------"
echo "MS2SDS directory = $MS2SDS_DIR"
# - Configure properties file
command cd $MS2SDS_DIR/config/
rm ms2sds.properties
echo "# Text encoding : ISO 8859-1 (Latin 1)" >> ms2sds.properties
echo "# binaryDirpath = Path to msmod executable" >> ms2sds.properties
echo "binaryDirpath=/Users/crawford/bin" >> ms2sds.properties
echo "workingDirpath=$MS2SDS_DIR/working_rep" >> ms2sds.properties
echo "applicationComment=Transform miniSEED files to SeisComp3 Data Structure" >> ms2sds.properties
command cd -

# - Set up environment variables
InJava_Par=$MS2SDS_DIR/config
Config_ms2sds_Path=$MS2SDS_DIR/config
Execut_dir_ms2sds=$MS2SDS_DIR
export JAVA_TOOL_OPTIONS=-Djava.util.logging.config.file=$InJava_Par/JULogging.properties

# - Collect input filenames
command cd $STATION_DIR/2_miniseed_basic
mseedfiles=$(ls *.mseed)
echo "mseedfiles=" $mseedfiles
command cd -

# Create output directory, if it doesn't exist
mkdir $STATION_DIR/SDS_uncorrected

# - Run executable
(command cd $Execut_dir_ms2sds
./ms2sds $mseedfiles -d $STATION_DIR -i "2_miniseed_basic" -o "SDS_uncorrected" --network "4G" --station "BB_1" -a SDS -p $Config_ms2sds_Path/ms2sds.properties) #-v

# ============================================================
# - MSDRIFT : CORRECT LINEAR CLOCK DRIFT
echo ""
echo "============================================================"
echo "Running MSDRIFT"
echo "------------------------------------------------------------"
echo "MSDRIFT directory = $MSDRIFT_DIR"

# - Configure properties file
command cd $MSDRIFT_DIR/config
rm msdrift.properties
echo "# Text encoding : ISO 8859-1 (Latin 1)" >> msdrift.properties
echo "qeditDirpath=/opt/passcal/bin/" >> msdrift.properties
echo "workingDirpath=$MSDRIFT_DIR/working" >> msdrift.properties
echo "applicationComment=Applies linear clock drift correction to miniSEED data
" >> msdrift.properties
command cd -

# - Set up environment variables
InJava_Par=$MSDRIFT_DIR/config
Config_msdrift_Path=$MSDRIFT_DIR/config
Execut_dir_msdrift=$MSDRIFT_DIR
export JAVA_TOOL_OPTIONS=-Djava.util.logging.config.file=$InJava_Par/JULogging.properties
# - Collect input filenames
command cd $STATION_DIR/2_miniseed_basic
mseedfile=$(ls *.mseed)
command cd -
echo "mseedfiles=" $mseedfile

# Create output directory if it doesn't exist
mkdir $STATION_DIR/3_miniseed_corr

# - Run executable
START_REFR="2015-04-22T12:24:00"
START_INST="0"
END_REFR="2016-05-28T15:35:00.3660"
END_INST="2016-05-28T15:35:02"
for mfile in $mseedfile
do
(command cd $Execut_dir_msdrift
./msdrift $mfile -d $STATION_DIR -i "2_miniseed_basic" -o "3_miniseed_corr" -m "%E.%S.00.%C.%Y.%D.%1_%2.mseed:%E.%S.00.%C.%Y.%D.%1_%2_driftcorr.mseed" -s "$START_REFR;$START_INST" -e "$END_REFR;$END_INST" -c "comment.txt" -p $Config_msdrift_Path/msdrift.properties) #-v
done
# -Forcing data quality to Q in miniseed files
echo ""
echo "============================================================"
echo "Forcing data quality to Q"
echo "------------------------------------------------------------"
command cd $STATION_DIR
sdp-process -c="Forcing data quality to Q" --cmd="msmod --quality Q -i 3_miniseed_corr/*.mseed"
command cd -
# - Copy process-steps.json file up to corrected miniseed directory
cp $STATION_DIR/process-steps.json $STATION_DIR/3_miniseed_corr/


# ============================================================
# - MS2SDS: TRANSFORM DATA TO SDS FORMAT
echo ""
echo "============================================================"
echo "Running MS2SDS"
echo "------------------------------------------------------------"
echo "MS2SDS directory = $MS2SDS_DIR"
# - Configure properties file
command cd $MS2SDS_DIR/config/
rm ms2sds.properties
echo "# Text encoding : ISO 8859-1 (Latin 1)" >> ms2sds.properties
echo "# binaryDirpath = Path to msmod executable" >> ms2sds.properties
echo "binaryDirpath=/Users/crawford/bin" >> ms2sds.properties
echo "workingDirpath=$MS2SDS_DIR/working_rep" >> ms2sds.properties
echo "applicationComment=Transform miniSEED files to SeisComp3 Data Structure" >> ms2sds.properties
command cd -

# - Set up environment variables
InJava_Par=$MS2SDS_DIR/config
Config_ms2sds_Path=$MS2SDS_DIR/config
Execut_dir_ms2sds=$MS2SDS_DIR
export JAVA_TOOL_OPTIONS=-Djava.util.logging.config.file=$InJava_Par/JULogging.properties

# - Collect input filenames
command cd $STATION_DIR/3_miniseed_corr
mseedfiles=$(ls *.mseed)
echo "mseedfiles=" $mseedfiles
command cd -

# Create output directory, if it doesn't exist
mkdir $STATION_DIR/SDS_corrected

# - Run executable
(command cd $Execut_dir_ms2sds
./ms2sds $mseedfiles -d $STATION_DIR -i "3_miniseed_corr" -o "SDS_corrected" --network "4G" --station "BB_1" -a SDS -p $Config_ms2sds_Path/ms2sds.properties) #-v

