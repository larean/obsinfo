""" 
Return process steps needed to go from basic miniSEED to data center ready
"""
import obsinfo

SEPARATOR_LINE="\n# " + 60 * "=" + "\n"


################################################################################       
def process_script(station, station_dir,
                    msdrift_dir, ms2sds_dir,
                    basic_miniseed_dir='2_miniseed_basic',
                    corr_miniseed_dir='3_minseed_corrected',
                    extra_commands=None,
                    include_header=True,
                    msmod_path='$MS2SDS_DIR/bin'):
    """Writes OBS data processing script using SDPCHAIN software
        
        station: an obsinfo.station object
        station_dir:         base directory for the station data
        basic_miniseed_dir:  directory beneath station_dir for basic miniseed
                             data ['2_miniseed_basic']
        corr_miniseed_dir:   directory beneath station_dir for basic miniseed
                             data ['3_miniseed_corrected']
        extra_commands:      list of command-line commands to use, will be run
                             using sdp-process so that process-steps.json is appended
        include_header:      whether or not to include the bash script header
                             ('#!/bin/bash') at the top of the script [True]
        msmod_path:          Path to the msmod executable ['$MS2SDS_DIR/bin']
    
        The sequence of commands is:
            1: optional proprietary format steps (proprietary format -> basic miniseed)
            2: optional extra_steps (any cleanup needed for the basic
                miniseed data, should either overwrite the existing data or
                remove the original files so that subsequent steps only see the
                cleaned data)
            3: ms2sds on basic miniseed data
            4: leap-second corrections, if necessary
            5: msdrift (creates drift-corrected miniseed)
        
    """   
    # Best solution if ms2sds could write all to the same directory
    SDS_uncorr_dir='../SDS_uncorrected'
    SDS_corr_dir=  '../SDS_corrected'
    # Short-term solution
    SDS_uncorr_dir='SDS_uncorrected'
    SDS_corr_dir=  'SDS_corrected'

    s=''
    if include_header:
        s = s + __header()
    s = s + __setup_variables(msdrift_dir,ms2sds_dir,station_dir)
    if extra_commands:
        s = s + __extra_command_steps(extra_commands)
    # Make SDS from basic miniseed data
    s = s + __ms2sds_steps(station,basic_miniseed_dir,SDS_uncorr_dir,
                            msmod_path=msmod_path)
    # Correct clock (drift and possibly leapsecond)
    s = s + __clockcorr_steps(basic_miniseed_dir,
                            corr_miniseed_dir,
                            station.clock_corrections)
    # Make SDS from corrected miniseed data
    s = s + __ms2sds_steps(station,corr_miniseed_dir,SDS_corr_dir,
                            msmod_path=msmod_path)

    return s
                    
############################################################################
def __header():

    s = "#!/bin/bash\n"    
    return s

############################################################################
def __setup_variables(msdrift_dir,ms2sds_dir,station_dir):

    s = SEPARATOR_LINE + "# SDPCHAIN STEPS" + SEPARATOR_LINE
    s = s + "#  This script assumes that you have SDPCHAIN installed\n"
    s = s + "#  SDPCHAIN includes the executables:\n"
    s = s + "#           msdrift (applies a drift correction to miniseed data)\n"
    s = s + "#           ms2sds  (converts miniseed data to sds format)\n"
    s = s + "#           sdp-process (creates/appends a process-step.json file for any command)\n"
    s = s + '\n'
        
    s = s + "#  - Set up paths to data and executables\n"
    s = s + f"MSDRIFT_DIR={msdrift_dir}\n"
    s = s + f"MS2SDS_DIR={ms2sds_dir}\n"
    s = s + f"STATION_DIR={station_dir}\n"
    
    return s

############################################################################
def __extra_command_steps(extra_commands):
    """
    Write extra command lines, embedded in sdp-process
    
    Input:
        extra_commands: list of strings containing extra commands
    """
    s=SEPARATOR_LINE
    s=s+'# - EXTRA COMMANDS\n'
    if not isa(extra_commands,'list'):
        error('extra_commands is not a list')
    for cmd_line in extra_commands:
        s=s+'sdp-process --cmd="{cmd_line}"\n'
    return s

