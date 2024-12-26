This project uses SIFT feature matching and homography transformation to stitch multiple images together. I first used SIFT descriptors to match features between two images with different angles,
and then performed RANSAC algorithm to find the best homography transformation between two images. With the obtained transformation, I transformed images to stitch it with another image to 
create a canvas with all images, as shown in the jpg files.
