import yaml
import pprint
import sys
import copy
import math as m

campaign_file='EMSO-MOMAR2016.campaign.yaml'
network_file= 'EMSO-MOMAR2016.INSU-IPGP.network.yaml'
instrument_file='INSU-IPGP.instrumentation.yaml'

########################################### 
def main():
    facility_network,instruments,campaign=\
        read_param_files(network_file,instrument_file,campaign_file)
   
    for name,station in facility_network['stations'].items():
        print('\n'+'*'*20 + ' ' + name + ' ' + '*'*20)
        instrument=find_instrument(name,station,instruments)
        #print(instrument)
        if not instrument:
            continue
        station['instrument']['parameters']=instrument.copy()
        station['instrument']['facility']=instruments['facility'].copy()
        station['network']=campaign['FDSN_network']
        station['name']=station.get('FDSN_name',name)
        #prettyprint_station(station,name)
        print_dbird(station)

########################################### 
def print_dbird(station):
    """write DBIRD for one station"""
    # Prep variables
    sample_rate=station['sample_rate']
    identifier=station['network']['code'] + '.' + station['name']
    network=station['network']
    params=station['instrument']['parameters']
    channel_dict=dict()
    for channel in params['channels']:
        #print(channel)
        channel_dict[channel]=dict()
    
    
    version="2"
    f1=sys.stdout  # Kludge to write to stdout, must not close at end!
    # Uncomment the following (and f1.close() at end) to write to unique file
    # f1=open(identifier)

    #  with open(identifier) as f1:
    f1.write("version " + version + "\n")

    # WRITE ORGANIZATION INFO
    orig_org=station['instrument']['facility']
    f1.write(orig_org_str(orig_org)+'\n\n')

    # NETWORK LINE
    f1.write('begin_network\n')
    f1.write('  ' + network_str(network) + '\n')
    f1.write('end_network\n\n')

    # STATION LINES
    f1.write('begin_station\n')    
    f1.write('  ' + station_str(station) + '\n')
    f1.write('  #' + station_str(station,enhanced=True) + '\n')
    f1.write('  Contact {}\n'.format(orig_org['email']))
    f1.write('  Owner {}\n'.format(orig_org['full_name']))
    
    # EQUIPMENT line: type, description, manufacurer, vendor, model, Serial#
    f1.write('  #Equipment {}\n'.format(equip_str(params['equipment']) ) )
                
    # COMMENT LINES
    f1.write('  #Comment "Time base = {}"\n'.format(station['time_base']))
    f1.write('  #Comment "{}"\n'.format(clock_correction_str(station['clock_correction_linear'])))
    f1.write('  #Comment "Location is based on: {}"\n'.format(
                station['location_codes']['00']['loc_type']))
    if station['comment_list']:
        for line in station['comment_list']:
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
        f1.write('    ' + loc_str(name,loc,pos)+'\n')
        f1.write('    #' + loc_str(name,loc,pos,enhanced=True)+'\n')
    f1.write('  end_location\n\n')

    # DATALOGGER LINES
    f1.write('  #begin_datalogger\n')
    f1.write('  #  LOGGER {}\n'.format(equip_str(params['datalogger'])))
    f1.write('  #end_datalogger\n\n')
    
    # SENSOR LINES
    sensor_dict=collect_channel_params(params['channels'],'sensor')
    #print(sensor_dict)
    # Print LINES
    f1.write('  begin_sensor\n')
    for key in sorted(sensor_dict):
        name='SENS{}'.format(key)
        f1.write('    '  + sensor_str(name,sensor_dict[key]['specs'])+'\n')
        f1.write('    #' + sensor_str(name,sensor_dict[key]['specs'],enhanced=True)+'\n')
        for ch_key in sensor_dict[key]['channels']:
            channel_dict[ch_key]['sensor_code']=name
    f1.write('  end_sensor\n\n')
        
    # PREAMPLIFIER LINES
    # COLLECT PREAMPLIFIER DEFINITIONS
    preamp_dict=collect_channel_params(params['channels'],'ana_filter')
    # Print LINES
    f1.write('  begin_ana_filter\n')
    for key in sorted(preamp_dict):
        name='AFILT{}'.format(key)
        f1.write('    '  + response_str(name,preamp_dict[key]['specs'])+'\n')
        f1.write('    #' + response_str(name,preamp_dict[key]['specs'],enhanced=True)+'\n')
        for ch_key in preamp_dict[key]['channels']:
            channel_dict[ch_key]['ana_filter_code']=name
    f1.write('  end_ana_filter\n\n')

    # DIGITIZER LINES 
    f1.write('  begin_digitizer\n')
    name='DIGI'
    f1.write('    '  + response_str(name,params['digitizer'])+'\n')
    f1.write('    #' + response_str(name,params['digitizer'],enhanced=True)+'\n')
    f1.write('  end_digitizer\n\n')
    for key in channel_dict:
            channel_dict[key]['digitizer_code']='DIGI'
            
    # DECIMATION LINES 
    # Put sample rate into DBIRD filename if necessary
    params['digital_filter']['DBIRD_file']=params['digital_filter']['DBIRD_file'].replace(
                    '{sample_rate}','{:g}'.format(sample_rate))
    f1.write('  begin_decimation\n')
    name='DECIM'
    f1.write('    '  + response_str(name,params['digital_filter'])+'\n')
    f1.write('    #' + response_str(name,params['digital_filter'],enhanced=True)+'\n')
    f1.write('  end_decimation\n\n')
    for key in channel_dict:
            channel_dict[key]['dig_filter_code']=name
            
    # CHANNEL LINES 
    # print(channel_dict)
    f1.write('  begin_channel\n')
    for key,val in sorted(channel_dict.items()):
        ch_code=modify_SEED_band_code(key.split(':')[0],sample_rate)
        f1.write('    {} {} {} {} {} {} CG STEIM1 {} {} {}\n'.format(
                    val['loc_code'],
                    key.split(':')[0],
                    val['sensor_code'],
                    val['ana_filter_code'],
                    val['digitizer_code'],
                    val['dig_filter_code'],
                    station['start_date'],
                    station['end_date'],
                    'NET1'
                    )
                )
    f1.write('  end_channel\n\n')
  
    # AND SO ON...
    f1.write('end_station\n')
    #f1.close()
    return

