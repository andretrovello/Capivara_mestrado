from astropy.io import fits
import os 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#loc = os.path.expanduser("~/Desktop/Capivara_mestrado/Input/S4G")
loc = os.path.expanduser("~/Desktop/Capivara_mestrado/Input/PHANGS/phangs_hst/ngc1087")
# Change to the target directory
os.chdir(loc)

# Get a list of all files in the directory
file_list = os.listdir()

#with fits.open('NGC1087.phot.1.fits') as hdul:

#print(file_list)
print(len(file_list))
with fits.open('hlsp_phangs-hst_hst_wfc3-uvis_ngc1087_f275w_v1_err-drc-wht.fits') as hdul:
    # Print the names of the HDUs in the file
    data = hdul[0].data
    header = hdul[0].header

    #print(hdul.info())

#print(data)

plt.figure(figsize=(10, 10))
for i,name in enumerate(file_list):
    if name.endswith('.fits'):
        with fits.open(name) as hdul:
            # Print the names of the HDUs in the file
            data = hdul[0].data
            header = hdul[0].header

    plt.subplot(5,3,i+1)
    plt.imshow(np.nan_to_num(data, nan=0), origin='lower', cmap='inferno')
    plt.title(f'{name}')
    plt.colorbar()
plt.show()
