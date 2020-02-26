# frangi3d

The Frangi filter for 3D numpy arrays.

This project utilizes scipy and numpy to compute eigenvalues for 3D numpy arrays which are then used as part of the Frangi filter for vesselness.

## Install

`pip install git+https://github.com/lrq3000/frangi3d.git`

## Usage

Here is an example on a 3D NIfTI image:

```python
import numpy as np
import nibabel as nib
from nilearn import image

from frangi import frangi

# Path to NIfTI image
imgpath = r'path/to/image.nii'

# Load up the NIfTI in memory
im = image.load_img(imgpath)

# Compute Frangi vesselness filter
im_frangi = frangi(im.get_fdata())
```

## License

This project is licensed under the MIT License.

## Authors

Original module by [David G Ellis](https://github.com/ellisdg).

Patches by [Lee Kamentsky](https://github.com/LeeKamentsky), [meetaig](https://github.com/meetaig) and [Stephen Karl Larroque](https://github.com/lrq3000).
