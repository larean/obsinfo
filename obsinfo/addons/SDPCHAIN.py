""" 
Generate scripts needed to go from basic miniSEED to data center ready
"""
import obsinfo
from obsinfo.network import network as oi_network
import os.path
import sys
from obspy.core import UTCDateTime

SEPARATOR_LINE="\n# " + 60 * "=" + "\n"


################################################################################       
def process_script(station, station_dir,
                    distrib_dir='/opt/sdpchain',
                    input_dir='miniseed_basic',
                    corrected_dir='minseed_corrected',
                    extra_commands=None,
                    include_header=True,
                    SDS_uncorr_dir='SDS_uncorrected',
                    SDS_corr_dir=  'SDS_corrected',
                  ):
    """Writes OBS data processing script using SDPCHAIN software
        
        station:          an obsinfo.station object
        station_dir:      base directory for the station data
        input_dir:        directory beneath station_dir for input (basic)
                          miniseed data ['miniseed_basic']
        corrected_dir:    directory beneath station_dir for output (corrected)
                          miniseed data ['miniseed_corrected']
        SDS_corr_dir:     directory beneath station_dir in which to write
                          SDS structure of corrected data (ideally
                          ../SOMETHING if ms2sds could write all to the
                          same directory)
        SDS_uncorr_dir:   directory beneath station_dir in which to write
                          SDS structure of uncorrected data (ideally
                          ../SOMETHING if ms2sds could write all to the
                          same directory)
        include_header:   whether or not to include the bash script header
                          ('#!/bin/bash') at the top of the script [True]
        distrib_dir:      Base directory of sdpchain distribution ['/opt/sdpchain']
    
        The sequence of commands is:
            1: optional proprietary format steps (proprietary format -> basic miniseed, separate)
            2: optional extra_steps (any cleanup needed for the basic
                miniseed data, should either overwrite the existing data or
                remove the original files so that subsequent steps only see the
                cleaned data)
            3: ms2sds on basic miniseed data
            4: leap-second corrections, if necessary
            5: msdrift (creates drift-corrected miniseed)
        
    """   
    leap_corr_dir='miniseed_leap_corrected'
    
    s=''
    if include_header:
        s += __header(station.code)
    s += __setup_variables(distrib_dir,station_dir)
    if extra_commands:
        s += __extra_command_steps(extra_commands)
    s += __ms2sds_script(station,input_dir,SDS_uncorr_dir)
    t =  __leap_second_script(station.clock_corrections.get('leapseconds',None),
                            input_dir,leap_corr_dir)
    if t:
      s+=t
      input_dir=leap_corr_dir
    s += __msdrift_script(input_dir,corrected_dir,station.clock_corrections)
    s += __force_quality_script(corrected_dir,'Q')
    s += __ms2sds_script(station,corrected_dir,SDS_corr_dir)

    return s
                    
############################################################################
def __header(station_name):

    s =  "#!/bin/bash\n"
    s += SEPARATOR_LINE + f"Working on station {station_name}" + SEPARATOR_LINE

    return s

############################################################################
def __setup_variables(distrib_dir,station_dir):

    s = SEPARATOR_LINE + "# SDPCHAIN STEPS" + SEPARATOR_LINE
    s += "#  - Set up paths\n"
    s += f"STATION_DIR={station_dir}\n"
    s += f"MSDRIFT_EXEC={os.path.join(distrib_dir,'bin','msdrift')}\n"
    s += f"MSDRIFT_CONFIG={os.path.join(distrib_dir,'config','msdrift.properties')}\n"
    s += f"MS2SDS_EXEC={os.path.join(distrib_dir,'bin','ms2sds')}\n"
    s += f"MS2SDS_CONFIG={os.path.join(distrib_dir,'config','ms2sds.properties')}\n"
    s += f"SDP-PROCESS_EXEC={os.path.join(distrib_dir,'bin','sdp-process')}\n"
    s += "\n"
    
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
def __ms2sds_script(station,in_path,out_path):

    """ 
    Writes the ms2sds lines of the script
    """
    sta=station.code
    net=station.network_code
    
    s =  f'echo "{"-"*60}"\n'
    s += 'echo "Running MS2SDS: MAKE SDS ARCHIVE"\n'
    s += f'echo "{"-"*60}"\n'
   
    s += f'in_dir="{in_path}"\n'
    s += f'out_dir="{out_path}"\n'
    
    s += '# - Create output directory\n'
    s += 'mkdir $STATION_DIR/$out_dir\n'
    
    s += '# - Collect input filenames\n'
    s += 'command cd $STATION_DIR/$in_dir\n'
    s += 'mseedfiles=$(ls *.mseed)\n'
    s += 'command cd -\n'
    s += 'echo "mseedfiles=" $mseedfiles\n'
    
    s += '# - Run executable\n'
    s += '$MS2SDS_EXEC $mseedfiles -d $STATION_DIR -i $in_dir -o $out_dir '
    s += f'--network "{net}" --station "{sta}" -a SDS -p $MS2SDS_CONFIG\n'
    s += '\n'
    
    return s

