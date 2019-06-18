"""
Input can be either a string or a csv file with conll-x format. If csv, please provide a filepath.
"""
import pandas as pd
import csv

class Convert_SPMRL_to_UD():

    def __init__(self, conll=None, filepath=None):
        if conll:
            self.conll = conll
            self.df = self.create_df()
        elif filepath:
            self.df = self.create_df_from_conll_file(filepath=filepath)
        self.pronouns = {
             'suf_gen=F|suf_gen=M|suf_num=P|suf_per=1': '_אנחנו',
             'suf_gen=F|suf_gen=M|suf_num=S|suf_per=1': '_אני',
             'suf_gen=M|suf_num=S|suf_per=2': '_אתה',
             'suf_gen=F|suf_num=S|suf_per=2': '_את',
             'suf_gen=M|suf_num=P|suf_per=2': '_אתם',
             'suf_gen=F|suf_num=P|suf_per=2': '_אתן',
             'suf_gen=F|suf_num=P|suf_per=3': '_הן',
             'suf_gen=F|suf_num=S|suf_per=3': '_היא',
             'suf_gen=M|suf_num=P|suf_per=3': '_הם',
             'suf_gen=M|suf_num=S|suf_per=3': '_הוא'
        }
        self.segmented_sentence = self.segmentation()

    def create_df_from_conll_file(self, filepath):
        treebank = []
        columns = ['ID', 'FORM', 'LEMMA', 'UPOS', 'XPOS', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
        try:
            df = pd.read_csv(filepath, sep='\t', header=None, names=columns, na_filter=False, quoting=csv.QUOTE_NONE)
        except:
            with open(filepath, 'r') as source:
                for line in source.readlines():
                    if len(line.split('\t')) == 10:
                        treebank.append(tuple(line.strip().split('\t')))
                    elif len(line.split('\t')) == 1:
                        treebank.append((line.strip(), '', '', '', '', '', '', '', '', ''))
                df = pd.DataFrame(data=treebank, columns=columns)
        return df

    def create_df_from_conll_formatted_string(self):
        rows = []
        conll = self.conll.split('\n')
        for line in conll:
            cols = line.split('\t')
            if len(cols) > 1:
                rows.append({'ID': cols[0], 'FORM': cols[1], 'LEMMA': cols[2], 'UPOS': cols[3], 'XPOS': cols[4],
                             'FEATS': cols[5], 'HEAD': cols[6], 'DEPREL': cols[7], 'DEPS': cols[8], 'MISC': cols[9]})
        df = pd.DataFrame(rows)
        return df

    def segmentation(self):
        """ this accutely needs something more efficient"""

        cols = self.df.columns
        segmented_spmrl_df = pd.DataFrame(columns=cols)
        for i, row in self.df.iterrows():
            suffix_feats = "|".join([x for x in row['FEATS'].split("|") if 'suf' in x])
            noun_feats = "|".join([x for x in row['FEATS'].split("|") if 'suf' not in x])
            clean_suffix_feats = "|".join([x.replace("suf_", "") for x in row['FEATS'].split("|") if 'suf' in x])
            if row['UPOS'] == 'NN' and 'suf_' in row['FEATS']:
                segmented_spmrl_df = segmented_spmrl_df.append(
                    {'ID': row['ID'], 'FORM': row['LEMMA'] + '_', 'LEMMA': row['LEMMA'], 'UPOS': 'NOUN', 'XPOS': 'NOUN',
                     'FEATS': 'Definite=Def|' + noun_feats, 'HEAD': row['HEAD'], 'DEPREL': row['DEPREL'],
                    'DEPS': row['DEPS'], 'MISC': row['MISC']},
                    ignore_index=True)

                segmented_spmrl_df = segmented_spmrl_df.append(
                    {'ID': 0, 'FORM': '_של_', 'LEMMA': 'של', 'UPOS': 'ADP', 'XPOS': 'ADP', 'FEATS': '_',
                      'HEAD': int(row['ID']) + 2,'DEPREL': 'case:gen', 'DEPS': row['DEPS'],'MISC': row['MISC']},
                    ignore_index=True)

                segmented_spmrl_df = segmented_spmrl_df.append(
                    {'ID': 0, 'FORM': self.pronouns[suffix_feats], 'LEMMA': 'הוא', 'UPOS': 'PRON',
                     'XPOS': 'PRON', 'FEATS': "Case=Gen|" + clean_suffix_feats + "|PronType=Prs",
                     'HEAD': int(row['ID']) + 2, 'DEPREL': 'nmod:poss', 'DEPS': row['DEPS'], 'MISC': row['MISC']},
                    ignore_index=True)

            elif row['XPOS'] == 'S_PRN':
                segmented_spmrl_df.at[i-1, 'XPOS'] = 'ADP'
                segmented_spmrl_df.at[i-1, 'FORM'] += '_'
                segmented_spmrl_df.at[i-1, 'FEATS'] = 'Case=Gen'

                prev_feats = segmented_spmrl_df.loc[i-1]['FEATS'] + '|'
                if prev_feats == '_|':
                    prev_feats = ''
                segmented_spmrl_df = segmented_spmrl_df.append({'ID': row['ID'], 'FORM': row['LEMMA'] + '_' ,'LEMMA': row['LEMMA'],  'UPOS': 'PRON',
                                    'XPOS': 'PRON', 'FEATS': prev_feats + 'PronType=Prs', 'HEAD': row['HEAD'],
                                    'DEPREL': row['DEPREL'], 'DEPS': row['DEPS'], 'MISC': row['MISC']}, ignore_index=True)


            elif row['XPOS'] == 'DTT' or row['XPOS'] == 'DT':
                if 'suf_' in row['FEATS']:
                    segmented_spmrl_df = segmented_spmrl_df.append(
                        {'ID': row['ID'], 'FORM': row['FORM'], 'LEMMA': row['LEMMA'], 'UPOS': 'NOUN',
                         'XPOS': 'NOUN', 'FEATS': row['FEATS'], 'HEAD': row['HEAD'],
                         'DEPREL': row['DEPREL'], 'DEPS': row['DEPS'], 'MISC': row['MISC']},
                        ignore_index=True)

                    segmented_spmrl_df = segmented_spmrl_df.append(
                        {'ID': 0, 'FORM': "_" + self.pronouns[suffix_feats], 'LEMMA': 'הוא', 'UPOS': 'PRON',
                         'XPOS': 'PRON', 'FEATS': "Case=Gen|" + clean_suffix_feats + "|PronType=Prs",
                         'HEAD': int(row['ID']) + 1,
                         'DEPREL': 'nmod:poss', 'DEPS': row['DEPS'], 'MISC': row['MISC']},
                        ignore_index=True)
                else:
                    segmented_spmrl_df = segmented_spmrl_df.append(row, ignore_index=True)
            elif row['XPOS'] == 'S_PRP':
                segmented_spmrl_df = segmented_spmrl_df.append(
                    {'ID': row['ID'], 'FORM': row['FORM'], 'LEMMA': row['LEMMA'], 'UPOS': row['UPOS'],
                     'XPOS': row['XPOS'], 'FEATS': row['FEATS'] + "|PronType=Prs|Reflex=Yes", 'HEAD': row['HEAD'],
                     'DEPREL': row['DEPREL'], 'DEPS': row['DEPS'], 'MISC': row['MISC']},
                    ignore_index=True)
            else:
                segmented_spmrl_df = segmented_spmrl_df.append(row, ignore_index=True)

        return segmented_spmrl_df

    def apply_conversions(self, feats=None, simple_pos=None, complex_pos_conversions=None):
        def simple_features_conversion(column, conversions):
            for old, new in conversions.items():
                column = column.replace(old, new)

            return column

        def pos_conversion(column, conversions):
            if column in conversions:
                return conversions[column]
            else:
                return column

        def pos_convert_entire_line(row, conversions):
            xpos = row['XPOS']
            #     if xpos in conversions:
            if xpos in conversions:
                upos = conversions[xpos]['pos']
                if conversions[xpos]['deprel'] == 'deprel':
                    deprel = row['DEPREL']
                else:
                    deprel = conversions[xpos]['deprel']
                if conversions[xpos]['feats'] == 'feats':
                    feats = row['FEATS']
                elif conversions[xpos]['feats']['old'] == '_':
                    feats = conversions[xpos]['feats']['new']
                elif conversions[xpos]['feats']['old'] == 'feats+':
                    if len(row['FEATS']) > 2:
                        feats = row['FEATS'] + conversions[xpos]['feats']['new']
                    else:
                        feats = conversions[xpos]['feats']['new'][1:]
                elif conversions[xpos]['feats']['old'] == '+feats':
                    feats = conversions[xpos]['feats']['new'] + row['FEATS']
                elif conversions[xpos]['feats']['old'] == '+feats+':
                    feats = conversions[xpos]['feats']['new'][0] + row['FEATS'] + conversions[xpos]['feats']['new'][1]
                return pd.Series([upos, deprel, feats])
            else:
                return pd.Series([row['UPOS'], row['DEPREL'], row['FEATS']])

        if feats:
            self.segmented_sentence.loc[:, 'FEATS'] = self.segmented_sentence['FEATS'].apply(
                lambda x: simple_features_conversion(x, feats))

        if simple_pos:
            self.segmented_sentence.loc[:, 'UPOS'] = self.segmented_sentence['UPOS'].apply(
                lambda x: pos_conversion(x, simple_pos))

        if complex_pos_conversions:
            self.segmented_sentence[['UPOS', 'DEPREL', 'FEATS']] = self.segmented_sentence.apply(
                lambda x: pos_convert_entire_line(x, complex_pos_conversions), axis=1)


if __name__ == '__main__':
    filepath_spmrl_dev = './data/spmrl-treebank/dev_hebtb-gold.conll'
    filepath_spmrl_train = './data/spmrl-treebank/train_hebtb-gold.conll'
    filepath_spmrl_test = './data/spmrl-treebank/test_hebtb-gold.conll'

    filepath_ud_dev = './data/ud-treebank/he_htb-ud-dev.conllu'
    filepath_ud_train = './data/ud-treebank/he_htb-ud-train.conllu'
    filepath_ud_test = './data/ud-treebank/he_htb-ud-test.conllu'
    converter = Convert_SPMRL_to_UD(filepath=filepath_spmrl_dev)
    base_df = converter.df
    print(base_df.head(30))
    # seg_df = converter.segmented_sentence

    basic_features = {'gen=F|gen=M': 'Gender=Fem,Masc', 'gen=F': 'Gender=Fem', 'gen=M': 'Gender=Masc',
                      'num=S': 'Number=Sing', 'num=P': 'Number=Plur',
                      'per=A': 'Person=1,2,3', 'per=': 'Person=',
                      'tense=BEINONI': 'VerbForm=Part', 'tense=TOINFINITIVE': 'VerbForm=Inf',
                      'tense=IMPERATIVE': 'Mood=Imp',
                      'tense=PAST': 'Tense=Past', 'tense=FUTURE': 'Tense=Fut'
                      }

    basic_pos = {
        'IN': 'ADP', 'NNP': 'PROPN', 'JJ': 'ADJ', 'NN': 'NOUN', 'VB': 'VERB', 'RB': 'ADV', 'NCD': 'NUM', 'NEG': 'ADV',
        'PREPOSITION': 'ADP', 'REL': 'SCONJ', 'COM': 'SCONJ', 'CONJ': 'CCONJ', 'POS': 'ADP', 'PRP': 'PRON',
        'yyCLN': 'PUNCT', 'yyCM': 'PUNCT', 'yyDASH': 'PUNCT', 'yyDOT': 'PUNCT', 'yyELPS': 'PUNCT', 'yyEXCL': 'PUNCT',
        'yyLRB': 'PUNCT', 'yyQM': 'PUNCT', 'yyQUOT': 'PUNCT', 'yyRRB': 'PUNCT', 'yySCLN': 'PUNCT', 'ZVL': 'X'
    }

    entire_line_pos_conversion = {
        'AT': {'pos': 'ADP', 'deprel': 'case:acc', 'feats': {'old': '_', 'new': 'Case=Acc'}},
        'BN': {'pos': 'VERB', 'deprel': 'deprel', 'feats': {'old': 'feats+', 'new': "|VerbForm=Part"}},
        'BNT': {'pos': 'VERB', 'deprel': 'deprel',
                'feats': {'old': '+feats+', 'new': ['Definite=Cons|', '|VerbForm=Part']}},
        'CD': {'pos': 'NUM', 'deprel': 'deprel', 'feats': 'feats'},
        'CDT': {'pos': 'NUM', 'deprel': 'deprel', 'feats': {'old': '+feats', 'new': "Definite=Cons|"}},
        'NNT': {'pos': 'NOUN', 'deprel': 'deprel', 'feats': {'old': '+feats', 'new': "Definite=Cons|"}},
        'COP': {'pos': 'AUX', 'deprel': 'deprel', 'feats': {'old': 'feats+', 'new': "|VerbType=Cop|VerbForm=Part"}},
        'DEF': {'pos': 'DET', 'deprel': 'deprel', 'feats': {'old': '_', 'new': 'PronType=Art'}},
        'EX': {'pos': 'VERB', 'deprel': 'deprel', 'feats': {'old': '_', 'new': 'HebExistential=True'}},
        'P': {'pos': 'ADV', 'deprel': 'compound:affix', 'feats': {'old': '_', 'new': 'Prefix=True'}},
        'DUMMY_AT': {'pos': 'ADP', 'deprel': 'case:acc', 'feats': {'old': '_', 'new': 'Case=Acc'}},
        'JJT': {'pos': 'ADJ', 'deprel': 'deprel', 'feats': {'old': '+feats', 'new': 'Definite=Cons|'}},
        'MD': {'pos': 'AUX', 'deprel': 'deprel', 'feats': {'old': 'feats+', 'new': '|VerbType=Mod'}},
        'QW': {'pos': 'ADV', 'deprel': 'deprel', 'feats': {'old': '_', 'new': 'PronType=Int'}},
        'TEMP': {'pos': 'SCONJ', 'deprel': 'mark', 'feats': {'old': '_', 'new': 'Case=Tem'}},
        'DTT': {'pos': 'DET', 'deprel': 'deprel', 'feats': {'old': '_', 'new': 'Definite=Cons'}},
        'S_ANP': {'pos': 'PRON', 'deprel': 'deprel', 'feats': {'old': '+feats+', 'new': ['Case=Acc|', '|PronType=Prs']}}

    }

    converter.apply_conversions(feats=basic_features, simple_pos=basic_pos, complex_pos_conversions=entire_line_pos_conversion)

    # print(converter.segmented_sentence[])
    columns = ['ID', 'FORM', 'LEMMA', 'UPOS', 'XPOS', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
    converter.segmented_sentence.to_csv('./data/check_segmentation.conllu', sep='\t', columns=columns, quoting=csv.QUOTE_NONE)