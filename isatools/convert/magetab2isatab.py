import pandas as pd
from isatools import isatab
import os
import logging
from isatools import magetab

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def convert(input_idf_path, output_path, technology_type=None, measurement_type=None):
    """ Converter for MAGE-TAB to ISA-Tab
    :param source_idf_fp: File descriptor of input IDF file
    :param output_path: Path to directory to write output ISA-Tab files to
    """
    ISA = magetab.parse_idf(input_idf_path, technology_type=technology_type, measurement_type=measurement_type)
    isatab.dump(ISA, output_path=output_path, skip_dump_tables=True)
    for sdrf_file in [x.value for x in ISA.studies[0].comments if x.name == "SDRF File"]:
        if isinstance(sdrf_file, str):
            study_df, assay_df = magetab.split_tables(sdrf_path=os.path.join(os.path.dirname(input_idf_path),
                                                                             sdrf_file))
            study_df.columns = study_df.isatab_header
            assay_df.columns = assay_df.isatab_header
            # write out ISA table files
            print("Writing s_{0} to {1}".format(os.path.basename(sdrf_file), output_path))
            with open(os.path.join(output_path, "s_" + os.path.basename(sdrf_file)), "w") as s_fp:
                study_df.to_csv(path_or_buf=s_fp, mode='a', sep='\t', encoding='utf-8', index=False)
            print("Writing a_{0} to {1}".format(os.path.basename(sdrf_file), output_path))
            with open(os.path.join(output_path, "a_" + os.path.basename(sdrf_file)), "w") as a_fp:
                assay_df.to_csv(path_or_buf=a_fp, mode='a', sep='\t', encoding='utf-8', index=False)
    print("Writing {0} to {1}".format("i_investigation.txt", output_path))


def get_investigation_title(line, ISA):
    split_line = [x for x in line.split('\t') if x != '']
    if len(split_line) > 1:
        value = split_line[1]
        ISA.title = value


def get_first_node_index(header):
    sqaushed_header = list(map(lambda x: magetab.squashstr(x), header))
    nodes = ["samplename", "extractname", "labeledextractname", "hybridizationname", "assayname"]
    for node in nodes:
        try:
            index = sqaushed_header.index(node)
            return index
        except ValueError:
            pass