############################################################################
def  __leap_second_script(leapseconds,in_dir,out_dir):
    """ 
    Create leap-second correction text
    
    Inputs:
        leapseconds: list of dictionaries from network information file
    """
    if not leapseconds:
        return ""
    
    s =  f'echo "{"-"*60}"\n'
    s += 'echo "LEAPSECOND CORRECTIONS"\n'
    s += f'echo "{"-"*60}"\n'
    
    s += f'in_dir={in_dir}\n'
    s += f'out_dir={out_dir}\n'
    
    s += '# - Create output directory\n'
    s += 'mkdir $STATION_DIR/$out_dir\n'
    
    s += '# - Copy files to output directory\n'
    s += 'cp $STATION_DIR/$in_dir/*.mseed $STATION_DIR/$out_dir\n'    
    
    for leapsecond in leapseconds:
        if leapsecond['corrected_in_basic_miniseed']:
            s += "# LEAP SECOND AT {} ALREADY CORRECTED IN BASIC MINISEED, DOING NOTHING\n".format(\
                leapsecond['time'])
            return s
        temp=leapsecond['time'].split('T')
        d=UTCDateTime(temp[0])
        leap_time=d.strftime('%Y,%j,')+temp[1].rstrip('Z')
        s += 'echo ""\n'
        s += f'echo "{"="*60}"\n'
        s += 'echo "Running LEAPSECOND correction"\n'
        s += f'echo "{"-"*60}"\n'
        if leapsecond['type']=="+":
            s += 'sdp-process -d $STATION_DIR -c="Shifting one second BACKWARDS after positive leapsecond" '
            s += f' --cmd="msmod --timeshift -1 -ts {leap_time} -s -i $out_dir/*.mseed"\n'
            s += 'sdp-process -c="Marking the record containing the positive leapsecond" '
            s += f' --cmd="msmod --actflags 4,1 -tsc {leap_time} -tec {leap_dir} -s -i $out_dir/*.mseed"\n'
        elif leapsecond['type']=="-":
            s += 'sdp-process -c="Shifting one second FORWARDS after negative leapsecond" '
            s += f' --cmd="msmod --timeshift +1 -ts {leap_time} -s -i $out_dir/*.mseed"\n'
            s += 'sdp-process -c="Marking the record containing the negative leapsecond" '
            s += f' --cmd="msmod --actflags 5,1 -tsc {leap_time} -tec {leap_time} -s -i $out_dir/*.mseed"\n'
        else:
            s += 'ERROR: leapsecond type "{}" is neither "+" nor "-"\n'.format(leapsecond['type'])
            sys.exit(2)
    return s
      
############################################################################
def  __msdrift_script(in_path,out_path,clock_corrs,):
    """ 
    Write msdrift lines of the script
    
    Inputs:
        in_path
        out_path
        clock_corrs
    """
    s =  f'echo "{"-"*60}"\n'
    s += 'echo "Running MSDRIFT: CORRECT LINEAR CLOCK DRIFT"\n'
    s += f'echo "{"-"*60}"\n'

    s += f'in_dir={in_path}\n'
    s += f'out_dir={out_path}\n'
    
    s += "# - Create output directory\n"
    s += 'mkdir $STATION_DIR/$out_dir\n'

    s += '# - Collect input filenames\n'
    s += f'command cd $STATION_DIR/$in_dir\n'
    s += 'mseedfiles=$(ls *.mseed)\n'
    s += 'command cd -\n'
    s += 'echo "mseedfiles=" $mseedfiles\n'
    
    if 'linear_drift' in clock_corrs:
        lin_corr=clock_corrs['linear_drift']
        s += '# - Run executable\n'
        s += f'START_REFR="{str(lin_corr["start_sync_reference"]).rstrip("Z")}"\n'
        s += f'START_INST="{str(lin_corr["start_sync_instrument"]).rstrip("Z")}"\n'
        s += f'END_REFR="{str(lin_corr["end_sync_reference"]).rstrip("Z")}"\n'
        s += f'END_INST="{str(lin_corr["end_sync_instrument"]).rstrip("Z")}"\n'
        s += f'$MSDRIFT_EXEC $mseedfiles -d $STATION_DIR -i $in_dir -o $out_dir '
        s += f'-m "%E.%S.00.%C.%Y.%D.%1_%2.mseed:%E.%S.00.%C.%Y.%D.%1_%2_driftcorr.mseed" '
        s += f'-s "$START_REFR;$START_INST" '
        s += f'-e "$END_REFR;$END_INST" '
        #s += f'-c "comment.txt" '
        s += f'-p $MSDRIFT_CONFIG\n'
        s += '\n'
    else :
        while lin_corr in clock_corrs['linear_drifts'] :
            s += + SEPARATOR+LINE
            s += + 'ERROR, CANT YET APPLY MULTIPLE TIME CORRECTIONS (SHOULD CHANGE\n'
            s += + 'MSDRIFT TO ONLY WRITE GIVEN TIME RANGE AND BE ABLE TO APPEND TO EXISTING FILE?)\n'
            s += + SEPARATOR+LINE
    return s
        
