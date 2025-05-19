import astropy
import os 


def get_filters(file_list, start, position):
    filters = []
    for file in file_list:
        if file.startswith(start):
            filter = file.split('_')[position]
            filters.append(filter)
    return filters


#loc = os.path.expanduser("~/Desktop/Capivara_mestrado/Input/S4G")
loc = os.path.expanduser("~/Desktop/Capivara_mestrado/Input/PHANGS/phangs_hst/ngc1087")
# Change to the target directory
os.chdir(loc)

# Get a list of all files in the directory
file_list = os.listdir()

#with fits.open('NGC1087.phot.1.fits') as hdul:
#with fits.open('hlsp_phangs-hst_hst_wfc3-uvis_ngc1087_f336w_v1_err-drc-wht.fits') as hdul:

filters = get_filters(file_list, 'hlsp_phangs-hst_hst_wfc3-uvis_ngc1087_', 5)
'''
# arquivos dos filtros
fits_files = [
    ('F115W.fits', 'F115W'),
    ('F150W.fits', 'F150W'),
    ('F200W.fits', 'F200W'),
    ('F277W.fits', 'F277W'),
    ('F356W.fits', 'F356W'),
    ('F410M.fits', 'F410M'),
    ('F444W.fits', 'F444W'),]

# referência para alinhamento (os filtros podem não 
#cobrir exatamente a mesma região, precisa corrigir)
ref_file, ref_filter = 'F115W.fits', 'F115W'
with fits.open(ref_file) as hdul_ref:
    ref_data = hdul_ref[1].data # confira se os dados estão em [0] ou [1]
    ref_header = hdul_ref[1].header

aligned_images = []
filter_names = []

# reprojeção e salvamento individual
for file, filt in fits_files:
    with fits.open(file) as hdul:
        if len(hdul) < 2 or hdul[1].data is None:
            print(f"Aviso: '{file}' não tem dados válidos na extensão 1.")
            continue

        data = hdul[1].data
        hdr_d = hdul[1].header
        w_in = WCS(hdr_d, hdul)

        data_aligned, _ = reproject_interp((data, w_in), ref_header)
        aligned_images.append(data_aligned)
        filter_names.append(filt)

        # salva imagem reprojetada individual
        w_out = WCS(ref_header)
        wcs_header = w_out.to_header()

        # cópia do cabeçalho original e atualização do WCS
        aligned_header = ref_header.copy()
        aligned_header.update(wcs_header)

        hdu_aligned = fits.PrimaryHDU(data_aligned, header=aligned_header)
        aligned_filename = f"{filt}_aligned.fits"
        hdu_aligned.writeto(aligned_filename, overwrite=True)
        print(f" '{aligned_filename}' salvo.")

# cubo
cube = np.array(aligned_images)

# header cubo
wcs_3d = WCS(naxis=3)

wcs_2d = WCS(ref_header, naxis=2)
wcs_3d.wcs.crpix[0] = wcs_2d.wcs.crpix[0]
wcs_3d.wcs.crpix[1] = wcs_2d.wcs.crpix[1]
wcs_3d.wcs.crval[0] = wcs_2d.wcs.crval[0]
wcs_3d.wcs.crval[1] = wcs_2d.wcs.crval[1]
wcs_3d.wcs.cdelt[0] = wcs_2d.wcs.cdelt[0]
wcs_3d.wcs.cdelt[1] = wcs_2d.wcs.cdelt[1]
wcs_3d.wcs.ctype[0] = wcs_2d.wcs.ctype[0]
wcs_3d.wcs.ctype[1] = wcs_2d.wcs.ctype[1]
wcs_3d.wcs.cunit[0] = wcs_2d.wcs.cunit[0]
wcs_3d.wcs.cunit[1] = wcs_2d.wcs.cunit[1]

wcs_3d.wcs.crpix[2] = 1
wcs_3d.wcs.crval[2] = 0
wcs_3d.wcs.cdelt[2] = 1
wcs_3d.wcs.ctype[2] = 'FILTER'
wcs_3d.wcs.cunit[2] = ''

cube_header = wcs_3d.to_header()
cube_header['NAXIS'] = 3
cube_header['NAXIS1'] = ref_data.shape[1]
cube_header['NAXIS2'] = ref_data.shape[0]
cube_header['NAXIS3'] = len(filter_names)

# escreve os filtros no header 
for i, filt in enumerate(filter_names):
    cube_header[f'FILTER{i+1}'] = filt

# cubo final
hdu = fits.PrimaryHDU(cube, header=cube_header)
hdu.writeto('JWST_NIRCam_cube.fits', overwrite=True)
print("Cubo salvo como 'JWST_NIRCam_cube.fits'")

# recorte de regiões específicas menores para rodar no capivara
regions = [
    ('region1', 900, 1000, 600, 700),    #x1, x2, y1, y2 
    ('region2', 1000, 1100, 600, 700),   
    ('region3', 1000, 1100, 700, 800)     
]

for name, x_start, x_end, y_start, y_end in regions:
    cube_cut = cube[:, y_start:y_end, x_start:x_end]
    
    new_nx = x_end - x_start
    new_ny = y_end - y_start

    # header das regiões cortadas
    cut_header = cube_header.copy()
    cut_header['NAXIS1'] = new_nx
    cut_header['NAXIS2'] = new_ny
    cut_header['CRPIX1'] -= x_start
    cut_header['CRPIX2'] -= y_start

    # cubos menores
    filename = f'JWST_NIRCam_cube_{name}.fits'
    hdu_cut = fits.PrimaryHDU(cube_cut, header=cut_header)
    hdu_cut.writeto(filename, overwrite=True)
    print(f"Cubo recortado salvo como '{filename}'")'''