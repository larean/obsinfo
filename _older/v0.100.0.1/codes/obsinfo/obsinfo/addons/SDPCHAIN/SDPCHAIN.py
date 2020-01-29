""" 
Create OCA-JSON object from obs-info network
"""
import obsinfo
import json

proprietary_dir='1_proprietary'
basic_miniseed_dir='2_basic_miniseed'
corrected_miniseed_dir='3_corrected_miniseed'
f=None  # output file
sta_folder=None

################################################################################       
def write_process_script(station,station_folder,
                            proprietary_format=None,
                            extra_commands=None):
    """writes OBS data processing script using SDPCHAIN software
        
        station: an obsinfo.station object
        station_folder: base folder for the station data (existing data should be in:
                    - station_folder/2_basic_miniseed_dir if it's miniseed
                    - station_folder/1_proprietary if it's proprietary
        proprietary format:  if known, will write a sequence using the codes
                             otherwise will write a placeholder step
        extra_steps     : list of command-line commands to use, will be run
                        using sdp-process so that process-steps.json is appended
    
        The sequence of commands will be:
            1: optional proprietary format steps (creates miniseed from
                         proprietary format, will write to basic miniseed dir)
            2: optional extra_steps (any cleanup needed for the basic
                miniseed data, should either overwrite the existing data or
                remove the original files so that subsequent steps only see the
                cleaned data)
            3: leap-second corrections, if necessary
            3: msdrift (creates drift-corrected miniseed)
            4: ms2sds on drift-corrected data
            5: ms2sds on basic miniseed data
        
    """   
    output_file=station.name+'process.sh'
    sta_folder=station_folder   # Just copying to persistant
    with open(output_file,'w') as f:
        __write_header()
        if proprietary_format:
            __write_proprietary_steps(proprietary_format)
        if extra_commands:
            __write_extra_command_steps(extra_commands)
        if station.hasleapYear:
            __write_leapyear_steps(station.leapyear)
            __write_msdrift_step("temp_leapyear_correction",station.linear_drift)
            __remove_leapyear_step_mseeds(station.leapyear)
        else:
            __write_msdrift_step(basic_miniseed_dir,station.linear_drift)
        __write_ms2sds_steps()
        f.close()
                
############################################################################
def __write_header():
    f.write("""\
#!/bin/bash
#  This script assumes that you have SDPCHAIN installed on your system
#  SDPCHAIN includes the executables:
#           msdrift (applies a drift correction to miniseed data)
#           ms2sds  (converts miniseed data to sds format)
#           sdp-process (creates a process-step for any command)
#           xxxxxxx (reruns the commands in a process-steps.json file)

# ============================================================================
#  1: Set up the paths to the data and the executables
MSDRIFT_DIR={}
MS2SDS_DIR={}
STATION_DIR={}

""".format(msdrift_dir,ms2sds_dir,station_dir))

############################################################################
def __write_proprietary_steps(
                            proprietary_format,
                            output_is_reference==False
                            network='XX',
                            station='XXXX',
                            channel_correspondance=None):
""" Write steps to convert from proprietary format to miniSEED
    
    Inputs:
        proprietary_format: string naming the format: only LCHEAPO has been defined
        output_is_reference: output will be used as the basic miniseed reference
"""
    if proprietary_format == "LCHEAPO"
        format_name=proprietary_format
        conversion_command='{}/lc2ms'.format(lc2ms_dir)
        input_files='*.fix.lch'
    else:
        print(f"unknown proprietary format: '{proprietary_format}', writing placeholder")
        format_name='PROPRIETARY'
        conversion_command=''
        input_files=''
        # All data is assumed to have the name *.fix.lch
    f.write(f"""\

# ============================================================================
# 1a: CONVERT {format_name} DATA TO MINISEED
MY_CONVERSION_PROGRAM='{conversion_command}'
MY_DATA_FILES='$STATION_DIR/{proprietary_dir}/{input_files}'
$MY_CONVERSION_PROGRAM $MY_DATA_FILES -net {network} -sta {station} -inst {channel_correspondence} -o $STATION_DIR/{basic_miniseed_dir}

"""

############################################################################
def __write_extra_command_steps(extra_commands):
    """
    Write extra command lines, embedded in sdp-process
    
    Input:
        extra_commands: list of strings containing extra commands
    """
    if not isa(extra_commands,'list'):
        error('extra_commands is not a list')
    f.write('''
# ============================================================================
# 1x: ADDITIONAL PREP OF BASIC MINISEED FILES
# Generally used to combine files inot one/channel or to fix -net, -sta, -chan
#      and/or -qual
#     This is dangerous and should be unnecessary: If you use extra commands,
#     they should change the files in-place or get rid of the old versions'''
    for cmd_line in extra_commands:
        f.write('sdp-process {cmd_line}\n')

############################################################################
def __write_leapyear_steps(leapyear_info):
    print('Not yet written.  Will create temporary files on first step to drift correction')

############################################################################
def __remove_leapyear_step_files(leapyear_info):
    print('Not yet written.  Remove temporary leapyear-corrected files')

############################################################################
def __write_msdrift_step(input_directory,linear_correction):
    """ 
    Writes the msdrift lines of the script
    """
    f.write(f"""\

# ============================================================================
# 2: DRIFT-CORRECT MINISEED DATA
MSDRIFT_CMD='{msdrift_dir}/msdrift'
INPUT_FILES='$STATION_DIR/{input_directory}/*.mseed'
OUTPUT_DIR=$STATION_DIR/{corrected_miniseed_dir}
# Create Corrected miniseed directory if it doesn't exist
mkdir $OUTPUT_DIR
$MSDRIFT_CMD $INPUT_FILES -s{s_inst};{s_ref} -e{e_inst};{e_ref} -o $OUTPUT_DIR

"""

############################################################################
def __write_ms2sds_steps(output_uncorrected_data=True):

    """ 
    Writes the ms2sds lines of the script
    """
    f.write(f"""\

# ============================================================================
# 3: SDS VERSION OF CORRECTED DATA
MS2SDS_CMD='{ms2sds_dir}/ms2sds'
INPUT_FILES='$STATION_DIR/{corrected_miniseed_dir}/*.mseed'
OUTPUT_DIR=$STATION_DIR/SDS
# Create output directory if it doesn't exist
mkdir $OUTPUT_DIR
$MS2SDS_CMD $INPUT_FILES -o $OUTPUT_DIR

"""
    if output_uncorrected_data:
    f.write(f"""\

# ============================================================================
# 3b: SDS VERSION OF UNCORRECTED DATA
INPUT_FILES='$STATION_DIR/{basic_miniseed_dir}/*.mseed'
$MS2SDS_CMD $INPUT_FILES -o $OUTPUT_DIR

"""
