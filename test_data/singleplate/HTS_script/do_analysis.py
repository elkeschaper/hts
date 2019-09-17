import logging
import os
import matplotlib
matplotlib.use('TkAgg')

from hts.run.run import Run

# Set the level of logging information (DEBUG, INFO, WARNING, ERROR).
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

# Define the base directory of the file system.
#PATH_TRUNK = "/Users/jdauvill/HTS/HTS_data"
PATH_TRUNK = "/Users/merveavar/PrionX_HTS"

#PATH_RUN_CONFIG = os.path.join(PATH_TRUNK, "Runs")
PATH_RUN_CONFIG = os.path.join(PATH_TRUNK, "HTS_script")

# Define for which runs the analysis should run.
#RUN_CONFIG1 = os.path.join(PATH_RUN_CONFIG, 'run_config_siRNA_20160318_Bei_Valeria.txt')
#RUN_CONFIG2 = os.path.join(PATH_RUN_CONFIG, 'run_config_siRNA_20160406_Bei_Valeria.txt')
#RUN_CONFIG3 = os.path.join(PATH_RUN_CONFIG, 'run_config_siRNA_20160418_Bei_Valeria.txt')
#l_run = [RUN_CONFIG1, RUN_CONFIG2, RUN_CONFIG3]
l_run = [os.path.join(PATH_RUN_CONFIG, 'run_config.txt')]

for i_run in l_run:
    print(i_run)
    my_run = Run.create(origin="config", path=os.path.join(PATH_RUN_CONFIG, i_run), reload=True)

    # Retrieve the measurement data in simple row wise .csv format:
    # data_pd = my_run.write(format="serialize_as_pandas", path=None, return_string=True)
    # my_run.write(format="csv_one_well_per_row", path="/path/of/choice/file.csv")

    # Do QC analysis.
    qc = my_run.qc(force=True)

    # Perform Gaussian process normalization.
