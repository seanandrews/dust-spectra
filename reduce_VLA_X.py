import os
import sys
import numpy as np
from casatools import msmetadata
from scipy.interpolate import interp1d
sys.path.append('.')
from targets_dict import targ as td
execfile('reduction_tools.py')


# I/O paths
pipe_dir = '/data/sandrews/VLA_LP/data/VLA/'
proc_dir = '/d4/asha1/dust-spec/DR/VLA/'


# fixed quantities: observing band, SPWs, flux calibrator, channel binning
band = 'X'
bspw = '0~31'
calname = '3C138'
chbin = 64


# execution identifiers
EB = ['03_1', '11_1', '12_1', '02_1', '10_1', '01_1', '07_1', '08_1',
      '05_1', '14_1', '04_1', '06_1', '09_1', '13_1', '03_2', '02_2', 
      '14_2', '07_2', '12_2', '18_1', '15_1', '16_1', '16_2', '17_1']
EB = [band + item + '/' for item in EB]


# MS filenames for pipeline-processed datasets
msfile = ['sb48829784.eb48927155.60821.833398229166_targets_cont',
          'sb48833475.eb48936464.60826.821180555555_targets_cont',
          'sb48833859.eb48936892.60827.83169114584_targets_cont',
          'sb48829373.eb48940822.60829.83844501157_targets_cont_data_column',
          'sb48832414.eb48949534.60832.799824340276_targets_cont',
          'sb48828973.eb48949560.60833.81233049768_targets_cont_data_column',
          'sb48831257.eb48949582.60834.835955601855_targets_cont',
          'sb48831626.eb48952297.60836.767009675925_targets_cont',
          'sb48830471.eb48957189.60839.76233471065_targets_cont',
          'sb48834841.eb48957581.60839.86754622685_targets_cont',
          'sb48830226.eb48958259.60840.82695858796_targets_cont',
          'sb48830672.eb48958277.60841.62774427084_targets_cont',
          'sb48832014.eb48958281.60841.768722187495_targets_cont',
          'sb48834063.eb48964813.60845.536979282406_targets_cont',
          'sb48829784.eb48966133.60847.80787053241_targets_cont',
          'sb48829182.eb48967391.60848.585893877316_targets_cont',
          'sb48834539.eb48967593.60850.55250611111_targets_cont',
          'sb48831068.eb48970526.60853.52720679398_targets_cont',
          'sb48833655.eb49034255.60880.45885700232_targets_cont',
          'sb49058849.eb49071093.60890.694885150464_targets_cont',
          'sb49055824.eb49079253.60892.388710949075_targets_cont',
          'sb49056557.eb49083214.60892.678362280094_targets_cont',
          'sb49056557.eb49122442.60896.6622600463_targets_cont',
          'sb49057019.eb49123036.60897.59742288194_targets_cont']
msfile = ['25A-330.' + item + '.ms' for item in msfile]


# additional RFI flagging ranges (determined by direct inspection)
rfi_flags = '0:0~8.010GHz,10:9.325~12GHz,11:9.457~9.481GHz,' + \
            '28:11.570~11.585GHz;11.606~11.626GHz,' + \
            '29:11.68~11.73GHz,31:11.96~15GHz'

