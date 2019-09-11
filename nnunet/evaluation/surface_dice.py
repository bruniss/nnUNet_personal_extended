#    Copyright 2019 Division of Medical Image Computing, German Cancer Research Center (DKFZ), Heidelberg, Germany
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import numpy as np
from medpy.metric.binary import __surface_distances


def normalized_surface_dice(a: np.ndarray, b: np.ndarray, threshold: float, spacing: tuple = None):
    """
    The normalized surface dice is symmetric, so it should not matter wheter a or b is the reference image

    This implementation natively supports 2D and 3D images. Whether other dimensions are supported depends in the
    __surface_distances implementation in medpy

    :param a: image 1
    :param b: image 2
    :param threshold: distances below this threshold will be counted as true positives. Threshold is in mm, not voxels!
    (if spacing = (1, 1(, 1)) then one voxel=1mm so the threshold is effectively in voxels)
    :param spacing: how many mm is one voxel in reality? Can be left at None, we then assume an isotropic spacing of 1mm
    :return:
    """
    if spacing is None:
        spacing = tuple([1 for _ in range(len(a.shape))])
    a_to_b = __surface_distances(a, b, spacing, 1)
    b_to_a = __surface_distances(b, a, spacing, 1)

    tp_a = np.sum(a_to_b <= threshold)
    tp_b = np.sum(b_to_a <= threshold)

    fp = np.sum(a_to_b > threshold)
    fn = np.sum(b_to_a > threshold)

    dc = (tp_a + tp_b) / (tp_a + tp_b + fp + fn)
    return dc
