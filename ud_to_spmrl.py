import pandas as pd
import json
import csv

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
                value = row_feature.split("=")[1]
                if key in features:
                    new_name = features[key]["spmrl_name"]
                    if features[key]["multiple_values"] == 0:
                        if value in features[key]["single_values"]:
                            new_value = features[key]["single_values"][value]
                            converted_features.append(f"{new_name}={new_value}")
                    else:
                        for ud, spmrl in features[key]["single_values"].items():
                            converted_features.append(f"{new_name}={spmrl}")
        return "|".join(converted_features)




if __name__ == "__main__":
    conll_path = "./data/new_datasets/academia_sep.conllu"
    conllu = pd.read_csv(conll_path, sep="\t", comment="#", skip_blank_lines=False)

    with open("./ud_to_spmrl.json", "r") as conv:
        conversion_rules = json.load(conv)
        pos_tags = conversion_rules["POS"]
        features = conversion_rules["FEATS"]

    conllu["XPOS"] = conllu.apply(lambda x: create_xpos(x, pos_tags), axis=1)
    conllu["FEATS"] = conllu.apply(lambda x: convert_features(x, features), axis=1)
    #
    conllu.to_csv("./data/new_datasets/academia_final_converted.conllu", sep="\t", index=False,
                  header=False, quoting=csv.QUOTE_NONE, quotechar="", escapechar="\\")