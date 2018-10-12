import os
import sys
from PIL import Image


class File():
    def __init__(self,filename,filepath):
        self.filepath=filepath
        self.filetype=''
        self.filename=filename

        try:
            i = filename.rindex('.')
            self.filetype=filename[i+1:]
            self.filename=filename[:i]
        except Exception as e:
            print('no type')
            pass

    def print(self):
        print("%s.%s"%(self.filename,self.filetype))


def mixPNA(pngfile,pnafile):
    img1=Image.open(pngfile)
    img2=Image.open(pnafile)
    img1=img1.convert('RGBA')
    img2=img2.convert('L')
    img1.putalpha(img2)

    img1.save(pngfile)

def main(work_dir):
    pngs =[]
    pngname = []
    pnas =[]

    for parent, dirnames, filenames in os.walk(work_dir,  followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent, filename)

            print('%s' % file_path)

            f = File(filename,file_path)

            if f.filetype == 'png':
                pngs.append(f)
                pngname.append(f.filename)
            elif f.filetype == 'pna':
                pnas.append(f)

    print('*--------------------------------------')
    for pna in pnas:
        if pna.filename in pngname:
            mixPNA(pngs[pngname.index(pna.filename)].filepath,pna.filepath)
            pna.print()
            os.remove(pna.filepath)


if __name__ == '__main__':
    work_dir = sys.argv[1]
    main(work_dir)