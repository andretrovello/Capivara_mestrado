install.packages("FITSio")
install.packages("remotes")

remotes::install_github("RafaelSdeSouza/capivara")
library(capivara)

require(capivara)
# Read the MaNGA datacube
#cube <- "/home/andretrovello/Desktop/manga-9000-12702-LOGCUBE.fits"
cube <- "/home/andretrovello/Desktop/Capivara_mestrado/Output/PHANGS_cube_region1.fits"
t<-FITSio::readFITS(cube)

# Apply Capivara segmentation
res <- capivara::segment(t,Ncomp=15)

image(res$cluster_map)
# Plot the segmented region
plot <- plot_cluster(res)
print(plot)

