remotes::install_github("RafaelSdeSouza/capivara")
library(capivara)

require(capivara)
# Read the MaNGA datacube
cube <- "/home/andretrovello/Desktop/manga-9000-12702-LOGCUBE.fits"
t<-FITSio::readFITS(cube)

# Apply Capivara segmentation
res <- capivara::segment(t,Ncomp=20)

image(res$cluster_map)
# Plot the segmented region
plot <- plot_cluster(res)
print(plot)