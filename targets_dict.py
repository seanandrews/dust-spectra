targ = {}

targ['FMTau']      = {'name': 'FMTau', 'label': 'FM Tau',
                      'vlabel': 'FM_Tau',
                      'X': {'X01_1': {'nt': 15.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False,
                                      'psolint': ['inf', '30s'], 
                                      'asolint': ['inf', '30s']}},
                      'RA': '04:14:13.58', 'DEC': '28:12:49.17',
                      'mua': 8.383, 'mud': -24.540}

targ['FNTau']      = {'name': 'FNTau', 'label': 'FN Tau',
                      'vlabel': 'FN_Tau',
                      'X': {'X01_1': {'nt': 10.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False,
                                      'psolint': ['inf'], 'asolint': ['inf']}},
                      'RA': '04:14:14.59', 'DEC': '28:27:58.07',
                      'mua': 9.344, 'mud': -23.839}

targ['CWTau']      = {'name': 'CWTau', 'label': 'CW Tau',
                      'vlabel': 'CW_Tau',
                      'X': {'X01_1': {'nt': 15.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False,
                                      'psolint': ['inf', '30s'], 
                                      'asolint': ['inf', '30s']}},
                      'RA': '04:14:17.00', 'DEC': '28:10:57.77',
                      'mua': 8.144, 'mud': -24.206}

targ['CIDA1']      = {'name': 'CIDA1', 'label': 'CIDA 1',
                      'vlabel': 'CIDA_1',
                      'RA': '04:14:17.61', 'DEC': '28:06:09.65',
                      'mua': 8.285, 'mud': -23.607}

targ['MHO1']       = {'name': ['MHO1', 'MHO2'], 
                      'label': ['MHO 1', 'MHO 2'],
                      'vlabel': 'MHO_2',
                      'X': {'X01_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False, 
                                      'psolint': ['inf'], 'asolint': ['inf']}},
                      'RA': ['04:14:26.27', '04:14:26.40'],
                      'DEC': ['28:06:03.27', '28:05:59.64'],
                      'mua': [7.954, 9.889], 'mud': [-26.469, -25.386]}

