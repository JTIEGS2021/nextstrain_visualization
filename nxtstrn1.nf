#!/usr/bin/env nextflow
nextflow.enable.dsl=2


// Define Inputs
py = Channel.fromPath("get_meta.py")
nwk = Channel.fromPath("data/Aspen_SGE_3_Outbreaks_LyveSET.tre")
ncbi = Channel.fromPath("data/outbreak_plus_ncbi_meta_highlights.csv")
aspen = Channel.fromPath("data/Aspen_SGE_3_Outbreaks.Meta.csv")
select = Channel.fromPath("data/meta_select.tsv")

// py = Channel.fromPath("get_meta.py")
// nwk = Channel.fromPath("outbreak.tre")
// ncbi = Channel.fromPath("outbreak_plus_ncbi_meta.csv")
// aspen = Channel.fromPath("res_seqo_combined1.csv")
// select = Channel.fromPath("meta_select.tsv")

//meta = Channel.fromPath("res_seqo_combined1.csv")

// Metadata merge
process meta_merge {
    debug true
	publishDir "./rst"

    input:
	path py
    path ncbi
    path aspen
    path select

    output:
    path "meta_out.csv", emit: meta

    """
	python $py --meta_ncbi $ncbi --meta_aspen $aspen --meta_select $select
	"""
}


// Augur Refine
process aug_refine {

    debug true
	
    input:
    path nwk

    output:
    path "refine_tree*", emit: tree 
    path "refine_node*", emit: node
    

    """
    augur refine \
    	  --tree $nwk \
   	  --output-tree refine_tree.nwk \
	  --output-node-data refine_node.json \
	  --keep-root \
	  --seed 1234
    """
}

//Get columns
process get_cols {
	debug true
	
	input:
	path meta

	output:
	stdout emit: cols
	
	'''
	cat meta_out.csv | head -1 | tr "," " " | tr -d "\n" | sed "s/^[[:space:]]*//"
	'''
}

// Augur Trait
// Allows predicting of the ancestral traits. Does not need all columns
// TODO create a text file input of select traits to create
process aug_traits {
	debug true
	publishDir "./rst"
	
	input:
	path tree
	path meta
	val cols

	output:
	path "meta_traits.json", emit: traits

	"""
	augur traits --tree $tree --metadata $meta  --output-node-data meta_traits.json --columns [$cols]
	"""
	
}

// Augur Export
process aug_export {
    debug true
    publishDir "./rst"

    input:
    path tree
    path node
    path meta
	path traits
	val cols

    output:
    path "export_out2.json"
    
    

    """
    augur export v2 \
    --tree $tree \
    --metadata $meta \
    --node-data $node $traits \
    --color-by-metadata  $cols \
    --output export_out2.json
    """
}

// Workflow
workflow {
	meta_merge(py, ncbi, aspen , select)
    aug_refine(nwk)
	get_cols(meta_merge.out.meta)
	aug_traits(aug_refine.out.tree, meta_merge.out.meta, get_cols.out.cols)
    aug_export(aug_refine.out.tree,
			   aug_refine.out.node,
			   meta_merge.out.meta,
			   aug_traits.out.traits,
			   get_cols.out.cols) 
}




