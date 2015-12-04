import ntpath
import os
import logging

import numpy
import pytest

from hts.plate import plate
from hts.plate_data import readout, data_issue

logging.basicConfig(level=logging.INFO)

TEST_FOLDER_LUMINESCENCE_CSV = "luminescence_cell_viability_QC"
TEST_RUN_CONFIG = "run_config_insulin_1.txt"
TEST_FILE_INSULIN = os.path.join("insulin", "test_1.csv")
TEST_FILE_SIRNA = os.path.join("siRNA", "siRNA_12595.csv")
TEST_PLATELAYOUT = os.path.join("Plate_layouts", "plate_layout_siRNA_1.csv")
TEST_PLATE_COLUMN_7_s_1 = [107514.0, 106208.0, 101280.0, 99894.0, 103955.0, 101470.0]

TEST_PLATE = [['41092', '43724', '41396', '39340', '39628', '38404', '36288', '39940', '43876', '41504', '44136', '41752', '42672', '43688', '42184', '41928', '44800', '43740', '38072', '37856', '39044', '37980', '39912', '36776'], ['39112', '42112', '43500', '41000', '40884', '43528', '46964', '42512', '44248', '45192', '38340', '43912', '41304', '38288', '45236', '42384', '44440', '43536', '43008', '39776', '39528', '35932', '41536', '32064'], ['45496', '40820', '41100', '46476', '39560', '40920', '46572', '41188', '46276', '44584', '44948', '44428', '44416', '44040', '44108', '41192', '40348', '41884', '40304', '42316', '39980', '40056', '35788', '38100'], ['42628', '38108', '44816', '44224', '40952', '45208', '47668', '39364', '45816', '44892', '44960', '44528', '42480', '43468', '45628', '44096', '40568', '47376', '42268', '37628', '37292', '41044', '39812', '36528'], ['44520', '43944', '37680', '43504', '44516', '37656', '41716', '41936', '46856', '41536', '45652', '42504', '43796', '43164', '41432', '43344', '44960', '41020', '40196', '40288', '37480', '37552', '36744', '36140'], ['37444', '40492', '42452', '46168', '41368', '43644', '44048', '43632', '44840', '41208', '43516', '45000', '44624', '44336', '43580', '41588', '43012', '40368', '37056', '41784', '38008', '35168', '38496', '37740'], ['38764', '41884', '41272', '41160', '42644', '43076', '41184', '44008', '39824', '44064', '47928', '43604', '40460', '43372', '41588', '39540', '42608', '40564', '37880', '39360', '40244', '42352', '40808', '41188'], ['39388', '42016', '39660', '42104', '42592', '41000', '44788', '43292', '43252', '43408', '40436', '39420', '44192', '43356', '38532', '44824', '41924', '43012', '41560', '38920', '39428', '38956', '39060', '38008'], ['42016', '42580', '40560', '41752', '37584', '39072', '37880', '43280', '42448', '42676', '40748', '46412', '40744', '44752', '42548', '43212', '45728', '40896', '36984', '37672', '39920', '38240', '37316', '36176'], ['43012', '41256', '41376', '45172', '41232', '42236', '43852', '44996', '42396', '40532', '41232', '43460', '41312', '41576', '40608', '37192', '41676', '39988', '40780', '37000', '35240', '37900', '40964', '38412'], ['40316', '42424', '40088', '42292', '43820', '35108', '41816', '43744', '41244', '42576', '41028', '44104', '40608', '41892', '39024', '44096', '45260', '36696', '39956', '41856', '38028', '38100', '38832', '38280'], ['38696', '40624', '39880', '40616', '39520', '41776', '40504', '43680', '38960', '44908', '41440', '42988', '39112', '45088', '38560', '40668', '39340', '40632', '39092', '36572', '36496', '37608', '37784', '36784'], ['41056', '47092', '44220', '42096', '41496', '41976', '42152', '40548', '46520', '43788', '39340', '43116', '40908', '42964', '38040', '40668', '42796', '46304', '40736', '38836', '39916', '38680', '39332', '36628'], ['40760', '41172', '40036', '43752', '39276', '43540', '41096', '37604', '42408', '43800', '42364', '47256', '39104', '44436', '40704', '42152', '43900', '43540', '39792', '37140', '41488', '39816', '35396', '36804'], ['43240', '44080', '36664', '37020', '40132', '37444', '39816', '42924', '45404', '40572', '37816', '42344', '43648', '43768', '39628', '38836', '43212', '41588', '38964', '39884', '40308', '40476', '40120', '37996'], ['38036', '39988', '41336', '38140', '40928', '43584', '37888', '41932', '37888', '41396', '38016', '38688', '37364', '42824', '36408', '35100', '39968', '44780', '40648', '33520', '32912', '34748', '37528', '34236']]
TEST_PLATE_DATA_NAME = "test_plate_data_1"
TEST_PLATE2 = [['35904', '38436', '36572', '34976', '34720', '40260', '37960', '36836', '38596', '37520', '38840', '39452', '37096', '41808', '38532', '38364', '35268', '37928', '38188', '43788', '40524', '35444', '36660', '32136'], ['36852', '38076', '41300', '41624', '37672', '39952', '39116', '43628', '42796', '35612', '41504', '42168', '40300', '37984', '40380', '36324', '40672', '39192', '36004', '38192', '36656', '36816', '35280', '35800'], ['35764', '41312', '40572', '40632', '41696', '41092', '37072', '36396', '42052', '45144', '41164', '38624', '43136', '44648', '36852', '42172', '38384', '41660', '39512', '35696', '39568', '34640', '37752', '34460'], ['38976', '36604', '41640', '36520', '36512', '43516', '43996', '39616', '43508', '37828', '40264', '42168', '42264', '40964', '40632', '38176', '38008', '37600', '42368', '35336', '37560', '40500', '39448', '35296'], ['37052', '39644', '40644', '41500', '36232', '38576', '35612', '37468', '44124', '41296', '44080', '42700', '38728', '40148', '37468', '37112', '37804', '38304', '39124', '39664', '38164', '39600', '39660', '38476'], ['40240', '39652', '36912', '38168', '37832', '39740', '35612', '38584', '40128', '41392', '41604', '42084', '40472', '41388', '36432', '40448', '37944', '39688', '37836', '36992', '39744', '33880', '40936', '37272'], ['35648', '38012', '39776', '41592', '37208', '38916', '40764', '41180', '42012', '40216', '38608', '38916', '39528', '39508', '37616', '39320', '41228', '40792', '42560', '39092', '38640', '38848', '36572', '34072'], ['35512', '42116', '38736', '36336', '36708', '44028', '38796', '39924', '42160', '38216', '41256', '40692', '40848', '38296', '40324', '34296', '35076', '35496', '39036', '35168', '42352', '39352', '35236', '35748'], ['37544', '37368', '41456', '37176', '38484', '42068', '39260', '37128', '40676', '38060', '36096', '39856', '38672', '40152', '39132', '36032', '39444', '38912', '39588', '41600', '36584', '35372', '38664', '34564'], ['38948', '36652', '41880', '37276', '32792', '41304', '36700', '43524', '36028', '39196', '36824', '35240', '38620', '35696', '39884', '41860', '40136', '38212', '40092', '40064', '35284', '36972', '37272', '38692'], ['38672', '37260', '35948', '38024', '39148', '39376', '41644', '36740', '39948', '38180', '41576', '36252', '39396', '40496', '39192', '38872', '39712', '39064', '37672', '38360', '40980', '37820', '39020', '36076'], ['38760', '38500', '35804', '37224', '36472', '38140', '39416', '38244', '39516', '39220', '39472', '42396', '41340', '41140', '37048', '36104', '37596', '35708', '38652', '38952', '36896', '37728', '33708', '34252'], ['36668', '36644', '37440', '40568', '37304', '40248', '33352', '40756', '40544', '42508', '39616', '41584', '35860', '38328', '39284', '40612', '37988', '37404', '37196', '36132', '40120', '36848', '36764', '37204'], ['38700', '38788', '38644', '38404', '36208', '38768', '42368', '43348', '35972', '39348', '39468', '42156', '39336', '42684', '36400', '36420', '40008', '38384', '37616', '34824', '36784', '39424', '37864', '37172'], ['33752', '39016', '39412', '43360', '36772', '38040', '37168', '39888', '39700', '40028', '40624', '37896', '36884', '44620', '40552', '35896', '35236', '35756', '37352', '39692', '35056', '33960', '41580', '39072'], ['35000', '37800', '37160', '36280', '34776', '37636', '37664', '37756', '37800', '34920', '38676', '37260', '41132', '40540', '37292', '40724', '36516', '35068', '38052', '36460', '35100', '37428', '35612', '36012']]
TEST_PLATE_DATA_NAME2 = "test_plate_data_2"
TEST_DATA =  {TEST_PLATE_DATA_NAME: TEST_PLATE, TEST_PLATE_DATA_NAME2: TEST_PLATE2}
TEST_PLATE_NAME = "test_plate"

