import yaml
import pprint
import sys
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
        if not instrument:
            continue
        station['instrument']['parameters']=instrument
        station['instrument']['facility']=instruments['facility']
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
    f1.write('begin_station\n')
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
    f1.write('  Contact: {}\n'.format(orig_org['email']))
    f1.write('  Owner: {}\n'.format(orig_org['full_name']))
    # EQUIPMENT LINE: type, description, manufacurer, vendor, model, Serial#
    f1.write('  #Equipment "{}" "{}" "{}" "{}" "{}" "{}"\n'.format(
                
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
    
    f1.write('  begin_location\n')
    i=0
    for loc,pos in station['location_codes'].items():
        i=i+1
        name='LOC'+'{:d}'.format(i)
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
    f1.write('  end_location\n')
  
    # AND SO ON...
    f1.write('end_station\n')
    #f1.close()
    return
  
    
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
    """ Find instrument corresponding one listed in station """
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
    return instruments['models'][inst_name][inst_SN]


#############################################################################
if __name__ == '__main__':
    sys.exit(main())
