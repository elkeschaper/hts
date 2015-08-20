# (C) 2015 Elke Schaper

"""
    :synopsis: ``quality_control`` implementes all methods connected to the
    quality control of a high throughput screening experiment.
    qc_knittr implements knittr specific methods.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import datetime
import logging
import os
import re
import sys

from hts.readout import readout, readout_dict

LOG = logging.getLogger(__name__)

PATH = '/Users/elkeschaper/Downloads/'


def report_qc(run, qc_result_path, qc_helper_methods, meta_data = None, *args, **kwargs):
    """
    Run QC tasks, and combine the result to a report.

    """

    if not os.path.exists(qc_result_path):
        LOG.warning("Creating QC report result path: {}".format(qc_result_path))
        os.makedirs(qc_result_path)

    path_knittr_data = os.path.join(qc_result_path, "data.csv")
    path_knittr_file = os.path.join(qc_result_path, "qc_report.Rmd")

    # Create header info and environment snippets
    header, environment, data_loader = knittr_header_setup(qc_helper_methods = qc_helper_methods, path_knittr_data = path_knittr_data, meta_data = meta_data)


    # Create QC snippets
    qc_report_data = {}
    for i_qc, i_qc_characteristics in kwargs.items():
        LOG.info("i_qc: {}".format(i_qc))
        try:
            qc_method_name = i_qc_characteristics['method']
        except:
            LOG.warning("No key 'method' in i_qc_characteristics: {}".format(i_qc_characteristics))
        # 1. Create subset of data
        if "filter" in i_qc_characteristics:
            qc_subset = knittr_subset(i_qc_characteristics['filter'])
        else:
            qc_subset = knittr_subset(None)
            LOG.info("No key 'filter' in i_qc_characteristics: {}".format(i_qc_characteristics))
        # 2. Create QC code
        qc_description, qc_result = perform_qc(qc_method_name)
        # 3. Apply filter
        if "threshold" in i_qc_characteristics:
            qc_decision = evaluate_qc(qc_result, i_qc_characteristics['threshold'])
        else:
            qc_decision = ""

        # Later on, you can make this line more complicated.
        qc_report_data[i_qc] = "### QC " + qc_method_name + "\n" + qc_description + "\n" + wrap_knittr_chunk(chunk="\n".join([qc_subset, qc_result, qc_decision]), echo=True, eval=True)

    #import pdb; pdb.set_trace()

    # QC report
    # 1. Write the start of a RMarkdown file,
    # 2. Add each section
    # 3. Add end of RMarkdown file
    # 4. Save and return results.
    with open(path_knittr_file, "w") as fh:
        fh.write(header)
        fh.write(environment)
        fh.write(data_loader)
        fh.write("## QC\n")
        for i_qc, i_qc_knittr in qc_report_data.items():
            fh.write(i_qc_knittr)

    return None


def perform_qc(method_name, *args, **kwargs):
    """
    Perform QC `method_name` with parameter *args and **kwargs, and return result.

    """

    try:
        qc_method = getattr(sys.modules[__name__], method_name)
    except:
        raise ValueError("method_name: {} not defined in qc_knittr.py".format(method_name))
    return qc_method(*args, **kwargs)



def knittr_header_setup(qc_helper_methods, path_knittr_data, meta_data = None, original_data_frame = "d_all", output= "html_document"):
    """ Create knittr markdown file header and setup.

   Create knittr markdown file header and setup.

    Args:
        path_qc_methods (str): Path to external R methods file
        path_data (str): Path to data file


    Returns:
        header (str): Knittr markdown file header
        environment (str): Knittr markdown environment setter
        data_loader (str): Knittr markdown data loader

    """

    header ="""
---
title: "QC report"
author: "Neuropathology USZ & Vital-IT, Swiss Institute of Bioinformatics"
date: "{}"
output: "{}"
---
""".format(str(datetime.date.today()),output)

    if meta_data:
        header += """
## HTS Run general info

| Overview |
|:-----------|:------------|\n"""

        header += "\n".join(["| {} | {}".format(i[0], i[1]) for i in  meta_data])


    environment_commands = """