notfixed = pytest.mark.notfixed


@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath("."), "../", "test_data")

@pytest.fixture
def path_raw():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath("."), "../", "test_data", "Raw_data")


@pytest.mark.no_external_software_required
def test_create_from_readout(path):

    test_readout = readout.Readout(data=TEST_DATA)
    test_plate = plate.Plate(data={"readout": test_readout}, height=test_readout.height, width=test_readout.width, name=TEST_PLATE_NAME)
    assert type(test_plate) == plate.Plate
    assert test_plate.name == TEST_PLATE_NAME
    assert test_plate.height == test_readout.height
    assert test_plate.width == test_readout.width


@pytest.mark.no_external_software_required
def test_create_from_insulin_csv(path_raw):

    config = {"readout": {"paths": [os.path.join(path_raw, TEST_FILE_INSULIN)], "formats": ["insulin_csv"]}}
    test_plate = plate.Plate.create(format="config", **config)

    assert test_plate.name == ntpath.basename(TEST_FILE_INSULIN)
    assert type(test_plate.readout) == readout.Readout
    assert len(test_plate.readout.data) == 481
    assert type(test_plate.readout.data[0]) == numpy.ndarray


@pytest.mark.no_external_software_required
def test_filter_wells(path, path_raw):

    config = {"readout": {"paths": [os.path.join(path_raw, TEST_FILE_SIRNA)], "formats": ["envision_csv"]},
              "plate_layout": {"paths": [os.path.join(path, TEST_PLATELAYOUT)], "formats": ["csv"]}
              }
    test_plate = plate.Plate.create(format="config", **config)

    test_neg = test_plate.filter(condition_data_type="plate_layout", condition_data_tag="layout", condition=lambda x: x=="s_1",
                                 value_data_type="readout", value_data_tag="1", value_type=None)
    assert type(test_neg) == list
    assert all([i in test_neg for i in TEST_PLATE_COLUMN_7_s_1])


