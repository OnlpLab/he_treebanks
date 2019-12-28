import pandas as pd
import json
import csv
import re
import numpy as np
from tqdm import tqdm
import argparse


def add_token_numbers_to_file(filepath, tokenized_filepath):
    """based on yochai's code"""
    # original format + original_token column
    columns = ['ID', 'FORM', 'LEMMA', 'UPOS', 'XPOS', 'FEATS', 'TOKEN_NUMBER']

    current_token = 0
    num_of_broken_tokens = 0
    with open(filepath, 'r') as conll_file, open(tokenized_filepath, 'wt') as tokenized_file:
        # create similiar tsv format with the new columns
        tokenized_file.write('\t'.join(columns) + '\n')
        # skip header of original file
        conll_file.readline()
        # iterate over the original file, keep comments and blanks and update original token accordingly
        for original_line in conll_file:
            # reset the original token (to one) when reaching new sentence (newline)
            if original_line == '\n':
                current_token = 0
            # write comments and newlines as is in the new file
            if not original_line[0].isdigit():
                tokenized_line = original_line.strip()
            else:
                tok_id = original_line.split('\t')[0]
                # assign original token (tokenized if one morpheme, splitted if multiple morphemes)
                # handle broken tokens
                if num_of_broken_tokens > 0:
                    num_of_broken_tokens -= 1
                    tokenized_line = original_line.strip() + '\t' + str(current_token)

                else:
                    # handle single-morpheme tokens (denote with _ instead of original token)
                    if not '-' in original_line:
                        current_token += 1
                        tokenized_line = original_line.strip() + '\t' + str(current_token)

                    # handle multi-morpheme tokens (denote with _ instead of original token)
                    elif '-' in tok_id:
                        try:
                            beg, end = tok_id.split('-')
                        except ValueError:
                            raise Exception(tok_id)
                        num_of_broken_tokens = int(end) - int(beg) + 1

                        current_token += 1
                        tokenized_line = original_line.strip() + '\t' + '_'
            tokenized_file.write(tokenized_line + '\n')
    return tokenized_filepath


def create_xpos(row, pos_tags):
    if pd.notna(row["UPOS"]):
        if row["UPOS"] == "_":
            return "_"
        else:
            upos = row["UPOS"]
            tag = pos_tags[upos]
            xpos = tag["default"]
            if tag["exceptions"]:
                for exception in tag["exceptions"]:
                    condition_met = 1
                    for condition in exception[:-1]:
                        if condition[0] == "FORM":
                            if condition[1] in row["FORM"]:
                                condition_met += 1
                        if condition[0] == "LEMMA":
                            if row["LEMMA"] in condition[1]:
                                condition_met += 1
                        if condition[0] == "FEATS":
                            if condition[1] in row["FEATS"]:
                                condition_met += 1
                    if condition_met == len(exception):
                        xpos = exception[-1]
            return xpos
    else:
        return None


def convert_features(row, features):
    converted_features = []
    if pd.notna(row["FEATS"]):
        if row["FEATS"] == "_":
            return "_"
        else:
            for row_feature in row["FEATS"].split("|"):
                key = row_feature.split("=")[0]
                try:
                    value = row_feature.split("=")[1]
                except IndexError:
                    pass
                    # raise Exception([row["ID"], row["FEATS"], row["XPOS"]])
                if key in features:
                    new_name = features[key]["spmrl_name"]
                    if value in features[key]["single_values"]:
                        new_value = features[key]["single_values"][value]
                        converted_features.append(f"{new_name}={new_value}")
                    elif "multiple_values" in features[key].keys():
                        converted_features.append(features[key]["multiple_values"][value])
                    else:
                        print("The feature {} does not have a value {}. If this is not a typo, "
                              "please update ud_to_spmrl.json".format(features[key]["spmrl_name"], value))
        return "|".join(converted_features)


def create_index(num):
    try:
        return int(num)-1
    except ValueError:
        return ""

def output_to_file(df, output_fp):
    prev_token_num = 0
    with open(output_fp, "w") as f:
        for i, row in df.iterrows():
            try:
                if not str(row["index"]).isdigit():
                    f.write("\n")
                else:
                    output = "\t".join([str(k) for k in row]) + "\n"
                    if "nan" not in output:
                        prev_token_num = row["TOKEN_NUMBER"]
                        f.write(output)
                    else:
                        output = "{}\t{}\t\"\t\"\tyyQUOT\tyyQUOT\t_\t{}\n".format(row["index"], row["ID"], (int(prev_token_num)+1))
                        f.write(output)
            except:
                raise Exception(row["index"])
        f.write("\n")

def main(df, conversion_json, include_upos=False):
    with open(conversion_json, "r") as conv:
        conversion_rules = json.load(conv)
        pos_tags = conversion_rules["POS"]
        features = conversion_rules["FEATS"]

    #add token numbers
    # df = set_tokens(df)
    # change part of speech
    df["XPOS"] = df.apply(lambda x: create_xpos(x, pos_tags), axis=1)
    # change features
    df["FEATS"] = df.apply(lambda x: convert_features(x, features), axis=1)
    # get rid of token information lines
    df = df[~df['ID'].str.contains("\d+-\d+", na=False)]
    # adding index column
    df['index'] = df["ID"].apply(create_index)
    # remove underscores
    df["FORM"] = df["FORM"].apply(lambda x: x.replace("_", "") if type(x) == str else x)
    if not include_upos:
        # replace upos col by xpos
        df = df[["index", "ID", "FORM", "LEMMA", "XPOS", "XPOS", "FEATS", "TOKEN_NUMBER"]]
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="conversion from UD annotation to SPMRL (YAP readable format).")

    parser.add_argument("--ud_filepath", help="Obligatory - path to file with manually tagged dataset (in UD)")
    parser.add_argument("--conversion_rules", default="./ud_to_spmrl.json", help="path to json file with conversion rules.")

    argv = parser.parse_args()

    # conll_path = "./data/new_datasets/academia_sep_1.conllu"
    # conversion_rules = "./ud_to_spmrl.json"
    tokenized_filepath = argv.ud_filepath.replace('.conllu', '_tokenized.conllu')
    add_token_numbers_to_file(argv.ud_filepath, tokenized_filepath)
    conllu = pd.read_csv(tokenized_filepath, sep="\t", comment="#", skip_blank_lines=False)

    conllu = main(conllu, argv.conversion_rules)
    conllu_for_yap = argv.ud_filepath.replace(".conllu", "_converted.conllu")
    output_to_file(conllu, conllu_for_yap)
    # conllu.to_csv(conllu_for_yap, sep="\t", index=False,
    #               header=False, quoting=csv.QUOTE_NONE, escapechar="\\")