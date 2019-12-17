import pandas as pd
import json


conll_path = "./data/new_datasets/academia_final.conllu"
conllu = pd.read_csv(conll_path, sep="\t", comment="#")


with open("./ud_to_spmrl.json", "r") as conv:
    conversion_rules = json.load(conv)
    pos_tags = conversion_rules["POS"]
    print(pos_tags)



def create_xpos(row):
    xpos = "UNK"
    for tag in pos_tags:
        if row["UPOS"] == tag["UPOS"]:
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


conllu["new_col"] = conllu.apply(lambda x: create_xpos(x), axis=1)
conllu.to_csv("./data/new_datasets/academia_final_converted.conllu", sep="\t")




