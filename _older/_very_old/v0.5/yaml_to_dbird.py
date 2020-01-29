import yaml
import pprint
import sys
import copy
import math as m

campaign_file='EMSOMOMAR2016.campaign.yaml'
network_file= 'EMSOMOMAR2016.network.yaml'
instrument_file='INSU-IPGP.instrumentation.yaml'

########################################### 
def main():
    orig_netinfo,stations,instruments,campaign=\
        read_param_files(network_file,instrument_file,campaign_file)
   
    for name,station in stations.items():
        print('*'*20 + orig_netinfo['code'] + '.' + name + '*'*20)
        instrument=find_instrument(name,station,instruments)
        #print(instrument)
        if not instrument:
            continue
        station['instrument']['parameters']=instrument.copy()
        station['instrument']['facility']=instruments['facility'].copy()
        station=add_network(station,campaign,orig_netinfo)
        #prettyprint_station(station,name)
        print_dbird(station,name)

########################################### 
def print_dbird(station,name):
    """write DBIRD for one station"""
    identifier=station['network']['code'] + '.' + name
    version="2"
    f1=sys.stdout  # Kludge to write to stdout, must not close at end!
    # Uncomment the following (and f1.close() at end) to write to unique file
    # f1=open(identifier)

    #  with open(identifier) as f1:
    f1.write("version " + version + "\n")

    # WRITE ORGANIZATION INFO
    orig_org=station['instrument']['facility']
    f1.write('originating_organization "{}" "{}" "{}" "{}"\n'.format(\
          orig_org['full_name'],orig_org['email'],orig_org['website'],
          orig_org['phone_number']))
    f1.write('\n')

    # WRITE NETWORK INFO
    f1.write('begin_network\n')
    network=station['network']
    f1.write('  NET1 "{}" "{}" "{}" {} {} "{}"\n'.format(\
                network['code'],network['name'],network['email'],
                network['start_date'],network['end_date'],
                network['telephone']))
    f1.write('end_network\n')
    f1.write('\n')

    # WRITE STATION INFO
    #import pprint
    #pp=pprint.PrettyPrinter(width=131, compact=True)
    #pp.pprint(station)
    
    f1.write('begin_station\n')
    inst_SN=station['instrument']['serial_number']
    sample_rate=station['sample_rate']
    # NAME, DATES AND POSITION LINE
    pos=station['location_codes']['00']
    lat=float(pos['latitude'])
    m_per_degree_lat=1852*60
    m_per_degree_lon=m_per_degree_lat*m.cos(lat*m.pi/180)
    location_str=station.get('station_location',network['network_location'])
    f1.write('  {} {} {} ({} {:.6f}) ({} {:.6f}) ({} {}) "{}"\n'.format(\
                name,station['start_date'],station['end_date'],
                pos['latitude'],
                float(pos['lat_uncert_m'])/m_per_degree_lat,
                pos['longitude'],
                float(pos['lon_uncert_m'])/m_per_degree_lon,
                pos['elevation'],
                pos['elev_uncert_m'],
                location_str))
    # CONTACT AND OWNER LINES
    f1.write('  Contact {}\n'.format(orig_org['email']))
    f1.write('  Owner {}\n'.format(orig_org['full_name']))
    
    params=station['instrument']['parameters']
    channel_dict=dict()
