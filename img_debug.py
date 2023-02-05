import cv2


class ImgDebug:
    scale = 0.8
    title = 'ImgDebug'
    enabled = False

    @staticmethod
    def display(img):
        if not ImgDebug.enabled:
            return
        resized = cv2.resize(img, (round(img.shape[1] * ImgDebug.scale), round(img.shape[0] * ImgDebug.scale)),
                             interpolation=cv2.INTER_AREA)
        cv2.imshow(ImgDebug.title, resized)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def enable():
        ImgDebug.enabled = True

    @staticmethod
    def disable():
        ImgDebug.enabled = False
