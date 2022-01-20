Word Fix
========
Fix all the space related misspellings in your document. Incorrect word splits or words joins are a very common issue with OCR.

The package has three functions: split, join, fix.
- Use fix() if you want all the errors to be automatically identified and corrected accordingly.
- Use split() if you only need to split incorrect words.
- Use join() if you only need to join incorrect words.


Usage
-----
```python
>>> import AI_doc_wordfix as wf
>>> wf.split("theviews of physicianspracticing in relevantclinical areas.")
'the views of physicians practicing in relevant clinical areas.'

>>> wf.join("Agre ement betw een Anth em a nd")
'Agreement between Anthem and'

>>> wf.fix('''T he co des includebutare not li m ite d to, AmericanMedical Association CurrentProcedural Termino logy ("CPT®-4"), CMS Healthcare CommonProcedure Coding System ("HCPCS"), International Classification of Diseases, 10th Revision, Clinical Modification ("ICD-10-CM"), National Drug Code ("NDC"), and Revenue Codes or their successors.''')
'The codes include but are not limited to, American Medical Association Current Procedural Terminology ("CPT®-4"), CMS Healthcare Common Procedure Coding System ("HCPCS"), International Classification of Diseases, 10th Revision, Clinical Modification ("ICD-10-CM"), National Drug Code ("NDC"), and Revenue Codes or their successors.'
```

Features
--------
Not only words, you can directly pass an entire document text to the fix method.
The package will handle the punctuations properly.

You can add or remove any words as per the language/domain to the dictionary file(en_words_cleaned.txt) located at the data directory.

