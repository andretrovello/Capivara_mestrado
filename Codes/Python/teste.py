from astropy.io import fits
import os 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



def parse_fits_header(filename):
    with fits.open(filename) as hdul:
        hdr = hdul[0].header
        
        # Filtra apenas keywords padrão (remove HISTORY e comentários)
        main_keys = [k for k in hdr.keys() if not k.startswith(('HISTORY', 'COMMENT', 'D00'))]
        
        # Cria dicionário com os metadados principais
        metadata = {}
        for k in main_keys:
            try:
                metadata[k] = hdr[k]
            except:
                metadata[k] = None
        
        # Extrai informações específicas do drizzle (se existirem)
        drizzle_params = {}
        for i in range(1, 10):  # Verifica até D009
            key_prefix = f'D{i:03d}'
            if key_prefix + 'VER' in hdr:
                drizzle_params[f'DRIZZLE_{i}'] = {
                    'version': hdr.get(key_prefix + 'VER'),
                    'input': hdr.get(key_prefix + 'DATA'),
                    'wavelength': hdr.get(key_prefix + 'LAM')
                }
        
        return {
            'main_metadata': metadata,
            'drizzle_info': drizzle_params,
            'history': [h for h in hdr['HISTORY'] if h.strip()]  # Lista de históricos não vazios
        }


#loc = os.path.expanduser("~/Desktop/Capivara_mestrado/Input/S4G")
loc = os.path.expanduser("~/Desktop/Capivara_mestrado/Input/PHANGS/phangs_hst/ngc1087")
# Change to the target directory
os.chdir(loc)

# Get a list of all files in the directory
file_list = os.listdir()

#with fits.open('NGC1087.phot.1.fits') as hdul:

#print(file_list)
#print(len(file_list))

with fits.open('hlsp_phangs-hst_hst_wfc3-uvis_ngc1087_f275w_v1_err-drc-wht.fits') as hdul:
    data = hdul[0].data
    head = hdul[0].header
    y_size, x_size = data.shape
    
    # Defina os limites do recorte (100 pixels de cada lado)
    x_center, y_center = x_size // 2, y_size // 2
    x_start, x_end = x_center - 100, x_center + 100
    y_start, y_end = y_center - 100, y_center + 100
    
    # Recorte os dados
    data_cut = data[y_start:y_end, x_start:x_end]
    


'''phangs = parse_fits_header('hlsp_phangs-hst_hst_wfc3-uvis_ngc1087_f275w_v1_err-drc-wht.fits')
#print(phangs['main_metadata'])
print(data.shape)'''

data_cube = np.zeros((data_cut.shape[0], data_cut.shape[1], len(file_list)))

for i in range(0, len(file_list)):
    with fits.open(file_list[i]) as hdul:
        
        data = hdul[0].data
        head = hdul[0].header
        y_size, x_size = data.shape
        
        # Defina os limites do recorte (100 pixels de cada lado)
        x_center, y_center = x_size // 2, y_size // 2
        x_start, x_end = x_center - 100, x_center + 100
        y_start, y_end = y_center - 100, y_center + 100
        
        # Recorte os dados
        data_cut = data[y_start:y_end, x_start:x_end]
        
        # Atualize o header WCS
        head['CRPIX1'] -= x_start  # Ajuste do ponto de referência X
        head['CRPIX2'] -= y_start  # Ajuste do ponto de referência Y
        print(i, file_list[i])
        data_cube[:,:,i] = data_cut


print(data_cube.shape)
# Salve o novo arquivo
fits.writeto('phangs_teste.fits', data_cube, head, overwrite=True)