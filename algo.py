import os
import time
from subprocess import Popen, PIPE, STDOUT

import pymeshlab

from utils import get_filename
from config import srst_path

if(not os.path.isfile(srst_path)):
    raise Exception("srst binary doesn't exist")

boolfn = lambda x: bool(int(x))
meshPercent = lambda x: pymeshlab.Percentage(int(x))


def getTransformedOptions(options, params):
    out = {}
    for param in params:
        out[param] = params[param]["type"](options[param])
    return out


def srstOutFn(input, output, **options):
    file_name = get_filename(input)
    outName = os.path.join(output, file_name + str(time.time()) + ".stl")
    p = Popen([srst_path, input, outName], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout = p.communicate(input=options["parameter"].encode())[0]
    return outName


def ball_pivoting(input, output, **options):
    """
    options:
    ballradius: Percentage = 0 %
    clustering: float = 20
    creasethr: float = 90
    deletefaces: bool = False
    """

    params = next(filter(lambda x: x["name"] == "ball pivoting", algos), None)["parameters"]
    transformedOpts = getTransformedOptions(options, params)

    file_name = get_filename(input)
    outName = os.path.join(output, file_name + str(time.time()) + ".stl")
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(input)
    ms.generate_surface_reconstruction_ball_pivoting(**transformedOpts)
    ms.save_current_mesh(outName)

    return outName


def screened_poisson(input, output, **options):
    """
    options:
        visiblelayer : bool = False
        depth : int = 8
        fulldepth : int = 5
        cgdepth : int = 0
        scale : float = 1.1
        samplespernode : float = 1.5
        pointweight : float = 4
        iters : int = 8
        confidence : bool = False
        preclean : bool = False
        threads : int = 16

    """

    params = next(filter(lambda x: x["name"] == "screened poisson", algos), None)["parameters"]
    transformedOpts = getTransformedOptions(options, params)

    file_name = get_filename(input)
    outName = os.path.join(output, file_name + str(time.time()) + ".stl")
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(input)
    ms.surface_reconstruction_screened_poisson(**transformedOpts)
    ms.save_current_mesh(outName)

    return outName


def vcg(input, output, **options):
    """
    options:
        voxsize : Percentage = 1%
        subdiv : int = 1
        geodesic : float = 2
        openresult : bool = True
        smoothnum : int = 1
        widenum : int = 3
        mergecolor : bool = False
        simplification : bool = False
        normalsmooth : int = 3


    """

    params = next(filter(lambda x: x["name"] == "vcg", algos), None)["parameters"]
    transformedOpts = getTransformedOptions(options, params)

    file_name = get_filename(input)
    outName = os.path.join(output, file_name + str(time.time()) + ".stl")
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(input)
    ms.surface_reconstruction_vcg(**transformedOpts)
    ms.save_current_mesh(outName)

    return outName



"""

To add a new algorithm add entry of the following format to the below list 
{
    name: algorithm_name,
    parameters: {parameterName: {label(visible in the gui), type(to be casted to), default(default value in the gui)}}
    fn: The reconstruction algorithm which returns the filename of the reconstructed file - fn(input_file, output_dir, parameters)
}
"""

algos = [
    {
        "name": "srst",
        "parameters": {"parameter": {"default": "5", "type": str}},
        "fn": srstOutFn
    },
    {
        "name": "ball pivoting",
        "parameters": {
            "ballradius": {"default": "0", "type": meshPercent},
            "clustering": {"default": "20", "type": float},
            "creasethr": {"default": "90", "type": float},
            "deletefaces": {"default": "0", "type": boolfn}
        },
        "fn": ball_pivoting
    },
    {
        "name": "screened poisson",
        "parameters": {
            "visiblelayer": {"default": "0", "type": boolfn, "label": "visiblelayer(boolean)"},
            "depth": {"default": "8", "type": int},
            "fulldepth": {"default": "5", "type": int},
            "cgdepth": {"default": "0", "type": int},
            "scale": {"default": "1.1", "type": float},
            "samplespernode": {"default": "1.5", "type": float},
            "pointweight": {"default": "4", "type": float},
            "iters": {"default": "8", "type": int},
            "confidence": {"default": "0", "type": boolfn, "label": "confidence(boolean)"},
            "preclean": {"default": "0", "type": boolfn, "label": "preclean(boolean)"},
            "threads": {"default": "16", "type": int},
        },
        "fn": screened_poisson
    },
    {
        "name": "vcg",
        "parameters": {
            "voxsize": {"default": "1", "type": meshPercent},
            "subdiv": {"default": "1", "type": int},
            "geodesic": {"default": "2", "type": float},
            "openresult": {"default": "1", "type": boolfn, "label": "openresult(boolean)"},
            "smoothnum": {"default": "1", "type": int},
            "widenum": {"default": "3", "type": int},
            "mergecolor": {"default": "0", "type": boolfn, "label": "mergecolor(boolean)"},
            "simplification": {"default": "0", "type": boolfn, "label": "simplification(boolean)"},
            "normalsmooth": {"default": "3", "type": int},
        },
        "fn": vcg
    }
]

# print(pymeshlab.print_filter_parameter_list('surface_reconstruction_vcg'))
# print(pymeshlab.print_filter_parameter_list('surface_reconstruction_screened_poisson'))
# print(pymeshlab.print_filter_parameter_list('surface_reconstruction_ball_pivoting'))