rm(list = ls(all = TRUE))
gc()
source("{}")
library(reshape2)""".format(qc_helper_methods)
    environment="\n\nCreate environment:\n" + wrap_knittr_chunk(chunk=environment_commands, echo=False, eval=True)

    data_loader_commands="""
path = "{}"
{} = read.csv(path, sep=",", header = TRUE)""".format(path_knittr_data, original_data_frame)
    data_loader="\nLoad data:\n" + wrap_knittr_chunk(chunk=data_loader_commands, echo=False, eval=True)

    return header, environment, data_loader

################ wrap knittr chunk ###################

def wrap_knittr_chunk(chunk, echo = True, eval=True):

    if echo:
        echo_tag = "echo=TRUE"
    else:
        echo_tag = "echo=FALSE"
    if eval:
        eval_tag = "eval=TRUE"
    else:
        eval_tag = "eval=FALSE"

    return "```{{r, {}, {}}}\n{}\n```\n".format(echo_tag, eval_tag, chunk)


################ Data subsetting #####################


def knittr_subset(subset_requirements, original_data_frame = "d_all", new_data_frame = "d"):
    """ Create knittr code to subset the data.

   Create knittr code to subset the data.

    Args:
        subset_requirements (dict): For each requirement, key, values and negated need to be supplied.
        original_data_frame (str): Name of the original data frame.
        new_data_frame (str): Name of the new data frame.

    Returns:
        subset (str): Knittr code subsetting

    """

    if subset_requirements == {}:
        LOG.info("subset_requirements is empty.")
        return ""

    knittr_requirements = []
    for knittr_key, i_s in subset_requirements.items():
        if type(i_s["values"]) == list:
            knittr_equal = "%in%"
            knittr_value = "c('{}')".format("', '".join(i_s["values"]))
        else:
            knittr_equal = "=="
            knittr_value = "'{}'".format(i_s["values"])
        if i_s["negated"] == True:
            knittr_negator = "not"
        else:
            knittr_negator = ""
        knittr_requirements.append(" ".join([knittr_negator, knittr_key, knittr_equal, knittr_value]))


    subset = "{} = subset({}, {})".format(new_data_frame, original_data_frame, " & ".join(knittr_requirements))
    return subset


################ QC methods ####################




def z_factor():


    description = '''
This QC is largely similar to SSMD and others.

Birmingham et al, Nature, (2009) "Statistical methods for analysis of high throughput RNA interference screens"
$$ z_{factor} = 1 - \frac{3\cdot(\sigma_s + \sigma_c)}{|\mu_s - \mu_c|} $$,
where s is the sample, and c the negative control."
'''

    calculation = '''
d_summary = ddply(d, .(sample, sample_type, x3, x3_plate_name), summarize, y_mean =mean(y), y_sd =sd(y))

calculate_z_factor <- function(neg, x3_plate_name) {
 neg_mean = d_summary[d_summary$sample == neg & d_summary$x3_plate_name == x3_plate_name, "y_mean"]
 neg_sd = d_summary[d_summary$sample ==neg & d_summary$x3_plate_name == x3_plate_name, "y_sd"]
 s_mean = mean(d[d$sample_type == "s" & d$x3_plate_name == x3_plate_name, "y"])
 s_sd = sd(d[d$sample_type == "s" & d$x3_plate_name == x3_plate_name, "y"])
 z_factor = 1 - 3*(neg_sd + s_sd) / abs (neg_mean - s_mean)
 return(z_factor)
}

my_grid = expand.grid(neg = unique(d[d$sample_type=="neg", "sample"]), x3_plate_name = unique(d$x3_plate_name))
d_z_factor = adply(my_grid, 1, transform, z_factor = calculate_z_factor(neg, x3_plate_name))

p = ggplot(d_z_factor, aes(x3_plate_name, z_factor))
p = p + geom_point(size = 2, aes(color = neg))
p = p + geom_hline(yintercept=0) + geom_hline(yintercept=0.5)
p = p + annotate("text", x = d_z_factor$x3_plate_name[1], y=c(10, 0.25, -10), label = c("very good", "acceptable", "unacceptable"))
p = p + scale_colour_brewer(palette="Set1")
beautifier(p)'''

    return description, calculation