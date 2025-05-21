from astropy.io import fits
from astropy.wcs import WCS
from reproject import reproject_interp
import os
import numpy as np
import psutil
import gc
from tqdm import tqdm  # Para barra de progresso

# Obtem os filtros do survey 
def get_filters(file_list, start, position):
    return list(set(file.split('_')[position] for file in file_list if file.startswith(start)))

# Checa o uso de memória ao longo do programa
def log_memory_usage():
    process = psutil.Process(os.getpid())
    print(f"Uso de memória: {process.memory_info().rss / 1024 ** 2:.2f} MB")

# Cria o cubo de dados considerando apenas uma região dos dados
# visto que os arquivos completos do PHANGS são muito pesados
def create_data_cube(aligned_images, filter_names, ref_header, ref_data, output_filename):
    # Cria o array 3D do cubo
    cube = np.array(aligned_images)
    
    # Configura o WCS 3D baseado no 2D
    wcs_3d = WCS(naxis=3)
    wcs_2d = WCS(ref_header, naxis=2)
    
    # Copia os parâmetros espaciais do 2D para o 3D
    spatial_params = ['crpix', 'crval', 'cdelt', 'ctype', 'cunit']
    for i in [0, 1]:  # Eixos x e y
        for param in spatial_params:
            getattr(wcs_3d.wcs, param)[i] = getattr(wcs_2d.wcs, param)[i]
    
    # Configura o eixo espectral (filtros)
    wcs_3d.wcs.crpix[2] = 1
    wcs_3d.wcs.crval[2] = 0
    wcs_3d.wcs.cdelt[2] = 1
    wcs_3d.wcs.ctype[2] = 'FILTER'
    wcs_3d.wcs.cunit[2] = ''
    
    # Cria o header do cubo
    cube_header = wcs_3d.to_header()
    cube_header['NAXIS'] = 3
    cube_header['NAXIS1'] = cube.shape[2]  # Largura
    cube_header['NAXIS2'] = cube.shape[1]  # Altura
    cube_header['NAXIS3'] = cube.shape[0]  # Número de filtros
    
    # Adiciona informações dos filtros no header
    for i, filt in enumerate(filter_names):
        cube_header[f'FILT{i+1:03d}'] = filt
    
    # Salva o cubo completo
    hdu = fits.PrimaryHDU(cube, header=cube_header)
    hdu.writeto(output_filename, overwrite=True)
    print(f"\nCubo principal salvo como '{output_filename}'")
    
    return cube, cube_header

# Corta o cubo principal em regiões menores
def create_cutouts(cube, cube_header, regions):
    for name, x_start, x_end, y_start, y_end in regions:
        # Verifica se os limites estão dentro das dimensões do cubo
        if (x_end > cube.shape[2] or y_end > cube.shape[1] or 
            x_start < 0 or y_start < 0):
            print(f"\nAviso: Região {name} fora dos limites. Ignorando...")
            continue
        
        cube_cut = cube[:, y_start:y_end, x_start:x_end]
        new_nx = x_end - x_start
        new_ny = y_end - y_start

        # Atualiza o header para o recorte
        cut_header = cube_header.copy()
        cut_header['NAXIS1'] = new_nx
        cut_header['NAXIS2'] = new_ny
        cut_header['CRPIX1'] = cut_header['CRPIX1'] - x_start
        cut_header['CRPIX2'] = cut_header['CRPIX2'] - y_start

        # Salva o cubo recortado
        filename = f'PHANGS_cube_{name}.fits'
        hdu_cut = fits.PrimaryHDU(cube_cut, header=cut_header)
        hdu_cut.writeto(filename, overwrite=True)
        print(f"Cubo recortado '{filename}' salvo com sucesso!")

def main():
    # Procura o diretório onde estão os FITS
    loc = os.path.expanduser("~/Desktop/Capivara_mestrado/Input/PHANGS/phangs_hst/ngc1087")
    os.chdir(loc)
    file_list = [f for f in os.listdir() if f.endswith('.fits')]
    
    # Processa os arquivos FITS
    fits_files = [(f, f.split('_')[5]) for f in file_list if f.startswith('hlsp_phangs-hst_hst_wfc3-uvis_ngc1087_')]
    
    # 1. Carrega a imagem de referência
    ref_file = fits_files[0][0]
    with fits.open(ref_file) as hdul_ref:
        ref_data = hdul_ref[0].data
        ref_header = hdul_ref[0].header
        y_size, x_size = ref_data.shape
        
        # Definir região de recorte (200x200 pixels)
        cut_size = 100
        x_center, y_center = x_size // 2, y_size // 2
        x_start, x_end = x_center - cut_size, x_center + cut_size
        y_start, y_end = y_center - cut_size, y_center + cut_size
        
        # Recorte da referência
        ref_data_cut = ref_data[y_start:y_end, x_start:x_end]
        ref_header_cut = ref_header.copy()
        ref_header_cut['NAXIS1'] = cut_size * 2
        ref_header_cut['NAXIS2'] = cut_size * 2
    
    # 2. Processa cada arquivo
    aligned_images = []
    filter_names = []
    
    for file, filt in tqdm(fits_files, desc="Processando imagens"):
        print(f"\nProcessando {filt}...")
        log_memory_usage()
        
        try:
            with fits.open(file) as hdul:
                if len(hdul) < 1 or hdul[0].data is None:
                    print(f"Aviso: '{file}' sem dados válidos")
                    continue
                
                # Recorte antes da reprojeção
                data_cut = hdul[0].data[y_start:y_end, x_start:x_end]
                wcs_in = WCS(hdul[0].header)
                
                # Reprojeção
                data_aligned, _ = reproject_interp(
                    (data_cut, wcs_in),
                    ref_header_cut
                )
                
                aligned_images.append(data_aligned)
                filter_names.append(filt)
                
                # Salvar imagem individual alinhada
                hdu = fits.PrimaryHDU(data_aligned, header=ref_header_cut)
                hdu.writeto(f"{filt}_aligned_cut.fits", overwrite=True)
                print(f"Arquivo {filt} processado e salvo.")
                
        except Exception as e:
            print(f"Erro processando {file}: {str(e)}")
        
        # Limpa a memória para evitar sobrecarga
        gc.collect()
        log_memory_usage()
    
    # 3. Cria cubo de dados
    if aligned_images:
        cube, cube_header = create_data_cube(
            aligned_images, 
            filter_names, 
            ref_header_cut, 
            ref_data_cut,
            'PHANGS_cube.fits'
        )
        
        # 4. Cria recortes menores
        regions = [
            ('region1', 40, 60, 40, 60),    # x1, x2, y1, y2 (dentro do recorte 100x100)
            ('region2', 60, 80, 40, 60),
            ('region3', 60, 80, 60, 80)
        ]
        create_cutouts(cube, cube_header, regions)
    else:
        print("\nNenhum dado válido para criar o cubo.")

if __name__ == "__main__":
    main()