time_flags = ['2025/05/26/21:17:16~2025/05/26/21:17:18',
              '2025/05/31/20:06:07~2025/05/31/20:06:10,' + \
              '2025/05/31/20:15:16~2025/05/31/20:15:35',
              '2025/06/01/21:03:28~2025/06/01/21:03:30,' + \
              '2025/06/01/21:28:06~2025/06/01/21:28:10',
              None,
              '2025/06/06/19:44:52~2025/06/06/19:44:53,' + \
              '2025/06/06/20:09:28~2025/06/06/20:09:29,' + \
              '2025/06/06/20:32:43~2025/06/06/20:32:45,' + \
              '2025/06/06/20:51:40~2025/06/06/20:51:41,' + \
              '2025/06/06/21:05:27~2025/06/06/21:05:29,' + \
              '2025/06/06/21:23:07~2025/06/06/21:23:08',
              None,
              '2025/06/08/20:27:24~2025/06/08/20:28:41,' + \
              '2025/06/08/20:46:22~2025/06/08/20:46:26,' + \
              '2025/06/08/21:01:25~2025/06/08/21:01:27,' + \
              '2025/06/08/22:16:20~2025/06/08/22:16:25',
              '2025/06/10/18:58:52~2025/06/10/18:58:53,' + \
              '2025/06/10/19:12:40~2025/06/10/19:12:42,' + \
              '2025/06/10/19:31:37~2025/06/10/19:31:38,' + \
              '2025/06/10/20:12:34~2025/06/10/20:12:35,' + \
              '2025/06/10/20:26:21~2025/06/10/20:26:25',
              None,
              None,
              '2025/06/14/21:08:57~2025/06/14/21:09:00',
              '2025/06/15/16:00:18~2025/06/15/16:00:22,' + \
              '2025/06/15/16:19:15~2025/06/15/16:19:20',
              '2025/06/15/18:42:25~2025/06/15/18:42:27,' + \
              '2025/06/15/19:01:22~2025/06/15/19:01:28,' + \
              '2025/06/15/19:15:10~2025/06/15/19:15:11,' + \
              '2025/06/15/19:57:25~2025/06/15/19:57:26,' + \
              '2025/06/15/20:29:05~2025/06/15/20:30:26',
              '2025/06/19/13:26:37~2025/06/19/13:26:38,' + \
              '2025/06/19/14:14:27~2025/06/19/14:14:30',
              '2025/06/21/19:56:19~2025/06/21/19:56:20',
              '2025/06/22/16:15:40~2025/06/22/16:15:42',
              '2025/06/24/14:50:15~2025/06/24/14:50:18',
              '2025/06/27/13:12:18~2025/06/27/13:12:20',
              '2025/07/24/12:29:55~2025/07/24/12:29:56,' + \
              '2025/07/24/13:12:58~2025/07/24/13:13:00',
              '2025/08/03/17:05:35~2025/08/03/17:05:40,' + \
              '2025/08/03/17:47:50~2025/08/03/17:47:55,' + \
              '2025/08/03/18:02:45~2025/08/03/18:02:48,' + \
              '2025/08/03/18:12:25~2025/08/03/18:12:27,' + \
              '2025/08/03/18:22:12~2025/08/03/18:22:15',
              '2025/08/05/09:48:30~2025/08/05/09:48:33,' + \
              '2025/08/05/10:29:28~2025/08/05/10:29:30,' + \
              '2025/08/05/11:37:06~2025/08/05/11:38:27',
              '2025/08/05/16:40:30~2025/08/05/16:40:32,' + \
              '2025/08/05/16:59:26~2025/08/05/16:59:30,' + \
              '2025/08/05/17:48:10~2025/08/05/17:49:30,' + \
              '2025/08/05/18:31:42~2025/08/05/18:31:44',
              '2025/08/09/17:10:10~2025/08/09/17:10:15',
              '2025/08/10/16:12:35~2025/08/10/16:14:00']
              


# get the list of VLA labels from the target dictionary
_ = [(k, td[k]['vlabel']) for k in td.keys()]
src, vlbls = map(list, zip(*_))



