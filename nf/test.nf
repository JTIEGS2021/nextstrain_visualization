nextflow.enable.dsl=1

params.force = false
params.yes = "yes"

println("Force: ${params.force}")


process test {

    debug true
	
//   when:
//	params.force

	val x from params.yes

    """
    echo "foo"
	echo "$x"
	"""
}
