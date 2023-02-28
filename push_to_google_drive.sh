# Copy data from local hard drive to Google Drive where it can be used from Google Colab
#rclone copy --drive-root-folder-id=1-C6OpKVM73g2lCEpaoWZkB_-Y8-xKwfM ../output/ alaska:/
#rclone copy --drive-root-folder-id=11gO6RZqpkbQSqLbXqzzqK9-h6ZOAnWZ5 ../data/ alaska:/

##rclone copy --drive-root-folder-id=1SXyjY1f_bMpylhKxe47nB3fU4hvKjY64 --exclude=.git/** uafgi/ alaska:/uafig
##rclone copy --drive-root-folder-id=1SXyjY1f_bMpylhKxe47nB3fU4hvKjY64 --exclude=.git/** sitka_salmon/ alaska:/sitka_salmon

rclone copy --drive-root-folder-id=1SXyjY1f_bMpylhKxe47nB3fU4hvKjY64 uafgi/ alaska:/uafgi
rclone copy --drive-root-folder-id=1SXyjY1f_bMpylhKxe47nB3fU4hvKjY64 sitka_salmon/ alaska:/sitka_salmon
