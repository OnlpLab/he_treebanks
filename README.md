# he_treebanks
A library for handling Hebrew treebanks, with focus on the Hebrew UD treebank HTB.

## Structure

### Data
1. The UD_HTB directory contains the Hebrew UD treebank, divided into _dev_, _train_ and _test_ splits.
2. Conversion schemes - mostly json files that hold the conversion information to be used by the conversion scripts.

### src

mostly conversion scripts. The main ones are:
#### changes_to_treebank.py
A tool for investigation and conversion of the treebank. e.g. allows retrieval of all tokens that correspond to some attribute.
For previous changes, see changelog. 

#### lattices_builder.py
takes a raw sentence and builds a "lattices" file - one which all possible parses of each token are listed.
For example, the sentence שלום, היום יום יפה would yield the following lattice (in a conll-ul format):
```
FROM   TO     FORM   LEMMA  UPOS  CPOS  FEATURES                    MISC    ANCHORS
0-5 בצלם
0      5      BCLM   BCLM   PROPN   -
0      1      B      B      ADP     -                                       goldid=1
0      3      BCL    BCL    NOUN    -   Gender=Masc|Number=Sing
1      2      H      H      DET     -   PronType=Art                        goldid=2
1      3      CL     CL     NOUN    -   Gender=Masc|Number=Sing
2      3      CL     CL     NOUN    -   Gender=Masc|Number=Sing             goldid=3
2      5      CLM    CILM   VERB    -   Gender=Masc|Number=Si...
2      5      CLM    CILM   VERB    -   Gender=Masc|Mood=Imp...
2      5      CLM    CLM    NOUN    -   Definite=Cons|Gender=Mas...
2      5      CLM    CLM    NOUN    -   Gender=Masc|Number=Sing
3      4      FL     FL     ADP     -                                       goldid=4
4      5      HM     ANI    PRON    -   Gender=Masc|Number=Plur|Person=3    goldid=5
5-7    הנעים
5      7      HNEIM  HNEIM  VERB    -   Gender=Masc...
5      6      H      H      DET     -   PronType=Art                        goldid=6
5      6      H      H      SCONJ   -
6      7      NEIM   NEIM   ADJ     -   Gender=Masc|Number=Sing             goldid=7
6      7      NEIM   NEIM   ADJ     -   Definite=Cons|Gender=...
6      7      NEIM   NEIM   ADV     -   Polarity=Neg
6      7      NEIM   NEIM   AUX     -   Gender=Masc|Number=Sing...
6      7      NEIM   NEIM   PROPN   -
6      7      NEIM   NEIM   VERB    -   Gender=Masc|Tense=Part|VerbForm=Part
6      7      NEIM   NEIM   VERB    -   Gender=Masc|VerbForm=Part

```
### Notebooks
Jupyter notebook versions of the scripts found in src. 