#     for channel in params['channels']:
#         channel_dict[channel]=dict()

    # EQUIPMENT line: type, description, manufacurer, vendor, model, Serial#
    f1.write('  #Equipment {}\n'.format(equip_str(params['equipment'],inst_SN) ) )
                
    # COMMENT LINES
    f1.write('  #Comment "{}"\n'.format(station['comments_time'].strip()))
    f1.write('  #Comment "Time base = {}; Start sync GPS={}, inst={}; End sync GPS={}, inst={}"\n'.format(\
                station['time_base'],
                station['start_sync_GPS'],
                station['start_sync_inst'],
                station['end_sync_GPS'],
                station['end_sync_inst']))
    f1.write('  #Comment "Location is based on: {}"\n'.format(pos['loc_type']))
    if station['comments_other']:
        for line in station['comments_other']:
            if line:
                f1.write('  Comment "{}"\n'.format(line))
    f1.write('\n')
    
    # LOCATION LINE(S)    
    f1.write('  begin_location\n')
    i=0
    for loc,pos in station['location_codes'].items():
        i=i+1
        name='LOC'+'{:d}'.format(i)
        for key in channel_dict:
            if loc in key:
                channel_dict[key]['loc_code']=name
        lat=float(pos['latitude'])
        m_per_degree_lat=1852*60
        m_per_degree_lon=m_per_degree_lat*m.cos(lat*m.pi/180)
        f1.write('    {} "{}" ({} {:.6f}) ({} {:.6f}) ({} {}) "seafloor" "unknown"\n'.format(\
            name,loc,
            pos['latitude'],
            float(pos['lat_uncert_m'])/m_per_degree_lat,
            pos['longitude'],
            float(pos['lon_uncert_m'])/m_per_degree_lon,
            pos['elevation'],
            pos['elev_uncert_m']))
    f1.write('  end_location\n\n')

    # DATALOGGER LINES (NEW) ABOUT DATALOGGER
    f1.write('  #begin_datalogger\n')
    f1.write('  #  LOGGER {}\n'.format(equip_str(params['datalogger'],inst_SN)))
    f1.write('  #end_datalogger\n\n')
    
    # SENSOR LINES
    # COLLECT SENSOR DEFINITIONS
    sensor_dict=collect_channel_params(params['channels'],'sensor')
    #sensor_dict=check_SN(sensor_dict,inst_SN)
    # Print LINES
    f1.write('  begin_sensor\n')
    for key in sorted(sensor_dict):
        # NEED TO PUT NAMES IN CHANNEL_DICT[key]['sensor_code']
        f1.write('    SEN{} "{}" "{}" "{}" {} {}\n'.format(
                key,
                sensor_dict[key]['specs']['description'],
                choose_SN(sensor_dict[key]['specs']['serial_number'],inst_SN),
                sensor_dict[key]['specs']['DBIRD_file'],
                sensor_dict[key]['specs']['azimuth'],
                sensor_dict[key]['specs']['dip']
                   )
                )
        f1.write('    #SEN{} {} "{}" {} {}\n'.format(
                key,
                equip_str(sensor_dict[key]['specs'],inst_SN),  
                sensor_dict[key]['specs']['DBIRD_file'],
                sensor_dict[key]['specs']['azimuth'],
                sensor_dict[key]['specs']['dip'] )
                )
    f1.write('  end_sensor\n\n')
        
    # PREAMPLIFIER LINES
    # COLLECT PREAMPLIFIER DEFINITIONS
    preamp_dict=collect_channel_params(params['channels'],'ana_filter')
    #preamp_dict=check_SN(sensor_dict,inst_SN)
    # Print LINES
    f1.write('  begin_ana_filter\n')
    for key in sorted(preamp_dict):
        # NEED TO PUT NAMES IN CHANNEL_DICT[key]['ana_filter_code']
        f1.write('    AFILT{} "{}" "{}" "{}"\n'.format(
                key,
                preamp_dict[key]['specs']['description'],
                choose_SN(preamp_dict[key]['specs']['serial_number'],inst_SN),
                preamp_dict[key]['specs']['DBIRD_file'])
                )
        f1.write('    #AFILT{} {} "{}"\n'.format(
                key,
                equip_str(preamp_dict[key]['specs'],inst_SN),  
                preamp_dict[key]['specs']['DBIRD_file'])
                )
    f1.write('  end_ana_filter\n\n')

    # DIGITIZER LINES 
    f1.write('  begin_digitizer\n')
    f1.write('    DIGI "{}" "{}" "{}"\n'.format(
                params['digitizer']['description'],
                choose_SN(params['digitizer']['serial_number'],inst_SN),
                params['digitizer']['DBIRD_file'])
            )
    f1.write('    #DIGI {} "{}"\n'.format(
                equip_str(params['digitizer'],inst_SN),
                params['digitizer']['DBIRD_file'])
            )
    f1.write('  end_digitizer\n\n')
    for key in channel_dict:
            channel_dict[key]['digitzer_code']='DIGI'
            
    # DECIMATION LINES 
    f1.write('  begin_decimation\n')
    # Put sample rate into DBIRD filename if necessary
    DBIRD_file=params['digital_filter']['DBIRD_file'].replace(
                    '{sample_rate}','{:g}'.format(sample_rate))
    f1.write('    DECIM "{}" "{}" "{}"\n'.format(
                params['digital_filter']['description'],
                choose_SN(params['digital_filter']['serial_number'],inst_SN),
                DBIRD_file)
            )
    f1.write('    #DECIM {} "{}"\n'.format(
                equip_str(params['digital_filter'],inst_SN),
                DBIRD_file)
            )
    f1.write('  end_decimation\n\n')
    for key in channel_dict:
            channel_dict[key]['dig_filter_code']='DECIM'
            
    # CHANNEL LINES 
    f1.write('  begin_channel\n')
    for key,val in sorted(channel_dict.items()):
        f1.write('{} {} {} {} {} {} CG STEIM1 {} {} {}'.format(
                    val['loc_code'],
                    key.split(':')[0],
                    val['sensor_code'],
                    val['ana_filter_code'],
                    val['digitizer_code'],
                    val['dig_filter_code'],
                    start_date,
                    end_date,
                    network
                    )
                )
    f1.write('    NOT DONE YET!!!!!!!!!\n')
    f1.write('    MUST ADAPT BAND CODES TO SAMPLING RATE\n')
    f1.write('  end_channel\n\n')
  
    # AND SO ON...
    f1.write('end_station\n')
    #f1.close()
    return