# Loop over batch of MS files
for i in range(len(EB)):
    # tracking
    print(f"\nReducing dataset {i:02d} for execution {EB[i]}...")

    # get a list of the targets
    msmd = msmetadata()
    msmd.open(pipe_dir + msfile[i])
    fieldnames = msmd.fieldnames()
    msmd.close()

    # parse into target names (for output) and field names (for access)
    tfields = [item for item in fieldnames if item in vlbls]
    ix = [item for item, x in enumerate(vlbls) if x in tfields]
    targ_names = [src[item] for item in ix]
    targ_fields = [vlbls[item] for item in ix]
    field_str = ', '.join(str(j) for j in targ_fields)
    print('\n' + field_str)

    # check if the MS file has a corrected data column
    has_corr = has_corrected_column(pipe_dir + msfile[i])
    use_col = 'corrected' if has_corr else 'data'

    # temporary copy of the pipeline-processed MS for the target fields
    if not os.path.exists(proc_dir + EB[i]):
        os.system('mkdir ' + proc_dir + EB[i])
    init_MS = proc_dir + EB[i] + 'pipeline.init.ms'
    os.system('rm -rf ' + init_MS + '*')
    mstransform(vis=pipe_dir + msfile[i], outputvis=init_MS, 
                datacolumn=use_col, field=field_str)

    # standard RFI flag set
    flagdata(vis=init_MS, mode='manual', spw=rfi_flags, flagbackup=False)

    # execution-specific time flagging
    if time_flags[i] is not None:
        flagdata(vis=init_MS, mode='manual', spw='', timerange=time_flags[i],
                 flagbackup=False)

    # individualized flagging
    if i == 0:
        tt = '2025/05/26/21:45:44~2025/05/26/21:46:02'
        flagdata(vis=init_MS, mode='manual', spw='1', 
                 timerange=tt, flagbackup=False)
        tt = '2025/05/26/20:25:00~2025/05/26/20:30:28,' + \
             '2025/05/26/21:04:00~2025/05/26/21:12:16,' + \
             '2025/05/26/21:14:45~2025/05/26/21:16:00,' + \
             '2025/05/26/21:18:10~2025/05/26/22:24:00'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/05/26/22:20:18~2025/05/26/22:20:24'
        flagdata(vis=init_MS, mode='manual', spw='23',
                 timerange=tt, flagbackup=False)
        tt = '2025/05/26/20:42:08~2025/05/26/20:42:24'
        flagdata(vis=init_MS, mode='manual', spw='23,24,25,27,28,29',
                 timerange=tt, flagbackup=False)
        tt = '2025/05/26/22:01:04~2025/05/26/22:01:18,' + \
             '2025/05/26/21:58:24~2025/05/26/21:58:42'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 1:
        tt = '2025/05/31/20:08:30~2025/05/31/20:08:52,' + \
             '2025/05/31/20:11:23~2025/05/31/20:13:15,' + \
             '2025/05/31/20:42:42~2025/05/31/20:42:51,' + \
             '2025/05/31/20:42:57~2025/05/31/20:43:00,' + \
             '2025/05/31/21:51:00~2025/05/31/21:54:00'
        flagdata(vis=init_MS, mode='manual', spw='11', 
                 timerange=tt, flagbackup=False)
        tt = '2025/05/31/20:01:41~2025/05/31/20:01:45,' + \
             '2025/05/31/20:02:15~2025/05/31/20:02:26,' + \
             '2025/05/31/21:07:33~2025/05/31/21:07:50,' + \
             '2025/05/31/21:48:18~2025/05/31/21:48:27'
        flagdata(vis=init_MS, mode='manual', spw='22~23,31',
                 timerange=tt, flagbackup=False)
        tt = '2025/05/31/20:12:57~2025/05/31/20:13:13'
        flagdata(vis=init_MS, mode='manual', spw='24,25',
                 timerange=tt, flagbackup=False)
        tt = '2025/05/31/21:42:20~2025/05/31/21:42:25'
        flagdata(vis=init_MS, mode='manual', spw='26',
                 timerange=tt, flagbackup=False)
        tt = '2025/05/31/20:01:37~2025/05/31/20:01:44,' + \
             '2025/05/31/20:02:13~2025/05/31/20:02:26'
        flagdata(vis=init_MS, mode='manual', spw='27', 
                 timerange=tt, flagbackup=False)
        tt = '2025/05/31/21:29:12~2025/05/31/21:29:28'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 2:
        tt = '2025/06/01/20:00:00~2025/06/01/20:21:20,' + \
             '2025/06/01/20:27:04~2025/06/01/21:03:30,' + \
             '2025/06/01/21:18:00~2025/06/01/21:24:11' 
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/01/21:06:15~2025/06/01/21:06:30,' + \
             '2025/06/01/21:38:54~2025/06/01/21:39:05'
        flagdata(vis=init_MS, mode='manual', spw='28,29',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/01/21:24:41~2025/06/01/21:25:10'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 3:
        tt = '2025/06/03/20:57:10~2025/06/03/20:59:43'
        flagdata(vis=init_MS, mode='manual', spw='1,2,25,26,27,28,29,30,31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/03/20:44:12~2025/06/03/21:03:30,' + \
             '2025/06/03/22:20:00~2025/06/03/22:30:00'
        flagdata(vis=init_MS, mode='manual', spw='9~14',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/03/20:32:00~2025/06/03/20:41:00,' + \
             '2025/06/03/20:43:54~2025/06/03/20:43:57,' + \
             '2025/06/03/21:08:40~2025/06/03/21:10:30,' + \
             '2025/06/03/21:37:28~2025/06/03/21:38:00,' + \
             '2025/06/03/21:40:24~2025/06/03/21:41:12'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/03/21:04:52~2025/06/03/21:08:15,' + \
             '2025/06/03/20:36:28~2025/06/03/20:37:10,' + \
             '2025/06/03/20:43:54~2025/06/03/20:43:57'
        flagdata(vis=init_MS, mode='manual', spw='13',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/03/20:44:12~2025/06/03/21:03:30'
        flagdata(vis=init_MS, mode='manual', spw='15,16',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/03/20:39:22~2025/06/03/20:39:25,' + \
             '2025/06/03/21:21:03~2025/06/03/21:21:25'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 4:
        tt = '2025/06/06/19:44:40~2025/06/06/19:44:50'
        flagdata(vis=init_MS, mode='manual', spw='22~29,31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/06/19:47:04~2025/06/06/19:47:27'
        flagdata(vis=init_MS, mode='manual', spw='23~25,27,28,29,31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/06/19:49:34~2025/06/06/19:49:54'
        flagdata(vis=init_MS, mode='manual', spw='24,25,27,28,29,31',
                 timerange=tt, flagbackup=False)
    if i == 5:
        tt = '2025/06/07/19:48:50~2025/06/07/19:49:38'
        flagdata(vis=init_MS, mode='manual', spw='4~7,10~14',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/07/19:57:20~2025/06/07/19:58:20'
        flagdata(vis=init_MS, mode='manual', spw='9~14',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/07/19:52:10~2025/06/07/19:52:52,' + \
             '2025/06/07/20:01:57~2025/06/07/20:02:10'
        flagdata(vis=init_MS, mode='manual', spw='10~14',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/07/19:45:41~2025/06/07/19:46:04,' + \
             '2025/06/07/21:07:27~2025/06/07/21:07:40'
        flagdata(vis=init_MS, mode='manual', spw='23~25,27~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/07/21:01:10~2025/06/07/21:01:12,' + \
             '2025/06/07/21:03:30~2025/06/07/21:03:50'
        flagdata(vis=init_MS, mode='manual', spw='30~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/07/19:57:06~2025/06/07/19:57:24,' + \
             '2025/06/07/20:00:09~2025/06/07/20:00:25'
        flagdata(vis=init_MS, mode='manual', spw='23,27,30,31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/07/19:48:10~2025/06/07/19:48:28'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 6:
        tt = '2025/06/08/20:34:34~2025/06/08/20:39:50,' + \
             '2025/06/08/20:51:00~2025/06/08/21:01:00,' + \
             '2025/06/08/21:24:00~2025/06/08/21:34:00'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/08/21:30:03~2025/06/08/21:30:10,' + \
             '2025/06/08/22:12:15~2025/06/08/22:12:30'
        flagdata(vis=init_MS, mode='manual', spw='23,27',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/08/20:53:38~2025/06/08/20:54:00'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 7:
        tt = '2025/06/10/20:23:40~2025/06/10/20:23:56'
        flagdata(vis=init_MS, mode='manual', spw='3',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/10/18:40:00~2025/06/10/18:41:20,' + \
             '2025/06/10/19:19:00~2025/06/10/19:23:00,' + \
             '2025/06/10/19:26:05~2025/06/10/19:26:13,' + \
             '2025/06/10/19:28:41~2025/06/10/19:29:16,' + \
             '2025/06/10/19:34:56~2025/06/10/19:35:18,' + \
             '2025/06/10/19:44:00~2025/06/10/19:54:00,' + \
             '2025/06/10/20:34:24~2025/06/10/20:35:40'
        flagdata(vis=init_MS, mode='manual', spw='9~15',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/10/19:03:30~2025/06/10/19:08:00,' + \
             '2025/06/10/19:12:00~2025/06/10/19:32:40,' + \
             '2025/06/10/19:35:22~2025/06/10/19:35:23,' + \
             '2025/06/10/19:35:36~2025/06/10/19:36:16,' + \
             '2025/06/10/19:54:40~2025/06/10/19:58:00,' + \
             '2025/06/10/19:59:40~2025/06/10/20:00:42,' + \
             '2025/06/10/20:01:34~2025/06/10/20:01:41,' + \
             '2025/06/10/20:27:40~2025/06/10/20:28:16,' + \
             '2025/06/10/20:28:34~2025/06/10/20:28:36,' + \
             '2025/06/10/20:33:30~2025/06/10/20:38:00'
        flagdata(vis=init_MS, mode='manual', spw='11~15',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/10/18:41:34~2025/06/10/18:41:45,' + \
             '2025/06/10/19:00:10~2025/06/10/19:02:10,' + \
             '2025/06/10/19:34:47~2025/06/10/19:36:20'
        flagdata(vis=init_MS, mode='manual', spw='12~13',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/10/18:40:00~2025/06/10/19:12:00,' + \
             '2025/06/10/19:38:58~2025/06/10/19:38:59'
        flagdata(vis=init_MS, mode='manual', spw='13~15',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/10/19:01:54~2025/06/10/19:02:08'
        flagdata(vis=init_MS, mode='manual', spw='',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/10/19:26:28~2025/06/10/19:26:50,' + \
             '2025/06/10/19:28:54~2025/06/10/19:29:22'
        flagdata(vis=init_MS, mode='manual', spw='23~25,27~29',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/10/20:42:40~2025/06/10/20:42:58,' + \
             '2025/06/10/20:45:07~2025/06/10/20:45:20'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 8:
        tt = '2025/06/13/18:32:00~2025/06/13/18:39:00'
        flagdata(vis=init_MS, mode='manual', spw='10~11',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/13/20:35:00~2025/06/13/20:39:00'
        flagdata(vis=init_MS, mode='manual', spw='10~14',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/13/19:12:00~2025/06/13/19:12:35' 
        flagdata(vis=init_MS, mode='manual', spw='23~25,27~29',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/13/20:00:56~2025/06/13/20:01:00'
        flagdata(vis=init_MS, mode='manual', spw='23,31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/13/20:23:40~2025/06/13/20:23:41'
        flagdata(vis=init_MS, mode='manual', spw='26',
                 timerange=tt, flagbackup=False)
    if i == 9:
        tt = '2025/06/13/21:04:00~2025/06/13/21:25:00'
        flagdata(vis=init_MS, mode='manual', spw='10~14',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/13/21:13:36~2025/06/13/21:14:00,' + \
             '2025/06/13/21:19:48~2025/06/13/21:20:04'
        flagdata(vis=init_MS, mode='manual', spw='18~20,22,24',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/13/22:17:38~2025/06/13/22:17:42'
        flagdata(vis=init_MS, mode='manual', spw='27~28',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/13/22:27:54~2025/06/13/22:28:10,' + \
             '2025/06/13/22:30:08~2025/06/13/22:30:28,' + \
             '2025/06/13/22:32:30~2025/06/13/22:32:36'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/13/21:49:40~2025/06/13/21:50:42,' + \
             '2025/06/13/21:55:30~2025/06/13/22:14:00,' + \
             '2025/06/13/22:21:00~2025/06/13/22:41:00'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
    if i == 10:
        tt = '2025/06/14/20:55:24~2025/06/14/20:55:44,' + \
             '2025/06/14/21:40:30~2025/06/14/21:40:42'
        flagdata(vis=init_MS, mode='manual', spw='23,27,30~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/14/21:29:00~2025/06/14/21:29:15'
        flagdata(vis=init_MS, mode='manual', spw='27~29',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/14/20:27:41~2025/06/14/20:28:00,' + \
             '2025/06/14/21:40:42~2025/06/14/21:41:04'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 11:
        tt = '2025/06/15/16:51:30~2025/06/15/16:52:00'
        flagdata(vis=init_MS, mode='manual', spw='13',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/15/15:41:14~2025/06/15/15:41:32,' + \
             '2025/06/15/16:31:55~2025/06/15/16:32:15,' + \
             '2025/06/15/16:34:15~2025/06/15/16:34:33,' + \
             '2025/06/15/16:36:35~2025/06/15/16:36:49,' + \
             '2025/06/15/16:41:24~2025/06/15/16:41:30,' + \
             '2025/06/15/16:43:40~2025/06/15/16:44:00'
        flagdata(vis=init_MS, mode='manual', spw='23~29',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/15/15:21:20~2025/06/15/15:21:36,' + \
             '2025/06/15/15:30:38~2025/06/15/15:31:00,' + \
             '2025/06/15/16:49:30~2025/06/15/16:49:35'
        flagdata(vis=init_MS, mode='manual', spw='27~31',
                 timerange=tt, flagbackup=False)
    if i == 12:
        tt = '2025/06/15/18:51:40~2025/06/15/18:54:00,' + \
             '2025/06/15/19:04:15~2025/06/15/19:06:20,' + \
             '2025/06/15/19:34:00~2025/06/15/19:52:40,' + \
             '2025/06/15/20:20:00~2025/06/15/20:45:00'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/15/19:02:08~2025/06/15/19:02:36,' + \
             '2025/06/15/19:04:30~2025/06/15/19:05:00'
        flagdata(vis=init_MS, mode='manual', spw='23~25,27~29',
                 timerange=tt, flagbackup=False)
    if i == 13:
        tt = '2025/06/19/13:29:45~2025/06/19/13:30:05,' + \
             '2025/06/19/13:32:03~2025/06/19/13:32:18,' + \
             '2025/06/19/14:44:26~2025/06/19/14:44:45,' + \
             '2025/06/19/14:49:32~2025/06/19/14:49:42'
        flagdata(vis=init_MS, mode='manual', spw='23~25,27~29,31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/19/13:20:16~2025/06/19/13:20:17,' + \
             '2025/06/19/14:42:04~2025/06/19/14:52:05'
        flagdata(vis=init_MS, mode='manual', spw='27~29',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/19/13:57:00~2025/06/19/13:57:15'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 14:
        tt = '2025/06/21/19:42:00~2025/06/21/19:49:25'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/21/21:38:45~2025/06/21/21:38:48'
        flagdata(vis=init_MS, mode='manual', spw='16~18',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/21/19:55:18~2025/06/21/19:55:24,' + \
             '2025/06/21/19:59:05~2025/06/21/19:59:15,' + \
             '2025/06/21/20:53:45~2025/06/21/20:54:03'
        flagdata(vis=init_MS, mode='manual', spw='23~25,27,30,31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/21/19:52:00~2025/06/21/19:52:20,' + \
             '2025/06/21/19:54:24~2025/06/21/19:54:52,' + \
             '2025/06/21/21:09:45~2025/06/21/21:09:55,' + \
             '2025/06/21/21:12:04~2025/06/21/21:12:25'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 15:
        tt = '2025/06/22/15:35:35~2025/06/22/15:36:00'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/22/16:12:35~2025/06/22/16:12:50'
        flagdata(vis=init_MS, mode='manual', spw='15',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/22/15:57:30~2025/06/22/15:57:33,' + \
             '2025/06/22/16:07:30~2025/06/22/16:07:33'
        flagdata(vis=init_MS, mode='manual', spw='16~22',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/22/15:40:20~2025/06/22/15:40:38'
        flagdata(vis=init_MS, mode='manual', spw='21~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/22/14:52:00~2025/06/22/14:52:15,' + \
             '2025/06/22/16:04:30~2025/06/22/16:04:56'
        flagdata(vis=init_MS, mode='manual', spw='23~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/22/15:57:30~2025/06/22/15:57:34,' + \
             '2025/06/22/16:07:31~2025/06/22/16:07:33'
        flagdata(vis=init_MS, mode='manual', spw='25~27,29~31',
                 timerange=tt, flagbackup=False)
    if i == 16:
        tt = '2025/06/24/13:31:00~2025/06/24/13:38:00,' + \
             '2025/06/24/14:22:30~2025/06/24/14:31:50,' + \
             '2025/06/24/15:12:45~2025/06/24/15:12:47'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/24/15:15:30~2025/06/24/15:24:00'
        flagdata(vis=init_MS, mode='manual', spw='11~16',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/24/15:16:43~2025/06/24/15:16:50'
        flagdata(vis=init_MS, mode='manual', spw='23',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/24/14:21:55~2025/06/24/14:22:00'
        flagdata(vis=init_MS, mode='manual', spw='24',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/24/13:48:10~2025/06/24/13:48:38,' + \
             '2025/06/24/14:11:32~2025/06/24/14:11:44,' + \
             '2025/06/24/15:16:15~2025/06/24/15:16:17'
        flagdata(vis=init_MS, mode='manual', spw='28~29',
                 timerange=tt, flagbackup=False)
    if i == 17:
        tt = '2025/06/27/12:55:55~2025/06/27/12:56:11'
        flagdata(vis=init_MS, mode='manual', spw='23~25,27~29',
                 timerange=tt, flagbackup=False)
        tt = '2025/06/27/14:21:12~2025/06/27/14:21:25,' + \
             '2025/06/27/14:16:11~2025/06/27/14:16:30'
        flagdata(vis=init_MS, mode='manual', spw='27~29',
                 timerange=tt, flagbackup=False)
    if i == 18:
        tt = '2025/07/24/12:09:04~2025/07/24/12:09:28'
        flagdata(vis=init_MS, mode='manual', spw='21~25',
                 timerange=tt, flagbackup=False)
        tt = '2025/07/24/11:17:19~2025/07/24/11:17:26,' + \
             '2025/07/24/12:01:00~2025/07/24/12:01:18,' + \
             '2025/07/24/13:20:20~2025/07/24/13:20:36,' + \
             '2025/07/24/13:22:46~2025/07/24/13:22:50'
        flagdata(vis=init_MS, mode='manual', spw='23~25,27~29',
                 timerange=tt, flagbackup=False)
        tt = '2025/07/24/13:18:39~2025/07/24/13:18:47'
        flagdata(vis=init_MS, mode='manual', spw='26',
                 timerange=tt, flagbackup=False)
        tt = '2025/07/24/12:03:33~2025/07/24/12:03:39,' + \
             '2025/07/24/12:23:36~2025/07/24/12:23:51'
        flagdata(vis=init_MS, mode='manual', spw='27',
                 timerange=tt, flagbackup=False)
        tt = '2025/07/24/11:17:21~2025/07/24/11:17:27'
        flagdata(vis=init_MS, mode='manual', spw='31',
                 timerange=tt, flagbackup=False)
    if i == 19:
        tt = '2025/08/03/17:05:30~2025/08/03/17:25:00'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/03/17:40:58~2025/08/03/17:41:12'
        flagdata(vis=init_MS, mode='manual', spw='23',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/03/17:20:12~2025/08/03/17:20:17'
        flagdata(vis=init_MS, mode='manual', spw='27',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/03/17:30:30~2025/08/03/17:31:00,' + \
             '2025/08/03/18:15:16~2025/08/03/18:15:26,' + \
             '2025/08/03/18:17:26~2025/08/03/18:17:44,' + \
             '2025/08/03/18:19:45~2025/08/03/18:19:56'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/03/17:13:30~2025/08/03/17:13:32,' + \
             '2025/08/03/17:20:10~2025/08/03/17:20:18,' + \
             '2025/08/03/17:41:00~2025/08/03/17:41:07'
        flagdata(vis=init_MS, mode='manual', spw='31',
                 timerange=tt, flagbackup=False)
    if i == 20:
        tt = '2025/08/05/09:49:34~2025/08/05/09:49:48,' + \
             '2025/08/05/11:08:13~2025/08/05/11:08:21,' + \
             '2025/08/05/11:10:40~2025/08/05/11:10:50'
        flagdata(vis=init_MS, mode='manual', spw='23~25,27~29',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/05/10:23:19~2025/08/05/10:23:30'
        flagdata(vis=init_MS, mode='manual', spw='28~29',
                 timerange=tt, flagbackup=False)
    if i == 21:
        tt = '2025/08/05/17:30:20~2025/08/05/17:32:40,' + \
             '2025/08/05/17:39:00~2025/08/05/18:26:00' 
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/05/16:43:55~2025/08/05/16:43:56' 
        flagdata(vis=init_MS, mode='manual', spw='13',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/05/16:44:34~2025/08/05/16:44:42,' + \
             '2025/08/05/16:37:48~2025/08/05/16:39:14,' + \
             '2025/08/05/17:06:00~2025/08/05/17:06:12,' + \
             '2025/08/05/17:11:27~2025/08/05/17:11:32,' + \
             '2025/08/05/17:55:44~2025/08/05/17:55:48'
        flagdata(vis=init_MS, mode='manual', spw='14',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/05/17:19:50~2025/08/05/17:21:12' 
        flagdata(vis=init_MS, mode='manual', spw='13~14',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/05/16:36:12~2025/08/05/16:36:28'
        flagdata(vis=init_MS, mode='manual', spw='21~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/05/17:22:45~2025/08/05/17:22:47,' + \
             '2025/08/05/17:30:46~2025/08/05/17:30:50'
        flagdata(vis=init_MS, mode='manual', spw='27',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/05/17:26:15~2025/08/05/17:26:30,' + \
             '2025/08/05/18:14:52~2025/08/05/18:15:09'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
    if i == 22:
        tt = '2025/08/09/17:27:28~2025/08/09/17:27:30,' + \
             '2025/08/09/17:29:43~2025/08/09/17:29:45,' + \
             '2025/08/09/17:30:36~2025/08/09/17:59:20'
        flagdata(vis=init_MS, mode='manual', spw='6~7,9~15',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/17:28:35~2025/08/09/17:28:40'
        flagdata(vis=init_MS, mode='manual', spw='7',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/17:30:36~2025/08/09/17:53:10'
        flagdata(vis=init_MS, mode='manual', spw='8',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/17:29:15~2025/08/09/17:29:18'
        flagdata(vis=init_MS, mode='manual', spw='9',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/17:09:00~2025/08/09/17:17:20'
        flagdata(vis=init_MS, mode='manual', spw='10',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/16:57:16~2025/08/09/17:19:20'
        flagdata(vis=init_MS, mode='manual', spw='11~14',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/17:19:20~2025/08/09/17:21:20'
        flagdata(vis=init_MS, mode='manual', spw='12~13',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/18:00:00~2025/08/09/18:01:20'
        flagdata(vis=init_MS, mode='manual', spw='13~14',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/17:30:19~2025/08/09/17:30:26'
        flagdata(vis=init_MS, mode='manual', spw='15',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/17:04:34~2025/08/09/17:04:42,' + \
             '2025/08/09/17:06:30~2025/08/09/17:06:44'
        flagdata(vis=init_MS, mode='manual', spw='27~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/17:03:02~2025/08/09/17:03:12,' + \
             '2025/08/09/17:05:20~2025/08/09/17:05:40,' + \
             '2025/08/09/17:07:48~2025/08/09/17:08:00,' + \
             '2025/08/09/17:53:26~2025/08/09/17:53:36,' + \
             '2025/08/09/17:55:42~2025/08/09/17:55:55,' + \
             '2025/08/09/18:11:00~2025/08/09/18:11:40'
        flagdata(vis=init_MS, mode='manual', spw='29~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/09/17:53:26~2025/08/09/17:53:42,' + \
             '2025/08/09/17:55:44~2025/08/09/17:56:00'
        flagdata(vis=init_MS, mode='manual', spw='30~31',
                 timerange=tt, flagbackup=False)
    if i == 23:
        tt = '2025/08/10/14:54:30~2025/08/10/15:01:30'
        flagdata(vis=init_MS, mode='manual', spw='11',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/10/14:50:22~2025/08/10/14:50:29'
        flagdata(vis=init_MS, mode='manual', spw='21~26,31',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/10/15:44:24~2025/08/10/15:44:46'
        flagdata(vis=init_MS, mode='manual', spw='23~26,28~31',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/10/15:42:00~2025/08/10/15:42:08,' + \
             '2025/08/10/15:46:54~2025/08/10/15:47:07,' + \
             '2025/08/10/16:38:08~2025/08/10/16:38:30'
        flagdata(vis=init_MS, mode='manual', spw='24,27',
                 timerange=tt, flagbackup=False)
        tt = '2025/08/10/15:51:00~2025/08/10/15:51:12,' + \
             '2025/08/10/16:06:05~2025/08/10/16:06:22'
        flagdata(vis=init_MS, mode='manual', spw='25~31',
                 timerange=tt, flagbackup=False)



    # rescale the fluxes based on interpolation between bootstrap executions
    ms.open(init_MS)
    med_time = np.median(ms.getdata('TIME')['time'])
    ms.close()
    _ = np.load('flux_bootstrap/' + calname + '_' + band + '.npz')
    mjd, calfact = _['mjd'], _['calfact']
    cfint = interp1d(mjd, calfact, axis=1, kind='linear', bounds_error=False,
                     fill_value=(calfact[:,0], calfact[:,-1]))
    cf = list(cfint(med_time))
    caltbl = init_MS.replace('.ms', '.gencal')
    os.system('rm -rf ' + caltbl + '*')
    gencal(vis=init_MS, caltable=caltbl, caltype='amp', spw=bspw, parameter=cf)
    applycal(vis=init_MS, gaintable=caltbl, calwt=True, flagbackup=True)
    fr_MS = proc_dir + EB[i] + 'pipeline.flag_rescale.ms'
    os.system('rm -rf ' + fr_MS + '*')
    mstransform(vis=init_MS, outputvis=fr_MS, datacolumn='corrected', spw=bspw)



    # Loop over each target field
    for j in range(len(targ_fields)):
        print('\n Averaging and splitting data for '+targ_fields[j]+' ... ')
        
        # Spectral averaging (1 pseudo-channel per SPW)
        o_MS = proc_dir + EB[i] + targ_names[j] + '.' + band + '.reduced.ms'
        os.system('rm -rf ' + o_MS + '*')
        mstransform(vis=fr_MS, outputvis=o_MS, datacolumn='data', spw=bspw,
                    field=targ_fields[j], chanaverage=True, chanbin=chbin)


    # Remove pipeline MS copy to save space
    os.system('rm -rf ' + init_MS + '*')
    print('----------------------------------------------------------------')
