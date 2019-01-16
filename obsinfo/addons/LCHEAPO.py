""" 
Write extraction script for LCHEAPO instruments (proprietary to miniseed)
"""
import obsinfo
import obsinfo.network.network as oi_network
import os.path

SEPARATOR_LINE="\n# " + 60 * "=" + "\n"


################################################################################       
def process_script(station,
                    station_dir,
                    lc2ms_dir,
                    lcheapo_dir='1_proprietary',
                    input_dir='2_miniseed_basic',
                    extra_commands=None,
                    include_header=True):
    """Writes script to transform raw OBS data to miniSEED
        
        station: an obsinfo.station object
        station_dir: base directory for the station data
        lcheapo_dir:  directory beneath station_dir for LCHEAPO data
                             data ['1_proprietary']
        input_dir:  directory beneath station_dir for basic miniseed
                             data ['2_miniseed_basic']
            
    """   
    s = ''
    if include_header:
        s = s + __header()
    s = s + __setup_variables(lc2ms_dir,station_dir)
    s = s + __configure()
    s = s + __commandline(station,lcheapo_dir,input_dir)

    return s
                    
############################################################################
def __header():

    s = "#!/bin/bash\n"    
    return s

############################################################################
def __setup_variables(lc2ms_dir,station_dir):

    s = SEPARATOR_LINE + "# LCHEAPO STEPS" + SEPARATOR_LINE
    s = s + f'echo "{"="*60}"\n'
    s = s + 'echo "Running LC2MS"\n'
    s = s + f'echo "{"-"*60}"\n'
    s = s + "#  - Set up paths to data and executables\n"
    s = s + f"LC2MS_DIR={lc2ms_dir}\n"
    s = s + f"STATION_DIR={station_dir}\n"
    s = s + '\n'
    return s

############################################################################
def __configure() :

    s = ''
    s = s + '# - Configure properties file\n'
    s = s + 'command cd $LC2MS_DIR/config/\n'
    s = s + 'rm lc2ms.properties\n'
    s = s + 'echo "# Text encoding : ISO 8859-1 (Latin 1)" >> lc2ms.properties\n'
    # Path to the lch2mseed executable
    s = s + 'echo "binaryDirpath=$LC2MS_DIR/bin" >> lc2ms.properties\n'
    # Path for the temporary working directory
    s = s + 'echo "workingDirpath=$LC2MS_DIR/working" >> lc2ms.properties\n'
    # Comment for the application
    s = s + 'echo "applicationComment=This is a comment" >> lc2ms.properties\n'
    # Path and filename of the CSV file specifying OBS types/families" >> lc2ms.properties
    # (ignored if specifiedon the command line)" >> lc2ms.properties
    # (If relative path, use <binaryDirpath> + <relpath>)" >> lc2ms.properties
    # (If absent, use <binaryDirpath> + "./obs-config.csv")" >> lc2ms.properties
    s = s + 'echo "obsConfigFilepath=$LC2MS_DIR/config/obs-config.csv" >> lc2ms.properties\n'
    s = s + 'command cd -\n'
    s = s + '\n'
     
    s = s + '# - Set up environment variables\n'
    s = s + 'InJava_Par=$LC2MS_DIR/config/\n'
    s = s + 'Config_lc2ms_Path=$LC2MS_DIR/config/\n'
    s = s + 'Execut_dir_lc2ms=$LC2MS_DIR/bin\n'
    s = s + 'export JAVA_TOOL_OPTIONS=-Djava.util.logging.config.file=$InJava_Par/JULogging.properties\n'
    s = s + '\n'
   
    return s

