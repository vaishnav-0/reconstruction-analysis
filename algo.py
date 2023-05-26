import os
import time
from subprocess import Popen, PIPE, STDOUT

srst_path = "../SRST-main/build/srst"


def srstOutFn(input, output, **options):
    file_name = input.split("/")[-1].split(".")[0]
    outName = os.path.join(output, file_name + str(time.time()) + ".stl")
    p = Popen([srst_path, input, outName], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout = p.communicate(input=options["parameter"].encode())[0]
    return outName


"""
{
    name: algorithm name,
    parameters: list of parameters the algorithm accepts. The parameters are passed to the function
                as a dictionary
    fn: The reconstruction algorithm which returns the filename of the reconstructed file
}
"""
algos = [
    {
        "name": "srst",
        "parameters": ["parameter"],
        "fn": srstOutFn
    }
]
