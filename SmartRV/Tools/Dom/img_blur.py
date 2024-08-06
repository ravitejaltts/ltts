#Import required Image library
import sys
from PIL import Image, ImageFilter

#Open existing image
OriImage = Image.open(sys.argv[1])
# OriImage.show()
modeImage = OriImage.convert(mode='RGB')

blurImage = modeImage.filter(ImageFilter.GaussianBlur(radius=5))
blurImage.show()
#Save blurImage
blurImage.save('blur.png')