########################################  
def SEED_band_code(input,sample_rate):
    """ Returns the SEED band code corresponding to the sample_rate and the input
    band code """
    if input in 'BHCFMLURPT':
        if sample_rate >=1000:
            return 'F'
        elif sample_rate >= 250:
            return 'C'
        elif sample_rate >= 80:
            return 'H'
        elif sample_rate >= 10:
            return 'B'
        elif sample_rate > 1:
            return 'M'
        elif sample_rate > 0.5:
            return 'L'
        elif sample_rate >= 0.001:
            return 'U'
        elif sample_rate >= 0.0001:
            return 'R'
        elif sample_rate >= 0.00001:
            return 'P'
        elif sample_rate >= 0.000001:
            return 'T'
        else:
            return 'Q'
    elif input in 'SEDG':
        if sample_rate >=1000:
            return 'G'
        elif sample_rate >= 250:
            return 'D'
        elif sample_rate >= 80:
            return 'E'
        elif sample_rate >= 10:
            return 'S'
        else:
            print('Output sampling rate too low for short-period data!')
            sys.exit(1)
    else:
        print('Unaccepted band code on input: "{}"'.format(input))
        sys.exit(1)

########################################  
########################################  
def choose_SN(primary,secondary):
    " Returns primary SN if it is defined, otherwise returns secondary"
    if primary:
        return primary
    else:
        return secondary