############################################################################
def __ms2sds_steps(station,in_path,out_path,msmod_path='$MS2SDS_DIR/bin'):

    """ 
    Writes the ms2sds lines of the script
    """
    station_code=station.code
    network_code=station.network_code
    
    s = SEPARATOR_LINE
    s = s + '# - MS2SDS: TRANSFORM DATA TO SDS FORMAT\n'
    s = s + 'echo ""\n'
    s = s + f'echo "{"="*60}"\n'
    s = s + 'echo "Running MS2SDS"\n'
    s = s + f'echo "{"-"*60}"\n'
    s = s + 'echo "MS2SDS directory = $MS2SDS_DIR"\n'
   
    s = s + '# - Configure properties file\n'
    s = s + 'command cd $MS2SDS_DIR/config/\n'
    s = s + 'rm ms2sds.properties\n'
    s = s + 'echo "# Text encoding : ISO 8859-1 (Latin 1)" >> ms2sds.properties\n'
    s = s + 'echo "# binaryDirpath = Path to msmod executable" >> ms2sds.properties\n'
    s = s + f'echo "binaryDirpath={msmod_path}" >> ms2sds.properties\n'
    # Path to temporary working directory
    s = s + 'echo "workingDirpath=$MS2SDS_DIR/working_rep" >> ms2sds.properties\n'
    # Comment for the application
    s = s + 'echo "applicationComment=Transform miniSEED files to SeisComp3 Data Structure" >> ms2sds.properties\n'
    s = s + 'command cd -\n'
    s = s + '\n'
    
    s = s + '# - Set up environment variables\n'
    s = s + 'InJava_Par=$MS2SDS_DIR/config\n'
    s = s + 'Config_ms2sds_Path=$MS2SDS_DIR/config\n'
    s = s + 'Execut_dir_ms2sds=$MS2SDS_DIR\n'
    s = s + 'export JAVA_TOOL_OPTIONS=-Djava.util.logging.config.file=$InJava_Par/JULogging.properties\n'
    s = s + '\n'
    
    s = s + '# - Collect input filenames\n'
    #s = s + 'workDir="/Volumes/PILAB_Donnees/${sitename}"\n'
    s = s + f'command cd $STATION_DIR/{in_path}\n'
    s = s + 'mseedfiles=$(ls *.mseed)\n'
    s = s + 'echo "mseedfiles=" $mseedfiles\n'
    s = s + 'command cd -\n'
    s = s + '\n'
    
    s = s + "# Create output directory, if it doesn't exist\n"
    s = s + f'mkdir $STATION_DIR/{out_path}\n'
    s = s + '\n'

    s = s + '# - Run executable\n'
    s = s + '(command cd $Execut_dir_ms2sds\n'
    s = s + f'./ms2sds $mseedfiles -d $STATION_DIR -i "{in_path}" -o "{out_path}" '
    s = s + f'--network "{network_code}" --station "{station_code}" '
    s = s + '-a SDS -p $Config_ms2sds_Path/ms2sds.properties) '
    s = s + '#-v\n'
    
    return s

