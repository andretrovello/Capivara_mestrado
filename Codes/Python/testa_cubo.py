from astropy.io import fits
import os
import matplotlib.pyplot as plt

#loc = os.path.expanduser("~/Desktop/Capivara_mestrado/Input/S4G")
loc = os.path.expanduser("~/Desktop/Capivara_mestrado/Input/PHANGS/phangs_hst/ngc1087")
# Change to the target directory
os.chdir(loc)

# Get a list of all files in the directory
file_list = os.listdir()
#print(file_list)
#with fits.open('NGC1087.phot.1.fits') as hdul:
#with fits.open('hlsp_phangs-hst_hst_wfc3-uvis_ngc1087_f336w_v1_err-drc-wht.fits') as hdul:

with fits.open('PHANGS_cube.fits') as hdul:
    data = hdul[0].data
    header = hdul[0].header

print(data.shape)

figura = data[0, :, :]
print(figura.shape)
plt.figure()
plt.imshow(figura[60:80, 60:80], cmap='inferno', origin='lower')
plt.colorbar()
plt.show()