############################################################################
def __commandline(station, in_path, out_path, 
            in_fnames='*.fix.lch',
            out_fnames_model='%E.%S.00.%C.%Y.%D.%T.%H_%I.mseed',
            force_quality_D=True):

    '''
        Write an lc2ms command line
        
        Inputs:
            station:       obsinfo station
            in_path:       relative path to directory containing input files
            in_fnames:     search string for input files within in_path ['*.fix.lch']
            out_path:      relative pth to directory for output files
            out_fnames_model: model for output filenames ['%E.%S.00.%C.%Y.%D.%T.%H_%I.mseed']
                              (should change to '%E.%S.%L.%C.%Y.%D.%T.%H_%I.mseed'
                               once lc2ms handles location codes)
            force_quality_D: uses a separate call to msmod to force the data
                              quality to "D" (should be unecessary once lc2ms is
                              upgraded)
        Output:
            string of bash script lines
    '''
    
    network_code = station.network_code
    station_code = station.code
    obs_type =     station.instrument.reference_code.split('_')[0]
    obs_SN   =     station.instrument.serial_number
    # CHANNEL CORRESPONDENCES WILL ALLOW THE CHANNEL NAMES TO BE EXPRESSED ON
    # THE COMMAND LINE, WITHOUT USING A DEDICATED CSV FILE
    #channel_corresp = station.instrument.channel_correspondances()
    
    s = ''
    s = s + "# - Collect input filenames\n"
    s = s + f'command cd $STATION_DIR/{in_path}\n'
    s = s + f'lchfile=$(ls {in_fnames})\n'
    s = s + 'command cd -\n'
    # s = s + 'echo "lchfile(s): " $lchfile\n'
    s = s + '\n'    
    
    s = s + '# - Create output directory\n'
    s = s + f'mkdir $STATION_DIR/{out_path}\n'
    s = s + '\n'

    s = s + '# - Copy process-steps.json file down to station directory\n'
    s = s + f'cp $STATION_DIR/{in_path}/process-steps.json $STATION_DIR\n'
    s = s + '\n'

    s = s + "# - Run executable\n"
    s = s + 'echo "Running lc2ms: converts LCHEAPO file(s) to miniSEED"\n'
    s = s + '(command cd $Execut_dir_lc2ms \n'
    s = s + f'./lc2ms $lchfile -d "$STATION_DIR" -i "{in_path}" -o "{out_path}" ' 
    s = s + f'-m ":{out_fnames_model}" ' 
    s = s + f'--experiment "{network_code}" ' 
    s = s + f'--sitename "{station_code}" ' 
    s = s + f'--obstype "{obs_type}" ' 
    s = s + f'--sernum "{obs_SN}" ' 
    # s = s + f'--channels "{channel_corresp}"' ' 
    s = s + '-p $Config_lc2ms_Path/lc2ms.properties \n'
    s = s + ')\n'
    s = s + '\n'

    if force_quality_D:
        s = s + "# -Forcing data quality to D in miniseed files\n"
        s = s + f'echo ""\necho "{"="*60}"\n'
        s = s + 'echo "Forcing data quality to D"\n'
        s = s + f'echo "{"-"*60}"\n'
        s = s + 'command cd $STATION_DIR\n'
        s = s + f'sdp-process -c="Forcing data quality to D" --cmd="msmod --quality D -i {out_path}/*.mseed"\n'
        s = s + 'command cd -\n'
        s = s + '\n'

    s = s + '# - Copy process-steps.json file up to new miniseed directory\n'
    s = s + f'cp $STATION_DIR/process-steps.json $STATION_DIR/{out_path}\n'
    s = s + '\n'
    
    return s

################################################################################ 
def _console_script(argv=None):
    """
    Create a bash-script to convert LCHEAPO data to basic miniSEED
    Data should be in station_data_path/{STATION_NAME}/{input_dir}/*.fix.lch
    
    requires O Dewee program lc2ms, and IRIS program msmod
    
    """
    from argparse import ArgumentParser

    parser = ArgumentParser( prog='obsinfo-make_process_scripts_LC2MS',description=__doc__)
    parser.add_argument( 'network_file', help='Network information file')
    parser.add_argument( 'station_data_path', help='Base path containing stations data')
    parser.add_argument( 'lc2ms_path', help='Path to lc2ms software')
    parser.add_argument( '-i', '--input_dir', default='1_proprietary',
        help='subdirectory of station_data_path/{STATION}/ containing input *.raw.lch files')
    parser.add_argument( '-o', '--output_dir', default='2_miniseed_basic',
        help='subdirectory of station_data_path/{STATION}/ to put output *.mseed files')
    parser.add_argument( '-v', '--verbose',action="store_true",
        help='increase output verbosity')
    parser.add_argument( '-q', '--quiet',action="store_true",
        help='run silently')
    args = parser.parse_args()
    
    if not args.quiet:
        print(f"Creating  LC2MS   process scripts, ",end="",flush=True)
    # READ IN NETWORK INFORMATION
    network=oi_network(args.network_file)
    if not args.quiet:
        print(f"network {network.network_info.code}, stations ",end="",flush=True)
        if args.verbose:
            print("")
    
    first_time=True
    for name,station in network.stations.items():
        if not args.quiet:
            if args.verbose:
                print(f"\t{name}",end="")
            else:
                if first_time:
                    print(f"{name}",end="",flush=True)
                else:
                    print(f", {name}", end="",flush=True)
        station_dir=os.path.join(args.station_data_path,name)
        script=process_script(station,
                                station_dir,
                                args.lc2ms_path,
                                lcheapo_dir=args.input_dir,
                                input_dir=args.output_dir,
                                include_header=False)
        fname='process_'+name+'_LC2MS.sh'
        if args.verbose:
            print(f" ... writing file {fname}",flush=True)
        with open(fname,'w') as f:
            f.write('#!/bin/bash\n\n')
            f.write('#'+'='*60 + '\n')
            f.write(f'echo "Running LC2MS processes on station {name}"\n')
            f.write('#'+'='*60 + '\n')
            f.write(script)
            f.write('\n')
            f.close()
        first_time=False
    if not args.verbose and not args.quiet:
        print("")