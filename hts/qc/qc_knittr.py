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
        qc_description, qc_calculation = perform_qc(qc_method_name)
        # 3. Apply filter
        if "threshold" in i_qc_characteristics:
            qc_decision = evaluate_qc(qc_result, i_qc_characteristics['threshold'])
            chunk = "\n".join([qc_subset, qc_calculation, qc_decision])
        else:
            chunk = "\n".join([qc_subset, qc_calculation])

        # Later on, you can make this line more complicated.
        wrapped_chunk = wrap_knittr_chunk(chunk=chunk, echo=True, eval=True)
        qc_report_data[i_qc] = "\n".join(["### QC " + qc_method_name, qc_description, wrapped_chunk])

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
            LOG.info("i_qc: {}".format(i_qc))
            fh.write(i_qc_knittr + "\n\n")

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
library(reshape2)
require(gridExtra)""".format(qc_helper_methods)
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


def chessboard_pattern():

    description = '''
Evolution of mean value over plates for odd and even row and columns.
'''

    calculation = '''
d = ddply(d, 1, transform, row_type = c("even", "odd")[(x2 %% 2) + 1])
d = ddply(d, 1, transform, column_type = c("even", "odd")[(x1 %% 2) + 1])


d_summary = ddply(d, .(x3, x3_plate_name, row_type), summarize, y_mean =mean(y), y_sd =sd(y))
p = ggplot(d_summary, aes(x3_plate_name, y_mean))
p = p + geom_errorbar(aes(ymin=y_mean-y_sd, ymax=y_mean+y_sd), width=.05)
p = p + geom_point(size = 2, aes(color = row_type))
p = p + scale_colour_brewer(palette="Set1")
p = beautifier(p)

d_summary = ddply(d, .(x3, x3_plate_name, column_type), summarize, y_mean =mean(y), y_sd =sd(y))
p2 = ggplot(d_summary, aes(x3_plate_name, y_mean))
p2 = p2 + geom_errorbar(aes(ymin=y_mean-y_sd, ymax=y_mean+y_sd), width=.05)
p2 = p2 + geom_point(size = 2, aes(color = column_type))
p2 = p2 + scale_colour_brewer(palette="Set1")
p2 = beautifier(p2)

grid.arrange(p, p2, ncol=2)'''

    return description, calculation



def compare_plate_replicates():

    description = '''
Plot replicate values against each other.'''

    calculation = '''
d_tmp_1 = subset(d, sample_replicate == 1)
d_tmp_2 = subset(d, sample_replicate == 2)
d_tmp_1$y_replicate_1 = d_tmp_1$y
d_tmp_1$y_replicate_2 = d_tmp_2$y

p = ggplot(d_tmp_1, aes(y_replicate_1, y_replicate_2))
p = p + geom_point(size = 0.8, color = "brown", alpha = 0.3)
p = p + geom_smooth(method=lm,   # Add linear regression lines
                se=FALSE,    # Don't add shaded confidence region
                fullrange=T, colour="grey")
p = p + facet_wrap( ~x3_plate_name, ncol=2) + scale_colour_brewer(palette="Set1")
#plot.new()
#legend('topleft', legend = lm_eqn(lm(y_replicate_1 ~ y_replicate_2, d_tmp_1)), bty = 'n') # Problem printing.
beautifier(p)'''

    return description, calculation



def heat_map():

    description = '''
Heatmap of well wise values.
'''

    calculation = '''
tag = "remove_tags_from_this_function"
tile_plot_x1x2x3(d, "y", tag, FALSE)'''

    return description, calculation



def kolmogorov_smirnov():

    description = '''
Kolmogorov–Smirnov test: Do sample and negative control stem from the same distribution (H0) or not (H1)?
'''

    calculation = '''
calculate_ks <- function(neg, x3_plate_name) {
 neg_y = d[d$sample == neg & d$x3_plate_name == x3_plate_name, "y"]
 sample_y = d[d$sample_type == 's' & d$x3_plate_name == x3_plate_name, "y"]
 my_ks = ks.test(neg_y, sample_y, alternative = c("two.sided"), exact = TRUE)
 return(my_ks[['p.value']])
}

my_grid = expand.grid(neg = unique(d[d$sample_type=='neg', 'sample']), x3_plate_name = unique(d$x3_plate_name))
d_ks = adply(my_grid, 1, transform, pvalue_ks = calculate_ks(neg, x3_plate_name))
d_ks$log10_pvalue_ks = log10(d_ks$pvalue_ks)

p = ggplot(d_ks, aes(x3_plate_name, log10_pvalue_ks))
p = p + geom_point()
p = p + geom_hline(yintercept=-2)
p = p + facet_wrap( ~neg, ncol=2)
beautifier(p)'''

    return description, calculation


def kolmogorov_smirnov_estimated():

    description = '''
Kolmogorov–Smirnov test: Does the negative control stem from the same (estimated) distribution as the sample (H0) or not (H1)?
'''

    calculation = '''
calculate_ks_estimate <- function(neg, x3_plate_name) {
 neg_y = d[d$sample == neg & d$x3_plate_name == x3_plate_name, "y"]
 # The maximum likelihood estimators for mu (sigma) of a Gaussian is the mean (the sample standard deviation = sd in R.)
 sample_y = d[d$sample_type == 's' & d$x3_plate_name == x3_plate_name, "y"]
 my_ks = ks.test(neg_y, 'pnorm', mean(sample_y), sd(sample_y), exact = TRUE)
 return(my_ks[['p.value']])
}

my_grid = expand.grid(neg = unique(d[d$sample_type=='neg', 'sample']), x3_plate_name = unique(d$x3_plate_name))
d_ks = adply(my_grid, 1, transform, pvalue_ks = calculate_ks_estimate(neg, x3_plate_name))
d_ks$log10_pvalue_ks = log10(d_ks$pvalue_ks)

p = ggplot(d_ks, aes(x3_plate_name, log10_pvalue_ks))
p = p + geom_point()
p = p + geom_hline(yintercept=-2)
p = p + facet_wrap( ~neg, ncol=2)
beautifier(p)'''

    return description, calculation



def mean_value_across_plates():

    description = '''
Evolution of mean value across plates.
'''

    calculation = '''
d_summary = ddply(d, .(sample_type, x3, x3_plate_name), summarize, y_mean =mean(y), y_sd =sd(y))

p = ggplot(d_summary, aes(x3_plate_name, y_mean))
p = p + geom_errorbar(aes(ymin=y_mean-y_sd, ymax=y_mean+y_sd), width=.1)
p = p + geom_point(size = 2, aes(color = sample_type))
p = p + facet_wrap( ~sample_type, ncol=4) + scale_colour_brewer(palette="Set1")
beautifier(p)'''



def shapiro_wilk_normality_test():

    description = '''
Shapiro-Wilk Normality Test: Does the negative control stem from a normal distribution? Does the sample stem from a normal distribution?
'''

    calculation = '''
calculate_sw <- function(data) {
 my_ks = shapiro.test(data)
 return(my_ks[['p.value']])
}

d_sw = ddply(d, .(x3_plate_name, x3, sample, sample_type), summarize, log10_pvalue_sw = log10(calculate_sw(y)))

p = ggplot(d_sw, aes(x3_plate_name, log10_pvalue_sw))
p = p + geom_point()
p = p + geom_hline(yintercept=-2)
p = p + facet_wrap( ~sample, ncol=2)
beautifier(p)'''

    return description, calculation



def ssmd():

    description = '''
SSMD (Definition according to [wikipedia](https://en.wikipedia.org/wiki/Strictly_standardized_mean_difference "Wikipedia: SSMD"))
$$ \\rm{ssmd} = \\frac{\mu_\\rm{pos} - \mu_\\rm{neg}}{\\sigma_\\rm{pos}^2 + \\sigma_\\rm{neg}^2}, $$
where pos is the positive control, and neg are positive is the negative control.
The displayed cut-off values assume a moderate control. Strong controls require smaller ssmd values.
'''

    calculation = '''
d_summary = ddply(d, .(sample, sample_type, x3, x3_plate_name), summarize, y_mean =mean(y), y_sd =sd(y))

calculate_ssmd <- function(neg, pos, x3_plate_name) {
 neg_mean = d_summary[d_summary$sample == neg & d_summary$x3_plate_name == x3_plate_name, "y_mean"]
 neg_sd = d_summary[d_summary$sample ==neg & d_summary$x3_plate_name == x3_plate_name, "y_sd"]
 pos_mean = d_summary[d_summary$sample == pos & d_summary$x3_plate_name == x3_plate_name, "y_mean"]
 pos_sd = d_summary[d_summary$sample == pos & d_summary$x3_plate_name == x3_plate_name, "y_sd"]
 ssmd = (pos_mean - neg_mean) / sqrt(pos_sd^2 + neg_sd^2)
 return(ssmd)
}

my_grid = expand.grid(neg = unique(d[d$sample_type=='neg', 'sample']),  pos = unique(d[d$sample_type=='pos', 'sample']), x3_plate_name = unique(d$x3_plate_name))
d_ssmd = adply(my_grid, 1, transform, ssmd = calculate_ssmd(neg, pos, x3_plate_name))
print(d_ssmd)

p = ggplot(d_ssmd, aes(x3_plate_name, ssmd))
p = p + geom_point(size = 2, aes(color = neg))
p = p + geom_hline(yintercept=-2) + geom_hline(yintercept=-1) + geom_hline(yintercept=-0.5)
p = p + annotate("text", x = d_ssmd$x3_plate_name[1], y=c(-3, -1.5, -0.75, 0), label = c("excellent", "good", "inferior", "poor"))
p = p + facet_wrap( ~pos, ncol=2) + scale_colour_brewer(palette="Set1")
beautifier(p)'''

    return description, calculation


def z_factor():

    description = '''
The estimated z-factor is calculated as:
$$ z_{\\rm{factor}} = 1 - \\frac{3\cdot(\sigma_\\rm{s} + \sigma_\\rm{neg})}{|\mu_\\rm{s} - \mu_\\rm{neg}|} $$,
where s is the sample, and neg the negative control."
(Described e.g. on [wikipedia](https://en.wikipedia.org/wiki/Z-factor "Wikipedia: Z-factor") or in Birmingham et al, Nature, (2009) "Statistical methods for analysis of high throughput RNA interference screens"
)
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


def z_dash_factor():

    description = '''
$$ z_{\\rm{dash_factor}} = 1 - \\frac{3\cdot(\sigma_\\rm{hc} + \sigma_\\rm{lc})}{|\mu_\\rm{hc} - \mu_\\rm{lc}|} $$,
where hc is the high value control, and lc the low value control. The order of controls is irrelevant in the equation.
(Described e.g. in Birmingham et al, Nature, (2009) "Statistical methods for analysis of high throughput RNA interference screens": "A potential issue in using the Z' factor as a measure of assay resolution is that it is possible to generate a high Z' factor using a very strong positive control, which may not realistically represent more moderate screening positives. This issue is of special con- cern for RNAi screens, in which weak effects might be biologically meaningful and in which the signal-to-background ratio can be of lower magnitude than in small-molecule screens (Supplementary Table 1). Thus, researchers are advised whenever possible to use positive controls that are similar in strength to the hits they antici- pate finding. It may also be necessary to adjust Z'-factor quality guidelines for RNAi screens; we have found that assays with Z' fac- tors of zero or greater have been successful in identifying validated hits when we screened library plates in duplicate or triplicate.")
'''

    calculation = '''
d_summary = ddply(d, .(sample, sample_type, x3, x3_plate_name), summarize, y_mean =mean(y), y_sd =sd(y))

calculate_z_dash_factor <- function(neg, pos, x3_plate_name) {
 neg_mean = d_summary[d_summary$sample == neg & d_summary$x3_plate_name == x3_plate_name, "y_mean"]
 neg_sd = d_summary[d_summary$sample ==neg & d_summary$x3_plate_name == x3_plate_name, "y_sd"]
 pos_mean = d_summary[d_summary$sample == pos & d_summary$x3_plate_name == x3_plate_name, "y_mean"]
 pos_sd = d_summary[d_summary$sample == pos & d_summary$x3_plate_name == x3_plate_name, "y_sd"]
 z_dash_factor = 1 - 3*(neg_sd + pos_sd) / abs (neg_mean - pos_mean)
 return(z_dash_factor)
}

my_grid = expand.grid(neg = unique(d[d$sample_type=='neg', 'sample']),  pos = unique(d[d$sample_type=='pos', 'sample']), x3_plate_name = unique(d$x3_plate_name))
d_z_dash_factor = adply(my_grid, 1, transform, z_dash_factor = calculate_z_dash_factor(neg, pos, x3_plate_name))

p = ggplot(d_z_dash_factor, aes(x3_plate_name, z_dash_factor))
p = p + geom_point(size = 2, aes(color = neg))
p = p + geom_hline(yintercept=0) + geom_hline(yintercept=0.5)
p = p + annotate("text", x = d_z_dash_factor$x3_plate_name[1], y=c(10, 0.25, -10), label = c("very good", "acceptable", "unacceptable"))
p = p + facet_wrap( ~pos, ncol=2) + scale_colour_brewer(palette="Set1")
beautifier(p)
'''

    return description, calculation


def smoothed_histogram():

    description = '''
Smoothed histogram to visualise the overlap of value densities per sample type.
'''

    calculation = '''
p = ggplot(d, aes(y, colour=sample)) + geom_density()
p = p + facet_wrap( ~x3_plate_name, ncol=2) + scale_colour_brewer(palette="Set1")
beautifier(p)'''

    return description, calculation


