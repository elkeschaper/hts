# (C) 2015 Elke Schaper

"""
    :synopsis: Input/output for screen data.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import csv
import logging
import os
import re

LOG = logging.getLogger(__name__)

################################## READ SCREEN DATA  #########################


def read_envision_csv(file):
    """Read screen data file in [] format.

    The envision .csv file structure is not described publicly.
    It may be read in as a .csv file.

    The general file format is (luminescence example)::

        Plate information
        Plate,Repeat,Barcode,Measured height,Chamber temperature at start,Chamber temperature at end,Humidity at start,Humidity at end,Ambient temperature at start,Ambient temperature at end,Formula,Measurement date,
        1,1,,N/A,N/A,N/A,N/A,N/A,N/A,N/A,Calc 1: Crosstalk = Crosstalk correction where Label : US LUM 384 (cps)(1) channel 1,5/23/2015 16:41:02,

        Background information
        Plate,Label,Result,Signal,Flashes/Time,Meastime,MeasInfo,
        1,US LUM 384 (cps),0,3896,0.1,00:00:00.000,De=USLum Ex=N/A Em=N/A Wdw=N/A,

        27880,90040,6314480,6866120,7064360,7495280,7444560,7967720,7581640,8013480,8003800,8386840,8264000,8063960,7586280,7541760,8116560,8175520,8164640,7956520,7960440,7596680,168960,47000,
        42200,143720,7661600,7987840,8128920,8284800,8602480,8513080,8606000,8800960,8388760,8792520,8588520,8438760,8174720,8362200,8271280,8561720,8322160,8375560,8243640,7986680,171840,58280,
        49960,152920,8006520,8555840,8395680,8338240,8336760,8225720,8555840,8427720,8408880,8427800,8448560,8189920,8498800,8784560,8418480,8263760,8718480,8276200,8351440,8119240,174720,58800,
        50320,146320,7972520,8241160,8394440,8389360,8547840,8589160,8484840,8760520,8407200,8600920,8354160,8469600,8831160,8599920,8459360,8572960,8633920,8246800,9091200,8087600,174360,61400,
        50520,160760,8630160,8331000,8026720,8379800,8368800,8360920,8694200,8313320,8403720,8603720,8460840,8298080,8450040,8575720,9203200,9215560,8301600,8654520,8672280,8410840,174520,62360,
        50920,148080,8033960,8308480,8274960,8243480,8375960,8576080,8197400,8392400,8731920,8643560,8568720,8308680,8236840,8265280,9154640,9374480,8498200,8415400,8756600,8353160,174160,60400,
        52960,144080,7798040,8085440,8190400,7954800,8142320,7981600,8259640,8016800,8087040,8097640,8056320,7898400,7843760,8325080,8361280,8510960,7828040,8369680,8060600,7444600,161440,59800,
        50120,145400,7783760,7533040,7389480,8032120,7825960,7477880,7264160,7182400,8141320,7842360,7610760,7041360,7355960,7328680,7687000,7232400,7529480,7211440,7091960,7065080,144560,55600,
        49640,138480,7924440,7965320,8475000,8921800,8266640,8091680,8152880,8036600,7972800,8120280,8045120,7978760,7691840,8749720,8850000,8800720,8621680,8094320,7933200,8389240,175080,54520,
        48680,145240,8024480,8331400,8225280,8334040,8393400,8306400,8225960,8000680,7967920,7903760,8433200,8161960,7901560,8523240,8925800,8372280,8529520,8882720,8551080,8390480,173120,53240,
        51160,149200,8173320,8556000,8215000,8127600,8234800,8644080,8298800,8165760,7932640,7823760,8611000,8209520,8391360,8436080,8420160,8889120,8887560,8712840,8285040,8807680,179400,54040,
        50760,158600,8063400,8324480,8088840,8183320,7860520,8184560,8097480,7907720,7821400,8065480,8257560,8282920,8477000,8203040,8796040,8617480,8515800,8527280,8756480,8323160,166280,55080,
        50080,158600,8100640,8248480,8102800,8189200,8243920,8404040,8428960,8119400,8128080,8174360,8454080,9175480,8454920,8871360,8404120,8412720,8378200,8721800,8354640,8135040,163040,55600,
        48320,144800,8100600,8127600,8225840,8602760,8275280,8765040,8485040,8425920,8016720,8561280,9294000,8747760,8609720,8663520,8497240,8517520,8713440,8572840,8423920,8697920,164040,58680,
        45240,136360,7895040,7838120,7994680,8014320,8292720,8238080,8180600,7901440,8385880,8217400,8515040,8505480,9591720,9629720,8327040,8338560,8622040,8810000,8428240,8394080,168920,60040,
        41280,138080,7523960,7681600,7770920,8126640,8142200,7769360,7562400,7553120,7810280,7687320,8150400,7966120,9034840,9346880,8305920,8614160,8505400,8409480,8383360,8055640,155120,53440,

        Plate information
        Plate,Repeat,Barcode,Measured height,Chamber temperature at start,Chamber temperature at end,Humidity at start,Humidity at end,Ambient temperature at start,Ambient temperature at end,Group,Label,ScanX,ScanY,Measinfo,Kinetics,Measurement date,
        1,1,,14.76,26.18,26.11,30.5,30.7,24.19,24.12,1,US LUM 384 (cps)(1),0,0,De=USLum Ex=N/A Em=N/A Wdw=N/A,0,5/23/2015 16:41:02,

        Background information
        Plate,Label,Result,Signal,Flashes/Time,Meastime,MeasInfo,
        1,US LUM 384 (cps),0,3896,0.1,00:00:00.000,De=USLum Ex=N/A Em=N/A Wdw=N/A,

        27880,90040,6314480,6866120,7064360,7495280,7444560,7967720,7581640,8013480,8003800,8386840,8264000,8063960,7586280,7541760,8116560,8175520,8164640,7956520,7960440,7596680,168960,47000,
        42200,143720,7661600,7987840,8128920,8284800,8602480,8513080,8606000,8800960,8388760,8792520,8588520,8438760,8174720,8362200,8271280,8561720,8322160,8375560,8243640,7986680,171840,58280,
        49960,152920,8006520,8555840,8395680,8338240,8336760,8225720,8555840,8427720,8408880,8427800,8448560,8189920,8498800,8784560,8418480,8263760,8718480,8276200,8351440,8119240,174720,58800,
        50320,146320,7972520,8241160,8394440,8389360,8547840,8589160,8484840,8760520,8407200,8600920,8354160,8469600,8831160,8599920,8459360,8572960,8633920,8246800,9091200,8087600,174360,61400,
        50520,160760,8630160,8331000,8026720,8379800,8368800,8360920,8694200,8313320,8403720,8603720,8460840,8298080,8450040,8575720,9203200,9215560,8301600,8654520,8672280,8410840,174520,62360,
        50920,148080,8033960,8308480,8274960,8243480,8375960,8576080,8197400,8392400,8731920,8643560,8568720,8308680,8236840,8265280,9154640,9374480,8498200,8415400,8756600,8353160,174160,60400,
        52960,144080,7798040,8085440,8190400,7954800,8142320,7981600,8259640,8016800,8087040,8097640,8056320,7898400,7843760,8325080,8361280,8510960,7828040,8369680,8060600,7444600,161440,59800,
        50120,145400,7783760,7533040,7389480,8032120,7825960,7477880,7264160,7182400,8141320,7842360,7610760,7041360,7355960,7328680,7687000,7232400,7529480,7211440,7091960,7065080,144560,55600,
        49640,138480,7924440,7965320,8475000,8921800,8266640,8091680,8152880,8036600,7972800,8120280,8045120,7978760,7691840,8749720,8850000,8800720,8621680,8094320,7933200,8389240,175080,54520,
        48680,145240,8024480,8331400,8225280,8334040,8393400,8306400,8225960,8000680,7967920,7903760,8433200,8161960,7901560,8523240,8925800,8372280,8529520,8882720,8551080,8390480,173120,53240,
        51160,149200,8173320,8556000,8215000,8127600,8234800,8644080,8298800,8165760,7932640,7823760,8611000,8209520,8391360,8436080,8420160,8889120,8887560,8712840,8285040,8807680,179400,54040,
        50760,158600,8063400,8324480,8088840,8183320,7860520,8184560,8097480,7907720,7821400,8065480,8257560,8282920,8477000,8203040,8796040,8617480,8515800,8527280,8756480,8323160,166280,55080,
        50080,158600,8100640,8248480,8102800,8189200,8243920,8404040,8428960,8119400,8128080,8174360,8454080,9175480,8454920,8871360,8404120,8412720,8378200,8721800,8354640,8135040,163040,55600,
        48320,144800,8100600,8127600,8225840,8602760,8275280,8765040,8485040,8425920,8016720,8561280,9294000,8747760,8609720,8663520,8497240,8517520,8713440,8572840,8423920,8697920,164040,58680,
        45240,136360,7895040,7838120,7994680,8014320,8292720,8238080,8180600,7901440,8385880,8217400,8515040,8505480,9591720,9629720,8327040,8338560,8622040,8810000,8428240,8394080,168920,60040,
        41280,138080,7523960,7681600,7770920,8126640,8142200,7769360,7562400,7553120,7810280,7687320,8150400,7966120,9034840,9346880,8305920,8614160,8505400,8409480,8383360,8055640,155120,53440,


        Basic assay information
        Assay ID: ,,,,13383
        Assay Started: ,,,,5/23/2015 16:39:34
        Assay Finished: ,,,,5/23/2015 16:41:04
        Assay Exported: ,,,,5/23/2015 16:41:11
        Protocol ID: ,,,,50035
        Protocol Name: ,,,,US LUM 384
        Serial#: ,,,,1040204



        Protocol information
        Protocol:
        Protocol name,,,,US LUM 384
        Number of assay repeats,,,,1
        Start assay repeat each,,,,N/A
        Number of plate repeats,,,,1
        Start plate repeat each,,,,N/A
        Is label meas. height used,,,,Yes
        Height of measurement,,,,Defined in label
        Is gripper height used,,,,No
        Mode of measurement,,,,By Rows  bi-directional
        Rotated plate,,,,No
        Soft move,,,,No
        Protocol notes,,,,

        Plate type:
        Name of the plate type,,,,384 General
        Number of rows,,,,16
        Number of columns,,,,24
        Number of the wells in the plate,,,,384
        Height of the plate,,,,14.35 mm

        Coordinates of corners:
        384 General
        12.13 mm x------------------------------------------------------ x 115.63 mm
        8.99 mm                                                            8.99 mm

        12.13 mm x------------------------------------------------------ x 115.63 mm
        76.49 mm                                                           76.49 mm

        Platemap:
        Plate,,,,1
        Group,,,,1

        ,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
        A,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        B,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        C,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        D,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        E,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        F,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        G,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        H,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        I,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        J,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        K,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        L,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        M,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        N,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        O,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-
        P,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,- ,-

         - - Undefined

        Calculations:
        Plate,,,,1
         Formula index,,,,Calc 1
         Formula name,,,,CrossTalk
         Formula,,,,Crosstalk where Label : US LUM 384 (cps)(1) channel 1

        Auto export parameters:
        Export format,,,,Plate
        Include basic assay information,,,,Yes
        Place assay information at,,,,End of file
        Include basic plate information,,,,Yes
        Place plate information at,,,,Beginning of plate
        Include protocol information,,,,Yes
        Protocol info level,,,,Large
        Include error and warning information,,,,Yes
        Include background information,,,,Yes
        Add plate number to the file name,,,,Yes
        Each plate to separate file,,,,No
        Field separator to use,,,,System
        File name format,,,,<DefaultDataFolder>\<Date>\<Time>_<AssayID>.csv

        Operations:
        Plate 1
          Group 1
            Measurement
              Label,,,,US LUM 384 (cps)(1)

        Labels:
        US LUM 384 (cps),,,,7500004
        Measurement height,,,,0 mm
        Measurement time,,,,0.1 s
        CT,,,,0
        Aperture,,,,384 Plate US Luminescence aperture
        Last edited,,,,10/16/2008 14:06:15
        Last edited by,,,,Installation
        Factory preset,,,,Yes

        Aperture:
        384 Plate US Luminescence aperture,,,,9
        Height,,,,4.2 mm
        Diameter,,,,3.7 mm
        Description,,,,Can also be used in 96 plate
        Last edited,,,,10/16/2008 14:06:15
        Last edited by,,,,Installation
        Factory preset,,,,Yes

        Instrument:
        Serial number,,,,1040204
        Nickname,,,,EnVision

        Normalization:





        Exported with EnVision Workstation version X.XX Build X


    .. todo:: Extract all necessary information
    .. todo:: Show correct output format


    Args:
        filename (str): Path to the file with  data in the envision
            file format.


    Returns:
        dict: A dictionary of the output

        Output format::

            {
                'id': 'PF08261.7',
                'letters': ['A', 'C', 'D', ..., 'Y'],
                'COMPO':
                    {'insertion_emissions': [2.68618, 4.42225, ..., 3.61503],
                      'emissions': [2.28205, 5.14899, ..., 1.92022],
                      'transitions': [0.01467, 4.62483, ..., -inf]},
                '1':
                    {'insertion_emissions': [2.68618, 4.42225, ..., 3.61503],
                     'emissions': [1.00089, 4.54999, ..., 5.23581],
                     'transitions': [0.01467, 4.62483, ..., 0.95510]},
                ...
                '8':
                    {'insertion_emissions': [2.68618, 4.42225, ..., 3.61503],
                     'emissions': [4.12723, 5.39816, ..., 4.58094],
                     'transitions': [0.00990, 4.62006, ..., -inf]}
            }

    """

    pat_info = ['Plate', 'Repeat', 'Barcode', 'Measured height']
    pat_background = ['Plate', 'Label', 'Result']



    # Our possible parser states:
    #
    # 0: searching for Plate information header & store
    # 0.2 : storing plate information row
    # 2: searching for background information header & store.
    # 2.2: storing background information
    # 2.3: storing plate data

    # 4: searching for basic assay information
    # 4.1: search for Assay ID
    # 4.2: search for Assay Start
    # 4.3: search for Assay Finished
    # 4.4: search for Protocol ID
    # 4.5: search for Protocol Name
    # 4.6: search for Serial hash
    # 5: search for Exported with EnVision Workstation version number

    state = 0
    data_plate_count = 0
    channel_wise_reads = {}
    channel_wise_info = {}
    plate_info = {}
    with open(file) as csvfile:
        #dialect = csv.Sniffer().sniff(csvfile.read(1024))
        #sample_text = ''.join(csvfile.readline() for x in range(3))
        #dialect = csv.Sniffer().sniff(sample_text)
        #reader = csv.reader(csvfile, dialect)
        #csvfile.seek(0)
        #import pdb; pdb.set_trace()
        reader = csv.reader(csvfile, delimiter = ",")
        for i, line in enumerate(reader):
            if len(line) <= 1:
                continue
            #print(line)
            LOG.debug("Line %s: %s", i, line)
            if 0 == state:
                if pat_info == line[:4]:
                    LOG.debug(" * (0->0.2) Found plate info & Store plate info tags.")
                    plate_info_tags = line
                    state = 0.2

            elif 0.2 == state:
                plate_info = {i:j for i,j in zip(plate_info_tags, line) if i != ""}
                LOG.debug(" * (0.2->2) Store plate info.")
                state = 2

            elif 2 == state:
                if pat_background == line[:3]:
                    data_plate_count += 1
                    data_background_info_tags = line
                    LOG.debug(" * (2->2.2) Found plate data start.")
                    state = 2.2

            elif 2.2 == state:
                data_background_info = {i:j for i,j in zip(data_background_info_tags, line) if i != ""}
                LOG.debug(" * (2.2->2.3) Store background info.")
                state = 2.3

            elif 2.3 == state:
                if len(line) >= 25 and line[0] != "":
                    data_plate = [[i for i in line if (i != "" and not i.isalpha())]]
                    line_length = len(data_plate[0])
                    LOG.debug(" * (2.3->2.4) Store first plate readout line.")
                    state = 2.4

            elif 2.4 == state:
                if len(line) >= 25 and line[0] != "":
                    data_plate.append([i for i in line if (i != "" and not i.isalpha())])
                    if line_length != len(data_plate[-1]):
                        LOG.error(" The lines in the plate differ in length. line_length: {}. line: {}".format(line_length, data_plate[-1]))
                    LOG.debug(" * (2.4->2.4) Store another plate readout line.")
                    state = 2.4
                else:
                    channel_wise_reads[data_plate_count] = data_plate
                    channel_wise_info[data_plate_count] = data_background_info
                    data_plate = None
                    LOG.debug(" * (2.4->2) Plate readout complete.")
                    state = 2

    if data_plate:
        channel_wise_reads[data_plate_count] = data_plate
        channel_wise_info[data_plate_count] = data_background_info
        LOG.debug(" * (2.4->None) Overall plate readout complete.")
        state = None

    return plate_info, channel_wise_reads, channel_wise_info