############################################################################
def  __force_quality_script(in_path,quality='Q'):
    """ 
    Force data quality to Q
    
    Inputs:
        in_path
        quality
    """
    s =  f'echo "{"-"*60}"\n'
    s += 'echo "Forcing data quality to Q"\n'
    s += f'echo "{"-"*60}"\n'
    s += f'$SDP-PROCESS_EXEC -d $STATION_DIR -c="Forcing data quality to Q" --cmd="msmod --quality Q -i $outdir/*.mseed"\n'

    return s

################################################################################ 
def _console_script(argv=None):
    """
    Console-level processing script
    
    requires SDPCHAIN programs msdrift and ms2sds, and IRIS program msmod
    
    Currently usese 'SDS_corrected' and 'SDS_uncorrected' as default SDS directories
    Would be better to use ../SDS_[un]corrected so that all data are together,
    but ms2sds is not yet capable of putting data in an existing SDS directory
    
    """
    from argparse import ArgumentParser

    parser = ArgumentParser( prog='obsinfo-make_process_scripts_SDPCHAIN',description=__doc__)
    parser.add_argument( 'network_file', help='Network information file')
    parser.add_argument( 'station_data_path', help='Base path containing station data')
    parser.add_argument( 'distrib_dir', help='Path to SDPCHAIN software',default='/opt/sdpchain')
    parser.add_argument( '-i', '--input_dir', default='miniseed_basic',
        help='subdirectory of station_data_path/{STATION}/ containing input *.mseed files')
    parser.add_argument( '-o', '--corrected_dir', default='miniseed_corrected',
        help='subdirectory of station_data_path/{STATION}/ to put corrected *.mseed files')
    parser.add_argument( '--SDS_corr_dir', default='SDS_corrected',
        help='subdirectory of station_data_path/{STATION}/ for SDS structure of corrected data')
    parser.add_argument( '--SDS_uncorr_dir', default='SDS_uncorrected',
        help='subdirectory of station_data_path/{STATION}/ for SDS structure of uncorrected data')
    parser.add_argument( '-v', '--verbose',action="store_true",
        help='increase output verbosiy')
    parser.add_argument( '--no_header',action="store_true",help='do not include file header')
    parser.add_argument( '-q', '--quiet',action="store_true",
        help='run silently')
    args = parser.parse_args()
        
    # READ IN NETWORK INFORMATION
    if not args.quiet:
        print(f"Creating SDPCHAIN process scripts, ",end="")
    network=oi_network(args.network_file)
    if not args.quiet:
        print(f"network {network.network_info.code}, stations ",end="")
        if args.verbose:
            print("")

    first_time=True
    for name,station in network.stations.items():
        if not args.quiet:
            if args.verbose:
                print(f"\t{name}",end="")
            else:
                if first_time:
                    print(f"{name}",end="")
                else:
                    print(f", {name}", end="")
        station_dir=os.path.join(args.station_data_path,name)
        script=process_script(station,station_dir,
                                distrib_dir=args.distrib_dir,
                                input_dir=args.input_dir,
                                corrected_dir=args.corrected_dir,
                                SDS_uncorr_dir=args.SDS_uncorr_dir,
                                SDS_corr_dir=args.SDS_corr_dir,
                                include_header=not args.no_header)
        fname='process_'+name+'_SDPCHAIN.sh'
        if args.verbose:
            print(f" ... writing file {fname}")
        with open(fname,'w') as f:
            #f.write(f'#!/bin/bash\n\n')
            #f.write('#'+'='*60 + '\n')
            #f.write(f'echo "Running SDPCHAIN processes on station {name}"\n')
            #f.write('#'+'='*60 + '\n')
            f.write(script)
            f.write('\n')
            f.close()
        first_time=False
    if not args.verbose and not args.quiet:
        print("")