@pytest.mark.no_external_software_required
def test_calculate_net_fret(path, path_raw):

    config = {"readout": {"paths": [os.path.join(path_raw, TEST_FILE_SIRNA)], "formats": ["envision_csv"]},
              "plate_layout": {"paths": [os.path.join(path, TEST_PLATELAYOUT)], "formats": ["csv"]}
              }
    test_plate = plate.Plate.create(format="config", **config)

    test_plate.calculate_net_fret(donor_channel="2", acceptor_channel="1")
    assert type(test_plate.readout) == readout.Readout
    assert type(test_plate.readout.data["net_fret"]) == numpy.ndarray


@pytest.mark.no_external_software_required
def test_calculate_data_issue_realtime_glo(path, path_raw):

    config = {"readout": {"paths": [os.path.join(path_raw, TEST_FILE_SIRNA)], "formats": ["envision_csv"]},
              "plate_layout": {"paths": [os.path.join(path, TEST_PLATELAYOUT)], "formats": ["csv"]}
              }
    test_plate = plate.Plate.create(format="config", **config)

    # In real real-time glo experiments, wild-type untreated is used as control.
    test_plate.calculate_data_issue_cell_viability_real_time_glo(real_time_glo_measurement="1", normal_well="neg_1")
    assert type(test_plate.data_issue) == data_issue.DataIssue
    assert type(test_plate.data_issue.data["realtime-glo_pvalue"]) == numpy.ndarray
    assert type(test_plate.data_issue.data["realtime-glo_zscore"]) == numpy.ndarray
    assert type(test_plate.data_issue.data["realtime-glo_qc"]) == list


@pytest.mark.no_external_software_required
def test_model_as_gaussian_process(path, path_raw):

    config = {"readout": {"paths": [os.path.join(path_raw, TEST_FILE_SIRNA)], "formats": ["envision_csv"]},
              "plate_layout": {"paths": [os.path.join(path, TEST_PLATELAYOUT)], "formats": ["csv"]}
              }
    test_plate = plate.Plate.create(format="config", **config)
    test_plate.model_as_gaussian_process(data_tag_readout="1", sample_key="pos")