########################################  
def collect_channel_params(channel_dict,param_key):
    """ for a dictionary channel_dict with a sub-parameter param_key in each element,
    puts the value of channel_dict[...][param_key] into a new dictionary with key=name
    and value=channel_dict[...][param_key].  If channel_dict[...][param_key] is already 
    in the new dictionary, ignore it but add the channel_name to a list of "channels" in the
    corresponding dictionary element"""
    the_dict=dict()
    i=0
    for ch_key in channel_dict:
        add_key=True
        specs=channel_dict[ch_key][param_key]
        if the_dict:
            for key,val in the_dict.items():
                #print(specs)
                #print(val['specs'])
                #print(specs==val['specs'])
                if specs == val['specs']:
                    the_dict[key]['channels'].append(ch_key)
                    add_key=False
                    break
        if add_key:
            i=i+1
            new_name='{:d}'.format(i)
            the_dict[new_name]={'channels':[ch_key],'specs':specs}
    return the_dict
########################################### 
def equip_str(equip_dict,instSN=None):
    """Make a DBIRD-compatible string from an EquipmentType dictionary 
    (keys=type,description, vendor, model, serial_number)"""
    #print(equip_dict)
    if not equip_dict['serial_number']:
        equip_dict['serial_number']=instSN
    str='"{}" "{}" "{}" "{}" "{}" "{}"'.format(
                equip_dict['type'],
                equip_dict['description'],
                equip_dict['manufacturer'],
                equip_dict['vendor'],
                equip_dict['model'],
                equip_dict['serial_number']
            )
    return str

    
########################################### 
def read_param_files(network_file,instrument_file,campaign_file):
    """READ NETWORK AND INSTRUMENT FILES"""
    with open(network_file,'r') as f:
        network=yaml.load(f)['network']['network_info']
        #network=yaml.load(f)['network']['network_code']
        #network='4G'
    with open(network_file,'r') as f:
        stations=yaml.load(f)['network']['stations']
    with open(instrument_file,'r') as f:
        instruments=yaml.load(f)['instrumentation']
    with open(campaign_file,'r') as f:
        campaign=yaml.load(f)['campaign']
        
    return network,stations,instruments,campaign
  
########################################### 
def prettyprint_station(station,name):
    """Pretty-print one station"""
    print('='*80)
    print('Station {}:'.format(name))
    pp=pprint.PrettyPrinter(width=131, compact=True)
    pp.pprint(station)
    print('')
  
########################################### 
def add_network(station,campaign,orig_net_info):
    """ Add network information from campaign file to station """
    # The following overwrites the network code from network_file
    # but preserves the original network
    campaign_net_code=campaign['FDSN_network']['code']
    if not orig_net_info['code'] == campaign_net_code:
        print("*"*50)
        print("station-specied and campaign-specified network codes are different")
        print("     ('{}' versus '{}')".format(orig_net_info['code'],campaign_net_code))
        print(" Using '{}'".format(campaign_net_code))
        print("*"*50)
    station['network']=campaign['FDSN_network']
    station['network']['original_network']=orig_net_info['code']
    station['network']['network_location']=orig_net_info['location']
    return station
########################################### 
def find_instrument(name,station,instruments):
    """ Find instrument corresponding to one specified in station """
    inst_name=station['instrument']['model']
    inst_SN  =station['instrument']['serial_number']
    inst_facility = station['instrument']['facility']
    # Verify the supplying OBS park
    if inst_facility not in [ 
                instruments['facility']['short_name'],
                instruments['facility']['full_name']  
                ]:
        print("""Station "{}"'s facility name ("{}") """.format(name,inst_facility),end='') 
        print("does not match a facility in the instruments list:") 
        for facility in instruments:
            print("    " + facility)
        return

  # Allow Serial Number to match wildcard
    if inst_SN not in instruments['models'][inst_name] \
            and 'Default' in instruments['models'][inst_name]:
        inst_SN='Default'
    try:
        instrument=instruments['models'][inst_name][inst_SN]
    except:
        print('Instrument named {} with serial number {} NOT FOUND!'.format(\
                inst_name,inst_SN))
        return   
    return copy.deepcopy(instruments['models'][inst_name][inst_SN])


#############################################################################
if __name__ == '__main__':
    sys.exit(main())

