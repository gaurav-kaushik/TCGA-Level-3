# Level 3 TCGA Data Tools

This project is for working on tools for munging/analyzing TCGA Level 3 data, along with the cwl.json files for use on the Seven Bridges Cancer Genomics Cloud.

### gene\_expression\_munger
This tool integrates RNAseq gene expression data (raw counts) into a clean matrix. When used on the Seven Bridges Cancer Genomics Cloud, it also produced a matrix of metadata attributes for each case analyzed.

To test locally: 
`python gene_expression_munger.py -f Gene_Exp_Test/* -c`

For testing the use of an index file: 
`python gene_expression_munger.py -r Gene_Exp_Test/test.index -c`