targ['FPTau']      = {'name': 'FPTau', 'label': 'FP Tau',
                      'vlabel': 'FP_Tau',
                      'X': {'X01_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False,
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:14:47.30', 'DEC': '26:46:26.41',
                      'mua': 8.990, 'mud': -22.658}

targ['CXTau']      = {'name': 'CXTau', 'label': 'CX Tau',
                      'vlabel': 'CX_Tau',
                      'X': {'X01_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 2,
                                      'peel': True, 'peel_mode': 'mfs',
                                      'peel_pb': '0.25',
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:14:47.86', 'DEC': '26:48:11.01',
                      'mua': 8.745, 'mud': -22.530,
                      'outlier_RA': '04:14:47.46',
                      'outlier_DEC': '26:51:43.69'}

targ['J04153916']  = {'name': 'J04153916', 'label': 'J04153916+2818586',
                      'vlabel': 'J04153916',
                      'X': {'X01_1': {'nt': 10.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False,
                                      'psolint': ['inf'], 'asolint': ['inf']}},
                      'RA': '04:15:39.16', 'DEC': '28:18:58.53',
                      'mua': 9.547, 'mud': -24.137}

targ['IRAS04125']  = {'name': 'IRAS04125', 'label': 'IRAS 04125+2902',
                      'vlabel': 'IRAS_04125',
                      'X': {'X01_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1.5,
                                      'peel': True, 'peel_pb': '0.2', 
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:15:42.79', 'DEC': '29:09:59.83',
                      'mua': 12.104, 'mud': -18.145}

targ['J04155799']  = {'name': 'J04155799', 'label': 'J04155799+2746175',
                      'vlabel': 'J04155799',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:15:58.00', 'DEC': '27:46:17.33',
                      'mua': 8.940, 'mud': -24.438}

targ['CYTau']      = {'name': 'CYTau', 'label': 'CY Tau',
                      'vlabel': 'CY_Tau',
                      'X_imaging': {'X_nt': 11.0, 'X_lnt': 4.0, 'X_imscl': 2,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:17:33.73', 'DEC': '28:20:46.81',
                      'mua': 8.886, 'mud': -25.679}

targ['KPNO10']     = {'name': 'KPNO10', 'label': 'KPNO 10',
                      'vlabel': 'KPNO_10',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:17:49.56', 'DEC': '28:13:31.77',
                      'mua': 8.800, 'mud': -25.182}

targ['V409Tau']    = {'name': 'V409Tau', 'label': 'V409 Tau',
                      'vlabel': 'V409_Tau',
                      'X': {'X03_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1.0,
                                      'peel': False,
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:18:10.78', 'DEC': '25:19:57.38',
                      'mua': 8.798, 'mud': -23.448}

targ['V410Xray2']  = {'name': 'V410Xray2', 'label': 'V410 X-ray 2',
                      'vlabel': 'V410_X-ray_2',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 3,
                                    'X_peelnt': 15.0, 'X_peellnt': 5.0,
                                    'X_peel': True, 
                                    'X_psolint': ['inf'], 'X_pminsnr': 3.0, 
                                    'X_asolint': ['inf'], 'X_aminsnr': 3.0},
                      'RA': '04:18:34.45', 'DEC': '28:30:30.23',
                      'mua': 10., 'mud': -20.}

targ['V892Tau']    = {'name': 'V892Tau', 'label': 'V892 Tau',
                      'vlabel': 'V892_Tau',
                      'X': {'X03_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False, 
                                      'psolint': ['inf'], 'asolint': ['inf']}},
                      'RA': '04:18:40.62', 'DEC': '28:19:15.63',
                      'mua': 3.517, 'mud': -28.806}

targ['LR1']        = {'name': 'LR1', 'label': 'LR 1',
                      'vlabel': 'LR_1',
                      'X': {'X03_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1.0,
                                      'peel': False,
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:18:41.33', 'DEC': '28:27:25.01',
                      'mua': 10., 'mud': -20.}

targ['BPTau']      = {'name': 'BPTau', 'label': 'BP Tau',
                      'vlabel': 'BP_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:19:15.83', 'DEC': '29:06:26.93',
                      'mua': 8.889, 'mud': -26.011}

targ['J04202144']  = {'name': 'J04202144', 'label': 'J04202144+2813491',
                      'vlabel': 'J04202144',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:20:21.44', 'DEC': '28:13:49.17',
                      'mua': 10., 'mud': -26.}

targ['J04202555']  = {'name': 'J04202555', 'label': 'J04202555+2700355',
                      'vlabel': 'J04202555',
                      'X': {'X03_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1.0,
                                      'peel': False,
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:20:25.56', 'DEC': '27:00:35.55',
                      'mua': 11.175, 'mud': -17.696}

targ['DETau']      = {'name': 'DETau', 'label': 'DE Tau',
                      'vlabel': 'DE_Tau',
                      'X_imaging': {'X_nt': 4.0, 'X_lnt': 2.0, 'X_imscl': 3,
                                    'X_peelnt': 5.0, 'X_peellnt': 2.0,
                                    'X_peel': True, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:21:55.63', 'DEC': '27:55:06.18',
                      'mua': 10.624, 'mud': -27.198,
                      'outlier_RA': '04:21:28.17',
                      'outlier_DEC': '27:51:02.66'}     # ~20" patch

targ['RYTau']      = {'name': 'RYTau', 'label': 'RY Tau',
                      'vlabel': 'RY_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:21:57.41', 'DEC': '28:26:35.56',
                      'mua': 8.744, 'mud': -27.002}

targ['IRAS04196']  = {'name': 'IRAS04196', 'label': 'IRAS 04196+2638',
                      'vlabel': 'IRAS_04196',
                      'X': {'X03_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False,
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:22:47.88', 'DEC': '26:45:52.87',
                      'mua': 11.595, 'mud': -17.399}

targ['IRAS04200']  = {'name': 'IRAS04200', 'label': 'IRAS 04200+2759',
                      'vlabel': 'IRAS_04200',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:23:07.78', 'DEC': '28:05:57.47',
                      'mua': 9.825, 'mud': -26.710}

targ['FTTau']      = {'name': 'FTTau', 'label': 'FT Tau',
                      'vlabel': 'FT_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:23:39.19', 'DEC': '24:56:14.25',
                      'mua': 7.448, 'mud': -21.849}

targ['IPTau']      = {'name': 'IPTau', 'label': 'IP Tau',
                      'vlabel': 'IP_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:24:57.08', 'DEC': '27:11:56.54',
                      'mua': 8.308, 'mud': -26.541}

targ['DGTau']      = {'name': 'DGTau', 'label': 'DG Tau',
                      'vlabel': 'DG_Tau',
                      'X': {'X03_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False,
                                      'psolint': ['inf'], 'asolint': ['inf']}},
                      'RA': '04:27:04.69', 'DEC': '26:06:16.06',
                      'mua': 5.514, 'mud': -20.478}

targ['IRAS04260']  = {'name': 'IRAS04260', 'label': 'IRAS 04260+2642',
                      'vlabel': 'IRAS_04260',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:29:04.98', 'DEC': '26:49:07.19',
                      'mua': 6.909, 'mud': -18.699}

targ['XEST13-010'] = {'name': 'XEST13-010', 'label': 'XEST 13-010',
                      'vlabel': 'XEST_13-010',
                      'X': {'X03_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': False,
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:29:36.06', 'DEC': '24:35:55.59',
                      'mua': 8.637, 'mud': -20.641}

targ['IQTau']      = {'name': 'IQTau', 'label': 'IQ Tau',
                      'vlabel': 'IQ_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:29:51.56', 'DEC': '26:06:44.86',
                      'mua': 5.951, 'mud': -21.309}

targ['UXTau']      = {'name': ['UXTauA', 'UXTauB', 'UXTauC'],
                      'label': ['UX Tau A', 'UX Tau B', 'UX Tau C'],
                      'vlabel': 'UX_Tau_A',
                      'X_imaging': {'X_nt': 7.0, 'X_lnt': 4.0, 'X_imscl': 3,
                                    'X_peel': True, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': ['04:30:04.00', '04:30:03.58', '04:30:03.99'],
                      'DEC': ['18:13:49.47', '18:13:49.48', '18:13:46.79'],
                      'mua': [12.850, 13.732, 12.560],
                      'mud': [-17.335, -20.007, -19.804],
                      'outlier_RA': '04:29:29.06',
                      'outlier_DEC': '18:15:52.42'}

targ['ZZTauIRS']   = {'name': 'ZZTauIRS', 'label': 'ZZ Tau IRS',
                      'vlabel': 'ZZ_Tau_IRS',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:30:51.72', 'DEC': '24:41:47.46',
                      'mua': 10.675, 'mud': -14.991}

targ['HLTau']      = {'name': 'HLTau', 'label': 'HL Tau',
                      'vlabel': 'HL_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:31:38.51', 'DEC': '18:13:57.86',
                      'mua': 4.2, 'mud': -15.3}

targ['Haro6-13']   = {'name': 'Haro6-13', 'label': 'Haro 6-13',
                      'vlabel': 'Haro_6-13',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:32:15.42', 'DEC': '24:28:59.58',
                      'mua': 5.300, 'mud': -21.168}

targ['MHO6']       = {'name': 'MHO6', 'label': 'MHO 6',
                      'vlabel': 'MHO_6',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:32:22.11', 'DEC': '18:27:42.65',
                      'mua': 12.474, 'mud': -18.693}

targ['GGTau']      = {'name': ['GGTauA', 'GGTauB'], 
                      'label': ['GG Tau A', 'GG Tau B'],
                      'vlabel': 'GG_Tau_A',
                      'X_imaging': {'X_nt': 11.0, 'X_lnt': 4.0, 'X_imscl': 3,
                                    'X_peel': True, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': ['04:32:30.35', '04:32:30.28'], 
                      'DEC': ['17:31:40.49', '17:31:30.45'],
                      'mua': [13.209, 13.180], 'mud': [-18.211, -20.461],
                      'outlier_RA': '04:31:57.37',
                      'outlier_DEC': '17:31:35.87'}

targ['FY_FZTau']   = {'name': ['FYTau' 'FZTau'],
                      'label': ['FY Tau', 'FZ Tau'],
                      'vlabel': 'FY_Tau',
                      'X_imaging': {'X_nt': 7.0, 'X_lnt': 4.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': ['04:32:30.58', '04:32:31.76'],
                      'DEC': ['24:19:57.36', '24:20:03.06'],
                      'mua': [6.842, 7.308], 'mud': [-21.546, -21.396]}

targ['UZTau']      = {'name': ['UZTauE', 'UZTauW'],
                      'label': ['UZ Tau E', 'UZ Tau W'],
                      'vlabel': 'UZ_Tau_E',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': ['04:32:43.07', '04:32:42.81'],
                      'DEC': ['25:52:31.01', '25:52:31.20'],
                      'mua': [5.460, 1.662], 'mud': [-22.021, -18.815]}

targ['V807Tau']    = {'name': 'V807Tau', 'label': 'V807 Tau',
                      'vlabel': 'V807_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:33:06.64', 'DEC': '24:09:54.98',
                      'mua': 5.800, 'mud': -16.252}

targ['IRAS04301']  = {'name': 'IRAS04301', 'label': 'IRAS 04301+2608',
                      'vlabel': 'IRAS_04301',
                      'X': {'X10_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 2,
                                      'p_pblim': -0.02, 
                                      'p_nt': 10., 'p_lnt': 4.,
                                      'peel': True, 'peel_pb': '0.25',
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:33:14.36', 'DEC': '26:14:23.46',
                      'mua': 7.746, 'mud': -17.166}

targ['J04333278']  = {'name': 'J04333278', 'label': 'J04333278+1800436',
                      'vlabel': 'J04333278',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:33:32.81', 'DEC': '18:00:43.61',
                      'mua': 13.704, 'mud': -18.178}

targ['GI_GKTau']   = {'name': ['GITau', 'GKTau'],
                      'label': ['GI Tau', 'GK Tau'],
                      'vlabel': 'GK_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': ['04:33:34.06', '04:33:34.56'],
                      'DEC': ['24:21:17.07', '24:21:05.86'],
                      'mua': [5.764, 7.465], 'mud': [-20.642, -20.510]}

targ['J04333905']  = {'name': 'J04333905', 'label': 'J04333905+2227207',
                      'vlabel': 'J04333905',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 3,
                                    'X_peel': True, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:33:39.08', 'DEC': '22:27:20.44',
                      'mua': 6., 'mud': -20.,
                      'outlier_RA': '04:33:22.71',
                      'outlier_DEC': '22:26:46.58'}

targ['DLTau']      = {'name': 'DLTau', 'label': 'DL Tau',
                      'vlabel': 'DL_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:33:39.08', 'DEC': '25:20:38.10',
                      'mua': 9.252, 'mud': -18.497}

targ['J04334171']  = {'name': 'J04334171', 'label': 'J04334171+1750402',
                      'vlabel': 'J04334171',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:33:41.73', 'DEC': '17:50:40.14',
                      'mua': 12.587, 'mud': -19.651}

targ['J04334465']  = {'name': 'J04334465', 'label': 'J04334465+2615005',
                      'vlabel': 'J04334465',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:33:44.66', 'DEC': '26:15:00.44',
                      'mua': 8.054, 'mud': -17.747}

targ['DMTau']      = {'name': 'DMTau', 'label': 'DM Tau',
                      'vlabel': 'DM_Tau',
                      'X_imaging': {'X_nt': 4.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:33:48.73', 'DEC': '18:10:09.97',
                      'mua': 11.691, 'mud': -18.292}

targ['CITau']      = {'name': 'CITau', 'label': 'CI Tau',
                      'vlabel': 'CI_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:33:52.01', 'DEC': '22:50:32.09',
                      'mua': 8.942, 'mud': -17.079}

targ['AATau']      = {'name': 'AATau', 'label': 'AA Tau',
                      'vlabel': 'AA_Tau',
                      'X_imaging': {'X_nt': 4.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:34:55.42', 'DEC': '24:28:53.03',
                      'mua': 5.323, 'mud': -20.680}

targ['HOTau']      = {'name': 'HOTau', 'label': 'HO Tau',
                      'vlabel': 'HO_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:35:20.21', 'DEC': '22:32:14.56',
                      'mua': 9.721, 'mud': -16.898}

targ['DNTau']      = {'name': 'DNTau', 'label': 'DN Tau',
                      'vlabel': 'DN_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:35:27.38', 'DEC': '24:14:58.91',
                      'mua': 6.056, 'mud': -20.864}

targ['HQTau']      = {'name': 'HQTau', 'label': 'HQ Tau',
                      'vlabel': 'HQ_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:35:47.34', 'DEC': '22:50:21.69',
                      'mua': 10.868, 'mud': -18.980}

targ['HPTau']      = {'name': 'HPTau', 'label': 'HP Tau',
                      'vlabel': 'HP_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:35:52.78', 'DEC': '22:54:23.16',
                      'mua': 9.037, 'mud': -13.853}

targ['DOTau']      = {'name': 'DOTau', 'label': 'DO Tau',
                      'vlabel': 'DO_Tau',
                      'X': {'X10_1': {'nt': 10.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': True, 'peel_mode': 'spw',
                                      'peel_pb': '0.25',
                                      'psolint': ['inf'], 'asolint': ['inf']}},
                      'RA': '04:38:28.58', 'DEC': '26:10:49.47',
                      'mua': 6.268, 'mud': -21.047}

targ['HVTau']      = {'name': ['HVTauAB', 'HVTauC'], 
                      'label': ['HV Tau AB', 'HV Tau/c'],
                      'vlabel': 'HV_Tau_C',
                      'X': {'X10_1': {'nt': 15.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': True, 'peel_mode': 'mfs',
                                      'psolint': [], 'asolint': []}},
                      'RA': ['04:38:35.29', '04:38:35.51'], 
                      'DEC': ['26:10:38.64', '26:10:41.32'],
                      'mua': [4.776, 4.776], 'mud': [-21.377, -21.377]}

targ['J04385859']  = {'name': 'J04385859', 'label': 'J04385859+2336351',
                      'vlabel': 'J04385859',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:38:58.60', 'DEC': '23:36:35.15',
                      'mua': 8.091, 'mud': -21.201}

targ['LkCa15']     = {'name': 'LkCa15', 'label': 'LkCa 15',
                      'vlabel': 'LkCa_15',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:39:17.79', 'DEC': '22:21:03.39',
                      'mua': 10.573, 'mud': -17.527}

targ['ITG15']      = {'name': 'ITG15', 'label': 'ITG 15',
                      'vlabel': 'ITG_15',
                      'X': {'X11_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': True, 'peel_mode': 'mfs',
                                      'peel_pb': '0.5',
                                      'psolint': [], 'asolint': []},
                            'X12_1': {'nt': 5.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': True, 'peel_mode': 'mfs',
                                      'peel_pb': '0.5',
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:39:44.88', 'DEC': '26:01:52.71',
                      'mua': 6.687, 'mud': -21.949}

targ['IRAS04370']  = {'name': 'IRAS04370', 'label': 'IRAS 04370+2559',
                      'vlabel': 'IRAS_04370',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 3,
                                    'X_peel': True, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:40:08.00', 'DEC': '26:05:25.43',
                      'mua': 5.650, 'mud': -20.769,
                      'outlier_RA': '04:40:23.85',
                      'outlier_DEC': '26:05:01.27'}

targ['IRAS04385']  = {'name': 'IRAS04385', 'label': 'IRAS 04385+2550',
                      'vlabel': 'IRAS_04385',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:41:38.83', 'DEC': '25:56:26.74',
                      'mua': 6.167, 'mud': -19.329,
                      'outlier_RA': '04:42:06.06',
                      'outlier_DEC': '25:59:14.71'}

targ['CIDA7']      = {'name': 'CIDA7', 'label': 'CIDA 7',
                      'vlabel': 'CIDA_7',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:42:21.02', 'DEC': '25:20:34.31',
                      'mua': 4.633, 'mud': -19.774}

targ['GOTau']      = {'name': 'GOTau', 'label': 'GO Tau',
                      'vlabel': 'GO_Tau',
                      'X': {'X12_1': {'nt': 10.0, 'lnt': 2.0, 'imscl': 1,
                                      'peel': True, 'peel_mode': 'mfs',
                                      'peel_pb': '0.5',
                                      'psolint': [], 'asolint': []}},
                      'RA': '04:43:03.08', 'DEC': '25:20:18.71',
                      'mua': 4.736, 'mud': -20.109}

targ['IRAS04414']  = {'name': 'IRAS04414', 'label': 'IRAS 04414+2506',
                      'vlabel': 'IRAS_04414',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:44:27.14', 'DEC': '25:12:16.43',
                      'mua': 5.760, 'mud': -19.848}

targ['IRAS04429']  = {'name': 'IRAS04429', 'label': 'IRAS 04429+1550',
                      'vlabel': 'IRAS_04429',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:45:51.35', 'DEC': '15:55:36.66',
                      'mua': 11.614, 'mud': -18.058}

targ['DQTau']      = {'name': 'DQTau', 'label': 'DQ Tau',
                      'vlabel': 'DQ_Tau',
                      'X_imaging': {'X_nt': 7.0, 'X_lnt': 4.0, 'X_imscl': 3,
                                    'X_peel': True, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:46:53.06', 'DEC': '17:00:00.14',
                      'mua': 4.906, 'mud': -13.296,
                      'outlier_RA': '04:46:55.14',
                      'outlier_DEC': '17:06:44.69'}

targ['Haro6-37']   = {'name': ['Haro6-37AB', 'Haro6-37C'],
                      'label': ['Haro 6-37 AB', 'Haro 6-37 C'],
                      'vlabel': 'Haro_6-37_C',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 5,
                                    'X_peelnt': 15.0, 'X_peellnt': 5.0,
                                    'X_peel': True, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': ['04:46:58.97', '04:46:59.09'],
                      'DEC': ['17:02:37.89', '17:02:39.96'],
                      'mua': [4.952, 5.298], 'mud': [-13.086, -14.131],
                      'outlier_RA': '04:46:55.16',
                      'outlier_DEC': '17:06:44.81'}     # same as DQ Tau

targ['DRTau']      = {'name': 'DRTau', 'label': 'DR Tau',
                      'vlabel': 'DR_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:47:06.22', 'DEC': '16:58:42.81',
                      'mua': 5.207, 'mud': -13.889}

targ['DSTau']      = {'name': 'DSTau', 'label': 'DS Tau',
                      'vlabel': 'DS_Tau',
                      'X_imaging': {'X_nt': 11.0, 'X_lnt': 4.0, 'X_imscl': 3,
                                    'X_peel': True, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '04:47:48.60', 'DEC': '29:25:11.19',
                      'mua': 5.049, 'mud': -24.439,
                      'outlier_RA': '04:47:46.45',
                      'outlier_DEC': '29:22:03.70'}

targ['GMAur']      = {'name': 'GMAur', 'label': 'GM Aur',
                      'vlabel': 'GM_Aur',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:55:10.98', 'DEC': '30:21:59.37',
                      'mua': 3.748, 'mud': -24.298}

targ['ABAur']      = {'name': 'ABAur', 'label': 'AB Aur',
                      'vlabel': 'AB_Aur',
                      'RA': '04:55:45.85', 'DEC': '30:33:04.29',
                      'mua': 4.018, 'mud': -24.027,
                      'X_imaging': {'X_nt': 7.0, 'X_lnt': 3.0, 'X_imscl': 3,
                                    'X_peelnt': 11.0, 'X_peellnt': 4.0,
                                    'X_peel': True, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'outlier_RA': '04:55:55.65',
                      'outlier_DEC': '30:40:41.93'}

targ['SUAur']      = {'name': 'SUAur', 'label': 'SU Aur',
                      'vlabel': 'SU_Aur',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 3,
                                    'X_peelnt': 11.0, 'X_peellnt': 4.0,
                                    'X_peel': True, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:55:59.39', 'DEC': '30:34:01.50',
                      'mua': 4.185, 'mud': -24.304,
                      'outlier_RA': '04:55:55.78',
                      'outlier_DEC': '30:40:42.32'}     # same as for AB Aur

targ['MWC480']     = {'name': 'MWC480', 'label': 'MWC 480',
                      'vlabel': 'MWC_480',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '04:58:46.27', 'DEC': '29:50:36.99',
                      'mua': 4.661, 'mud': -25.168}

targ['V836Tau']    = {'name': 'V836Tau', 'label': 'V836 Tau',
                      'vlabel': 'V836_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 3,
                                    'X_peelnt': 15.0, 'X_peellnt': 5.0,
                                    'X_peel': True, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '05:03:06.59', 'DEC': '25:23:19.61',
                      'mua': 2.991, 'mud': -17.304,
                      'outlier_RA': '05:02:58.54',
                      'outlier_DEC': '25:16:25.00'}     # need ~15" radius

targ['CIDA8']      = {'name': 'CIDA8', 'label': 'CIDA 8',
                      'vlabel': 'CIDA_8',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '05:04:41.40', 'DEC': '25:09:54.58',
                      'mua': 2.379, 'mud': -16.979}

targ['MWC758']     = {'name': 'MWC758', 'label': 'MWC 758',
                      'vlabel': 'MWC_758',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 1,
                                    'X_peel': False, 'X_psolint': [],
                                    'X_pminsnr': 3.0, 'X_asolint': [],
                                    'X_aminsnr': 3.0},
                      'RA': '05:30:27.53', 'DEC': '25:19:57.08',
                      'mua': 3.685, 'mud': -26.373}

targ['CQTau']      = {'name': 'CQTau', 'label': 'CQ Tau',
                      'vlabel': 'CQ_Tau',
                      'X_imaging': {'X_nt': 5.0, 'X_lnt': 2.0, 'X_imscl': 3,
                                    'X_peel': True, 'X_psolint': ['inf'],
                                    'X_pminsnr': 3.0, 'X_asolint': ['inf'],
                                    'X_aminsnr': 3.0},
                      'RA': '05:35:58.47', 'DEC': '24:44:54.09',
                      'mua': 2.987, 'mud': -26.364}