############################################################################
def  __clockcorr_steps(in_path,out_path,clock_corrs,
                        force_quality_Q=True):
    """ 
    Write leap-second correction and msdrift lines of the script
    
    Inputs:
        in_path
        out_path
        clock_corrs
        force_quality_Q: Force the data quality to "Q" using a separate call
                         of msmod (should be unecessary once lc2ms is upgraded)
    """
    s = SEPARATOR_LINE
    s = s + '# - LEAPSECOND CORRECTION(S)\n'
    leapseconds=clock_corrs.get('leapseconds',None)
    if leapseconds:
        s = s + '# Placeholder\n'
    else:
        s = s + '# No leapseconds declared\n'
    s = s + '# NO LEAPSECOND CORRECTION SCRIPT!\n'
    s = s + "\n"
    
    # LINEAR CLOCK DRIFT
    s = SEPARATOR_LINE
    s = s + '# - MSDRIFT : CORRECT LINEAR CLOCK DRIFT\n'
    s = s + 'echo ""\n'
    s = s + f'echo "{"="*60}"\n'
    s = s + 'echo "Running MSDRIFT"\n'
    s = s + f'echo "{"-"*60}"\n'
    s = s + 'echo "MSDRIFT directory = $MSDRIFT_DIR"\n'
    s = s + '\n'

    s = s + '# - Configure properties file\n'
    s = s + 'command cd $MSDRIFT_DIR/config\n'
    s = s + 'rm msdrift.properties\n'
    s = s + 'echo "# Text encoding : ISO 8859-1 (Latin 1)" >> msdrift.properties\n'
    # Path to qedit executable" >> msdrift.properties
    s = s + 'echo "qeditDirpath=/opt/passcal/bin/" >> msdrift.properties\n'
    # Path to temporary working directory" >> msdrift.properties
    s = s + 'echo "workingDirpath=$MSDRIFT_DIR/working" >> msdrift.properties\n'
    # Comment for the application" >> msdrift.properties
    s = s + 'echo "applicationComment=Applies linear clock drift correction to miniSEED data\n" >> msdrift.properties\n'
    s = s + 'command cd -\n'
    s = s + '\n'

    s = s + '# - Set up environment variables\n'
    s = s + 'InJava_Par=$MSDRIFT_DIR/config\n'
    s = s + 'Config_msdrift_Path=$MSDRIFT_DIR/config\n'
    s = s + 'Execut_dir_msdrift=$MSDRIFT_DIR\n'
    s = s + 'export JAVA_TOOL_OPTIONS=-Djava.util.logging.config.file=$InJava_Par/JULogging.properties\n'

    s = s + '# - Collect input filenames\n'
    s = s + f'command cd $STATION_DIR/{in_path}\n'
    s = s + 'mseedfile=$(ls *.mseed)\n'
    s = s + 'command cd -\n'
    s = s + 'echo "mseedfiles=" $mseedfile\n'
    s = s + '\n'
    
    s = s + "# Create output directory if it doesn't exist\n"
    s = s + f'mkdir $STATION_DIR/{out_path}\n'
    s = s + '\n'

    if 'linear_drift' in clock_corrs:
        lin_corr=clock_corrs['linear_drift']
        s = s + '# - Run executable\n'
        s = s + f'START_REFR="{str(lin_corr["start_sync_reference"]).rstrip("Z")}"\n'
        s = s + f'START_INST="{str(lin_corr["start_sync_instrument"]).rstrip("Z")}"\n'
        s = s + f'END_REFR="{str(lin_corr["end_sync_reference"]).rstrip("Z")}"\n'
        s = s + f'END_INST="{str(lin_corr["end_sync_instrument"]).rstrip("Z")}"\n'
        s = s + 'for mfile in $mseedfile\n'
        s = s + 'do\n'
        s = s + '(command cd $Execut_dir_msdrift\n'
        s = s + f'./msdrift $mfile -d $STATION_DIR -i "{in_path}" -o "{out_path}" '
        s = s + f'-m "%E.%S.00.%C.%Y.%D.%1_%2.mseed:%E.%S.00.%C.%Y.%D.%1_%2_driftcorr.mseed" '
        s = s + f'-s "$START_REFR;$START_INST" '
        s = s + f'-e "$END_REFR;$END_INST" '
        s = s + f'-c "comment.txt" '
        s = s + f'-p $Config_msdrift_Path/msdrift.properties) #-v\n'
        s = s + 'done\n'
    else :
        while lin_corr in clock_corrs['linear_drifts'] :
            s = s + SEPARATOR+LINE
            s = s + 'ERROR, CANT YET APPLY MULTIPLE TIME CORRECTIONS (SHOULD CHANGE\n'
            s = s + 'MSDRIFT TO ONLY WRITE GIVEN TIME RANGE AND BE ABLE TO APPEND TO EXISTING FILE?)\n'
            s = s + SEPARATOR+LINE
        
    if force_quality_Q:
        s = s + "# -Forcing data quality to Q in miniseed files\n"
        s = s + 'echo ""\n'
        s = s + f'echo "{"="*60}"\n'
        s = s + 'echo "Forcing data quality to Q"\n'
        s = s + f'echo "{"-"*60}"\n'
        s = s + 'command cd $STATION_DIR\n'
        s = s + f'sdp-process -c="Forcing data quality to Q" --cmd="msmod --quality Q -i {out_path}/*.mseed"\n'
        s = s + 'command cd -\n'

    s = s + '# - Copy process-steps.json file up to corrected miniseed directory\n'
    s = s + f'cp $STATION_DIR/process-steps.json $STATION_DIR/{out_path}/\n'
    s = s + '\n'

    return s