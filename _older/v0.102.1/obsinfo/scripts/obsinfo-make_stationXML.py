#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List contents of an information file.

Example
=======

obsinfo-list MYCAMPAIGN.campaign.yaml

"""
ffrom argparse import ArgumentParser

from obsinfo.core import validate

DEFAULT_INFO_FILE='../examples/Information_Files/campaigns/MYCAMPAIGN/MYCAMPAIGN.INSU-IPGP.network.yaml'

def _somethings:
    """
    Description
    """
    return (days, hours, minutes, seconds)




def main(argv=None):
    parser = ArgumentParser(
        prog='obspy-sds-report', description=__doc__,
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument(
        '-r', '--sds-root', dest='sds_root', required=True,
        help='Root folder of SDS archive.')
    parser.add_argument(
        '-o', '--output', dest='output', required=True,
        help='Full path (absolute or relative) of output files, without '
             'suffix (e.g. ``/tmp/sds_report``).')
    parser.add_argument(
        '-u', '--update', dest='update', default=False, action="store_true",
        help='Only update latency information, reuse previously computed list '
             'of streams to check and data percentage and gap count. Many '
             'other options e.g. regarding stream selection (``--id``, '
             ' ``--location``, ..) and time span of data quality checks '
             '(``--check-quality-days``) will be without effect if this '
             'option is specified. Only updating latency is significantly '
             'faster than a full analysis run, a normal use case is to do a '
             'full run once or twice per day and update latency every 5 or '
             'ten minutes. An exception is raised if an update is specified '
             'but the necessary file is not yet present.')
    parser.add_argument(
        '-l', '--location', dest='locations', action="append",
        help='Location codes to look for (e.g. ``""`` for empty location code '
             'or ``"00"``). This option can be provided multiple times and '
             'must be specified at least once for a full run (i.e. without '
             '``--update`` option). While network/station combinations are '
             'automatically discovered, only streams whose location codes are '
             'provided here will be discovered and taken into account and '
             'ultimately displayed.')
    parser.add_argument(
        '-c', '--channel', dest='channels', action="append",
        help='Channel codes to look for (e.g. specified three times with '
             '``HHZ``, ``EHZ`` and ``ELZ`` to cover all stations that serve '
             'a broad-band, short-period or low gain vertical channel). '
             'This option can be provided multiple times and must be '
             'specified at least once for a full run (i.e. without '
             '``--update`` option). Only one stream per '
             'network/station/location combination will be displayed, '
             'selected by the lowest latency.')
    parser.add_argument(
        '-i', '--id', dest='ids', action="append", default=[],
        help='SEED IDs of streams that should be included in addition to the '
             'autodiscovery of streams controlled by ``--location`` and '
             '``--channel`` options (e.g. ``IU.ANMO..LHZ``). '
             'This option can be provided multiple times.')
    parser.add_argument(
        '--skip', dest='skip', action="append", default=[],
        help='Networks or stations that should be skipped (e.g. ``IU`` or '
             '``IU.ANMO``). This option can be provided multiple times.')
    parser.add_argument(
        '-f', '--format', default="MSEED", choices=ENTRY_POINTS['waveform'],
        help='Waveform format of SDS archive. Should be "MSEED" in most '
             'cases. Use ``None`` or empty string for format autodection '
             '(slower and should not be necessary in most all cases). '
             'Warning: formats that do not support ``headonly`` '
             'option in ``read()`` operation will be significantly slower).')
    parser.add_argument(
        '--check-backwards-days', dest='check_back_days', default=30,
        type=int, help='Check for latency backwards for this many days.')
    parser.add_argument(
        '--check-quality-days', dest='check_quality_days', default=7,
        type=int, help='Calculate and plot data availability and number of '
                       'gaps for a period of this many days.')
    parser.add_argument(
        '--latency-warn', dest='latency_warn', default=3600,
        type=float, help='Latency warning threshold in seconds.')
    parser.add_argument(
        '--latency-warn-color', dest='latency_warn_color', default="#FFFF33",
        help='Latency warning threshold color (valid HTML color string).')
    parser.add_argument(
        '--latency-error', dest='latency_error', default=24 * 3600,
        type=float, help='Latency error threshold in seconds.')
    parser.add_argument(
        '--latency-error-color', dest='latency_error_color', default="#E41A1C",
        help='Latency error threshold color (valid HTML color string).')
    parser.add_argument(
        '--percentage-warn', dest='percentage_warn', default=99.5, type=float,
        help='Data availability percentage warning threshold (``0`` to '
             '``100``).')
    parser.add_argument(
        '--gaps-warn', dest='gaps_warn', default=20, type=int,
        help='Gap/overlap number warning threshold.')
    parser.add_argument(
        '--data-quality-warn-color', dest='data_quality_warn_color',
        default="#377EB8",
        help='Data quality (percentage/gap count) warning color '
             '(valid HTML color string).')
    parser.add_argument(
        '--outdated-color', dest='outdated_color', default="#808080",
        help='Color for streams that have no data in check range '
             '(valid HTML color string).')
    parser.add_argument(
        '--ok-color', dest='ok_color', default="#4DAF4A",
        help='Color for streams that pass all checks (valid HTML color '
             'string).')
    parser.add_argument(
        '--background-color', dest='background_color', default="#999999",
        help='Color for background of page (valid HTML color string).')
    parser.add_argument(
        '-V', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args(argv)

    now = UTCDateTime()
    stop_time = now - args.check_back_days * 24 * 3600
    client = Client(args.sds_root)
    dtype_streamfile = np.dtype("U10, U30, U10, U10, f8, f8, i8")
    availability_check_endtime = now - 3600
    availability_check_starttime = (
        availability_check_endtime - (args.check_quality_days * 24 * 3600))
    streams_file = args.output + ".txt"
    html_file = args.output + ".html"
    scan_file = args.output + ".png"
    if args.format.upper() == "NONE" or args.format == "":
        args.format = None

    # check whether to set up list of streams to check or use existing list
    # update list of streams once per day at nighttime
    if args.update:
        if not os.path.isfile(streams_file):
            msg = ("Update flag specified, but no output of previous full run "
                   "was present in the expected location (as determined by "
                   "``--output`` flag: {})").format(streams_file)
            raise IOError(msg)
        # use existing list of streams and availability information, just
        # update latency
        nslc = np.loadtxt(streams_file, delimiter=",", dtype=dtype_streamfile)
    else:
        if not args.locations or not args.channels:
            msg = ("At least one location code ``--location`` and at least "
                   "one channel code ``--channel`` must be specified.")
            raise ObsPyException(msg)
        nsl = set()
        # get all network/station combinations in SDS archive
        for net, sta in client.get_all_stations():
            if net in args.skip or ".".join((net, sta)) in args.skip:
                continue
            # for all combinations of user specified location and channel codes
            # check if data is in SDS archive
            for loc in args.locations:
                for cha in args.channels:
                    if client.has_data(net, sta, loc, cha):
                        # for now omit channel information, we only include the
                        # channel with lowest latency later on
                        nsl.add((net, sta, loc))
                        break
        nsl = sorted(nsl)
        nslc = []
        # determine which channel to check for each network/station/location
        # combination
        for net, sta, loc in nsl:
            latency = []
            # check latency of all channels that should be checked
            for cha in args.channels:
                latency_ = client.get_latency(net, sta, loc, cha,
                                              stop_time=stop_time)
                latency.append(latency_ or np.inf)
            # only include the channel with lowest latency in our stream list
            cha = args.channels[np.argmin(latency)]
            latency = np.min(latency)
            nslc.append((net, sta, loc, cha, latency))
        for id in args.ids:
            net, sta, loc, cha = id.split(".")
            latency = client.get_latency(net, sta, loc, cha,
                                         stop_time=stop_time)
            latency = latency or np.inf
            nslc.append((net, sta, loc, cha, latency))
        nslc_ = []
        # request and assemble availability information.
        # this takes pretty long (on network/slow file systems),
        # so we only do it during a full run here, not during update
        for net, sta, loc, cha, latency in nslc:
            percentage, gap_count = client.get_availability_percentage(
                net, sta, loc, cha, availability_check_starttime,
                availability_check_endtime)
            nslc_.append((net, sta, loc, cha, latency, percentage, gap_count))
        nslc = nslc_
        # write stream list and availability information to file
        nslc = np.array(sorted(nslc), dtype=dtype_streamfile)
        np.savetxt(streams_file, nslc, delimiter=",",
                   fmt=["%s", "%s", "%s", "%s", "%f", "%f", "%d"])
        # generate obspy-scan image
        files = []
        seed_ids = set()
        for nslc_ in nslc:
            net, sta, loc, cha, latency, _, _ = nslc_
            if np.isinf(latency) or latency > args.check_back_days * 24 * 3600:
                continue
            seed_ids.add(".".join((net, sta, loc, cha)))
            files += client._get_filenames(
                net, sta, loc, cha, availability_check_starttime,
                availability_check_endtime)
        scan(files, format=args.format, starttime=availability_check_starttime,
             endtime=availability_check_endtime, plot=scan_file, verbose=False,
             recursive=True, ignore_links=False, seed_ids=seed_ids,
             print_gaps=False)

    # request and assemble current latency information
    data = []
    for net, sta, loc, cha, latency, percentage, gap_count in nslc:
        if args.update:
            latency = client.get_latency(net, sta, loc, cha,
                                         stop_time=stop_time)
            latency = latency or np.inf
        data.append((net, sta, loc, cha, latency, percentage, gap_count))

    # separate out the long dead streams
    data_normal = []
    data_outdated = []
    for data_ in data:
        latency = data_[4]
        if np.isinf(latency) or latency > args.check_back_days * 24 * 3600:
            data_outdated.append(data_)
        else:
            data_normal.append(data_)

    # write html output to file
    html = _format_html(args, data_normal, data_outdated)
    with open(html_file, "wt") as fh:
        fh.write(html)


if __name__ == "__main__":
    main()

#! env python3
import obsinfo.misc.validate as validate


validate.validate(info_file)