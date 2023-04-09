### 2023-04-09

Changes for UD v2.8 
1. Fixed validation issues with lang-spec relations and features.
  - Commas are now dependent on the head of the element (subordinate clause, appos) that they introduce.
  - DEPREL of det:def changed to det + Definite=Def added to FEATS
  - Hyphens that follow compound:affix depend on the affix rather than the compound head (בין-משרדית).
2. Attribute HebSource moved from FEATS to MISC; same for undocumented Xtra=Junk.
3. HebExistential changed from True to Yes as with other boolean features in UD.

### 2018-10-28

1. fix instances where the case's form was different from the lemma, e.g. להם --> להם + הם instead of להם --> ל_ + הם
2. Whereas the present tense existential markers were marked as HebExistential=True in the
FEATS column (יש בו נגיעה לענייני החוק), past and future inflected instances were marked as VerbType=Cop (לא היה איש בדירתו)
3. Whenever a verb is both marked as VerbType=cop, it is the head of its clause and it is followed by its subject, 
we changed the VerbType=Cop feature into HebExistential=True.
4. change (CCONJ X advmod) to (ADV X advmod)
5. For cases of אותו, אותה, אותן etc. in the sense of "the same", replace Case=Acc with Definite=Def and add אותו as lemma.
6. change לראותם into לראות את הם --> modified in Victoria's code.
7. change fixed to advmod where internal structure makes the 'fixed' token come before its head.


### 2018-07-09

1. Change iobj --> obl for DEPREL
2. Change acl:inf --> acl for DEPREL
3. Change det:quant --> det for DEPREL
4. Change PART --> ADP for UPOSTAG and XPOSTAG
5. Some occurrences of ze / zo are labeled as amod/PRON and we think they shouldn't. 
Such are the determiners that appear after the nominal.Change amod --> det when POS tag is PRON for UPOSTAG and XPOSTAG
6. Replacing the feature prefix=yes with the relation compound:affix
7. changing past/future copulars from aux to cop and their POS to AUX.
8. Replacing hebrew specific labels with global ones for non-specific phenomena:
    - Change conj:discourse --> parataxis for DEPREL
    - Change obl:tmod --> advmod when POS tag is ADV for UPOSTAG and XPOSTAG
    - Change advmod:inf --> acl for DEPREL
    - Change aux:q --> mark:q for DEPREL
    - Change advmod:phrase --> advmod for DEPREL
    - advmod phrase --> fixed
9. wherever the POS tag is INTJ, the label was changed from advmod to discourse
10. Change predicative complemets from advcl to and advmod xcomp
11. change dep to advmod when head is advmod:phrase
12. making modal items as aux (and respectively dependent) and passing their label to their (former) predicate dependent.