# import pdb; pdb.set_trace()
    my_run.do_task(type="gp", force=True)

    # Add the meta data from the picklist.
    if not hasattr(my_run, "is_created_from_pickle"):
        my_run.add_meta_data(tag="sirna")
        my_run.add_data_from_data_frame(tags=["meta_SEQUENCE"])

    # Create the normalization report.
    my_run.do_task(type="normalization", force=True)

    # Create all other analysis reports.
    my_run.do_task(type="report", force=True)

    # Save the data as a .pickle file
    #my_run.write(format="pickle")

    ## Define variable names for all variables that you wish to save in the aggregated measurement data.
    # Raw data (sample compared to sample distribution)
    PVALUE_VS_S_RAW = "signal__vs__s__p_value"  # (variable name from protocol config)
    SS_VS_S_RAW = "signal__vs__s__standard_score" # (variable name from protocol config)
    RANK_RAW = "rank__raw_signal__pvalue_s"

    # Raw data (sample compared to negative control distribution)
    PVALUE_VS_NEG_RAW = "signal__vs__neg__p_value" # (variable name from protocol config)
    SS_VS_NEG_RAW = "signal__vs__neg__standard_score" # (variable name from protocol config)
    RANK_VS_NEG_RAW = "rank_signal__vs__neg__pvalue"

    # Raw data (up-regulated sample compared to negative control distribution)
    PVALUE_UP_VS_NEG_RAW = "signal_up_vs__neg__p_value" # (variable name from protocol config)
    SS_UP_VS_NEG_RAW = "signal_up_vs__neg__standard_score" # (variable name from protocol config)
    RANK_UP_VS_NEG_RAW = "rank_signal_up_vs__neg__pvalue"
    
    
    # Gaussian process normalized data (sample compared to sample distribution)
    PVALUE_VS_S__N__GP = "best_gp_normalized_signal__vs__s__p_value" # (variable name from protocol config)
    SS_VS_S__N__GP = "best_gp_normalized_signal__vs__s__standard_score" # (variable name from protocol config)
    RANK__N__GP = "rank__best_gp_normalized_signal__pvalue_s"

    # Gaussian process normalized data (sample compared to negative control distribution)
    PVALUE_VS_NEG__N__GP = "best_gp_normalized_signal__vs__neg__p_value" # (variable name from protocol config)
    SS_VS_NEG__N__GP = "best_gp_normalized_signal__vs__neg__standard_score" # (variable name from protocol config)
    RANK_VS_NEG__N__GP = "rank__best_gp_normalized_signal__vs__neg__pvalue"
    

    # Realtime-GLO normalized data (sample compared to sample distribution)
    PVALUE_VS_S__N__RTGLO = "net_fret__div__rtglo_signal__vs__s__p_value" # (variable name from protocol config)
    SS__N__RTGLO = "net_fret__div__rtglo_signal__vs__s__standard_score" # (variable name from protocol config)
    RANK__N__RTGLO = "rank__rtglo_normalized_signal__pvalue_s"
    
    # Realtime-GLO normalized data (sample compared to negative control distribution)
    PVALUE_VS_NEG__N__RTGLO = "net_fret__div__rtglo_signal__vs__neg__p_value" # (variable name from protocol config)
    SS_NEG_N__RTGLO = "net_fret__div__rtglo_signal__vs__neg__standard_score" # (variable name from protocol config)
    RANK_VS_NEG__N__RTGLO = "rank__rtglo_normalized_signal__vs__neg__pvalue"
    

    # Realtime-GLO and then Gaussian process normalized data (sample compared to sample distribution)
    PVALUE_VS_S__N__RTGLO_GP = "rt_glo__best_gp_normalized_signal__vs__s__p_value" # (variable name from protocol config)
    SS__N__RTGLO_GP = "rt_glo__best_gp_normalized_signal__vs__s__standard_score" # (variable name from protocol config)
    RANK__N__RTGLO_GP = "rank__rtglo_gp_normalized_signal__pvalue_s"

    # Realtime-GLO data only (sample compared to sample distribution)
    PVALUE_VS_S__RTGLO = "rtglo_signal__vs__s__p_value" # RT-GLO only !!! (variable name from protocol config)
    SS_RTGLO = "rtglo_signal__vs__s__standard_score"  # RT-GLO only !!! (variable name from protocol config)
    RANK_RTGLO = "rank__raw_signal__pvalue_s" # RT-GLO only !!!

    IS_HIT_TAG = "is_hit___{}"

    aggregated_dataframe = my_run.merger_summarize_statistical_significance(
        replicate_defining_column="meta_SEQUENCE",
        data_tag_readouts_to_aggregate=["net_fret", "net_fret__normalized_by__best_gp", "net_fret__div__rtglo_signal__vs__s__p_value"],
        data_tag_pvalues_to_aggregate=[PVALUE_VS_S__N__GP, PVALUE_VS_NEG__N__GP, PVALUE_VS_S__RTGLO, PVALUE_VS_S_RAW, PVALUE_VS_NEG_RAW, PVALUE_VS_S__N__RTGLO, PVALUE_VS_S__N__RTGLO_GP, PVALUE_UP_VS_NEG_RAW, PVALUE_VS_NEG__N__GP, PVALUE_VS_NEG__N__RTGLO],
        data_tag_standard_scores_to_aggregate=[SS_VS_S_RAW, SS_VS_NEG_RAW, SS_VS_S__N__GP, SS_VS_NEG__N__GP, SS__N__RTGLO, SS__N__RTGLO_GP, SS_RTGLO, SS_NEG_N__RTGLO]
    )
    

    aggregated_dataframe = my_run.merger_rank_samples(
        replicate_defining_column="meta_SEQUENCE",
        ranking_column=PVALUE_VS_S__N__RTGLO,
        rank_column_name=RANK__N__RTGLO,
        rank_threshold=20,
        is_hit_by_rank_column_name=IS_HIT_TAG.format(RANK__N__RTGLO),
        value_threshold=0.001,
        is_hit_by_value_column_name=IS_HIT_TAG.format(PVALUE_VS_S__N__RTGLO))

    aggregated_dataframe = my_run.merger_rank_samples(
        replicate_defining_column="meta_SEQUENCE",
        ranking_column=PVALUE_VS_S__N__GP,
        rank_column_name=RANK__N__GP,
        rank_threshold=20,
        is_hit_by_rank_column_name=IS_HIT_TAG.format(RANK__N__GP),
        value_threshold=0.001,
        is_hit_by_value_column_name=IS_HIT_TAG.format(PVALUE_VS_S__N__GP))

    aggregated_dataframe = my_run.merger_rank_samples(
        replicate_defining_column="meta_SEQUENCE",
        ranking_column=PVALUE_VS_S_RAW,
        rank_column_name=RANK_RAW,
        rank_threshold=20,
        is_hit_by_rank_column_name=IS_HIT_TAG.format(RANK_RAW),
        value_threshold=0.001,
        is_hit_by_value_column_name=IS_HIT_TAG.format(PVALUE_VS_S_RAW))

    aggregated_dataframe = my_run.merger_rank_samples(
        replicate_defining_column="meta_SEQUENCE",
        ranking_column=PVALUE_VS_S__N__RTGLO_GP,
        rank_column_name=RANK__N__RTGLO_GP,
        rank_threshold=20,
        is_hit_by_rank_column_name=IS_HIT_TAG.format(RANK__N__RTGLO_GP),
        value_threshold=0.001,
        is_hit_by_value_column_name=IS_HIT_TAG.format(PVALUE_VS_S__N__RTGLO_GP))

    # Add rankings based on position relative to negative controls distribution
    # - Negative effect on Prpc
    #     - not normalised
    aggregated_dataframe = my_run.merger_rank_samples(
       replicate_defining_column="meta_SEQUENCE",
        ranking_column=PVALUE_VS_NEG_RAW,
        rank_column_name=RANK_VS_NEG_RAW,
        rank_threshold=20,
        is_hit_by_rank_column_name=IS_HIT_TAG.format(RANK_VS_NEG_RAW),
        value_threshold=0.001,
        is_hit_by_value_column_name=IS_HIT_TAG.format(PVALUE_VS_NEG_RAW))
    #     - normalised by GP
    aggregated_dataframe = my_run.merger_rank_samples(
        replicate_defining_column="meta_SEQUENCE",
        ranking_column=PVALUE_VS_NEG__N__GP,
        rank_column_name=RANK_VS_NEG__N__GP,
        rank_threshold=20,
        is_hit_by_rank_column_name=IS_HIT_TAG.format(RANK_VS_NEG__N__GP),
        value_threshold=0.001,
        is_hit_by_value_column_name=IS_HIT_TAG.format(PVALUE_VS_NEG__N__GP))
    #     - normalised by RT-Glo
    aggregated_dataframe = my_run.merger_rank_samples(
        replicate_defining_column="meta_SEQUENCE",
        ranking_column=PVALUE_VS_NEG__N__RTGLO,
        rank_column_name=RANK_VS_NEG__N__RTGLO,
        rank_threshold=20,
        is_hit_by_rank_column_name=IS_HIT_TAG.format(RANK_VS_NEG__N__RTGLO),
        value_threshold=0.001,
        is_hit_by_value_column_name=IS_HIT_TAG.format(PVALUE_VS_NEG__N__RTGLO))

    # - Positive effect on Prpc
    #     - not normalised
    aggregated_dataframe = my_run.merger_rank_samples(
        replicate_defining_column="meta_SEQUENCE",
        ranking_column=PVALUE_UP_VS_NEG_RAW,
        rank_column_name=RANK_UP_VS_NEG_RAW,
        rank_threshold=20,
        is_hit_by_rank_column_name=IS_HIT_TAG.format(RANK_UP_VS_NEG_RAW),
        value_threshold=0.001,
        is_hit_by_value_column_name=IS_HIT_TAG.format(PVALUE_UP_VS_NEG_RAW))
        
    
        

    # Decide on replicates by: meta_SEQUENCE
    # Future (For gene wise aggregation): Decide on genes by: meta_FIRST_TARGET_GENE_ID

    # Define what columns are taken from the picklist file!
    # For Bei's Endocytome data set, the picklist column names / variable names differ slightly compared to Valeria's data set.
    # This might need updating for future data sets.
    if "Bei" in i_run:
        aggregated_dataframe = my_run.merger_add_data_from_data_frame(
            replicate_defining_column="meta_SEQUENCE",
            columns=["meta_ALL_TARGET_GENES", "meta_CAT_NO", "meta_FIRST_GENE_DESCRIPTION", "meta_FIRST_TARGET_GENE_ID", "meta_FIRST_TARGET_GENE_SYMBOL", "meta_LIBRARY_ID", "meta_NUM_TARGET_GENES", "meta_SEQUENCE", "meta_SMF_SAMPLE_ID", "meta_SOURCE_2DBARCODE","source_plate_name", "plate_name"])
    else:
        aggregated_dataframe = my_run.merger_add_data_from_data_frame(
            replicate_defining_column="meta_SEQUENCE",
            columns=["GENE_SYMBOL", "GENE_ID", "KNOCKDOWN_TYPE", "plate_name"])


    # Write data to .csv files
    #   - not aggregated data
    my_run.data_frame.to_csv(my_run.config_data["write"]["data_frame_all_path"],
                             columns=sorted(my_run.data_frame_samples.columns.values))
	
	#   - aggregated around siRNAs (meta_SEQUENCE)
    # Define sorting of rows for the aggregated file.
    ad = aggregated_dataframe
    # ad = ad.sort([PVALUE_VS_NEG__N__GP], ascending=[1])
    ad = ad.sort_values([PVALUE_VS_NEG__N__GP], axis=0, ascending=True)
	# Write csv, sorting columns in alphanumerical increasing order of column names
    ad.to_csv(my_run.config_data["write"]["aggregated_path"], columns=sorted(ad.columns.values))


#import pdb; pdb.set_trace()