########################################  
def clock_correction_str(info):
    str = 'Linear clock correction using {} as reference: Start sync (reference,instrument)=({},{}); End sync =({},{})'.format(\
                info['reference'],
                info['start_sync_reference'], 
                info['start_sync_instrument'],
                info['end_sync_reference'],
                info['end_sync_instrument'])
    return str

########################################  
def orig_org_str(orig_org):
    str='originating_organization "{}" "{}" "{}" "{}"'.format(\
          none_sub(orig_org['full_name']),
          none_sub(orig_org['email']),
          none_sub(orig_org['website']),
          none_sub(orig_org['phone_number']))
    return str

########################################  
def network_str(network):
    str='NET1 "{}" "{}" "{}" {} {} "{}"'.format(\
                none_sub(network['code']),
                none_sub(network['name']),
                none_sub(network['email']),
                network['start_date'],
                network['end_date'],
                none_sub(network['telephone'])
                )
    return str
    
########################################  
def station_str(station,enhanced=False):
    pos=station['location_codes']['00']
    if not enhanced:
        str='{} {} {} {} {} {} "{}"'.format(\
                station['name'],
                station['start_date'],
                station['end_date'],
                pos['latitude'],
                pos['longitude'],
                pos['elevation'],
                none_sub(station.get('site','')))
    else:
        lat=float(pos['latitude'])
        m_per_degree_lat=1852*60
        m_per_degree_lon=m_per_degree_lat*m.cos(lat*m.pi/180)
        str='{} {} {} ({} {:.6f}) ({} {:.6f}) ({} {}) "{}"'.format(\
                station['name'],
                station['start_date'],
                station['end_date'],
                pos['latitude'],
                float(pos['lat_uncert_m'])/m_per_degree_lat,
                pos['longitude'],
                float(pos['lon_uncert_m'])/m_per_degree_lon,
                pos['elevation'],
                pos['elev_uncert_m'],
                none_sub(station.get('site','')))
    
    return str
    
########################################  
def loc_str(name,loc,pos,enhanced=False):
    if not enhanced:
        str = '{} "{}" {} {}  {} "{}" "{}"'.format(\
            name,
            none_sub(loc),
            pos['latitude'],
            pos['longitude'],
            pos['elevation'],
            none_sub(pos['vault']),
            none_sub(pos['geology'])
            )
    else:
        lat=float(pos['latitude'])
        m_per_degree_lat=1852*60
        m_per_degree_lon=m_per_degree_lat*m.cos(lat*m.pi/180)
        str = '{} "{}" ({} {:.6f}) ({} {:.6f}) ({} {}) "{}" "{}"'.format(\
            name,
            none_sub(loc),
            pos['latitude'],
            float(pos['lat_uncert_m'])/m_per_degree_lat,
            pos['longitude'],
            float(pos['lon_uncert_m'])/m_per_degree_lon,
            pos['elevation'],
            pos['elev_uncert_m'],
            none_sub(pos['vault']),
            none_sub(pos['geology'])
            )
    
    return str
    
########################################  
def sensor_str(name,info,enhanced=False):
    str='{} {} {}'.format(
                response_str(name,info,enhanced),
                info['azimuth'],
                info['dip']
                )
    return str
########################################  
def response_str(name,info,enhanced=False):
    if not enhanced:
        str='{} "{}" "{}" "{}"'.format(
                name,
                none_sub(info['description']),
                none_sub(info['serial_number']),
                none_sub(info['DBIRD_file']))
    else:
        str='{} {} "{}"'.format(
                name,
                equip_str(info),
                none_sub(info['DBIRD_file']))
    return str
########################################  
def modify_SEED_band_code(input,sample_rate):
    """ Returns the SEED channel code after modifying the band code to match
     the sample_rate band code """
    #print(sample_rate)
    if len(input) != 3:
        print('SEED band code must have 3 characters!')
        sys.exit(0)
    band_code=input[0]
    if band_code in 'BHCFMLURPT':
        if sample_rate >=1000:
            bc= 'F'
        elif sample_rate >= 250:
            bc=  'C'
        elif sample_rate >= 80:
            bc=  'H'
        elif sample_rate >= 10:
            bc=  'B'
        elif sample_rate > 1:
            bc=  'M'
        elif sample_rate > 0.5:
            bc=  'L'
        elif sample_rate >= 0.001:
            bc=  'U'
        elif sample_rate >= 0.0001:
            bc=  'R'
        elif sample_rate >= 0.00001:
            bc=  'P'
        elif sample_rate >= 0.000001:
            bc=  'T'
        else:
            bc=  'Q'
    elif band_code in 'SEDG':
        if sample_rate >=1000:
            bc=  'G'
        elif sample_rate >= 250:
            bc=  'D'
        elif sample_rate >= 80:
            bc=  'E'
        elif sample_rate >= 10:
            bc=  'S'
        else:
            print('Output sampling rate too low for short-period data!')
            sys.exit(1)
    else:
        print('Unaccepted band code on input: "{}"'.format(input))
        sys.exit(1)
    return bc+input[1:]

########################################  
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
def equip_str(equip_dict):
    """Make a DBIRD-compatible string from an EquipmentType dictionary 
    (keys=type,description, vendor, model, serial_number)"""
    #print(equip_dict)
    str='"{}" "{}" "{}" "{}" "{}" "{}"'.format(
                none_sub(equip_dict['type']),
                none_sub(equip_dict['description']),
                none_sub(equip_dict['manufacturer']),
                none_sub(equip_dict['vendor']),
                none_sub(equip_dict['model']),
                none_sub(equip_dict['serial_number'])
            )
    return str

########################################### 
def none_sub(str):
    # return an empty string if str is empty (instead of "None")
    if not str:
        return ""
    return str
    
########################################### 
def read_param_files(network_file,instrument_file,campaign_file):
    """READ NETWORK AND INSTRUMENT FILES"""
    with open(network_file,'r') as f:
        facility_network=yaml.load(f)['network']
    with open(instrument_file,'r') as f:
        instruments=yaml.load(f)['instrumentation']
    with open(campaign_file,'r') as f:
        campaign=yaml.load(f)['campaign']
        
    return facility_network,instruments,campaign
  
########################################### 
def prettyprint_station(station,name):
    """Pretty-print one station"""
    print('='*80)
    print('Station {}:'.format(name))
    pp=pprint.PrettyPrinter(width=131, compact=True)
    pp.pprint(station)
    print('')
  
########################################### 
def find_instrument(name,station,instrumentation):
    """ Find instrument corresponding to one specified in station """
    model=station['instrument']['model']
    serial_number  =station['instrument']['serial_number']
    instruments=instrumentation['instruments']
#     pp=pprint.PrettyPrinter(width=131, compact=True)
#     pp.pprint(instruments)
    # Allow Serial Number to match wildcard
    generic_str='generic'
    if serial_number in instruments[model] :
        instrument=copy.deepcopy(instruments[model][serial_number])
    elif generic_str in instruments[model]:
        instrument=copy.deepcopy(instruments[model][generic_str])
    else:
        print('Instrument model "{}" has no serial number {} and no generic definition'.format(\
                model, serial_number))
        return

    instrument['equipment']['serial_number']=serial_number
    return instrument


#############################################################################
if __name__ == '__main__':
    sys.exit(main())

