from detectron2.utils.logger import setup_logger
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from torchvision.ops import box_area
setup_logger()
# Load here your Detection model
# The chosen detector model is "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"
# because this particular model has a good balance between accuracy and speed.
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
DET_MODEL = DefaultPredictor(cfg)


def get_vehicle_coordinates(img):
    """
    This function will run an object detector over the the image, get
    the vehicle position in the picture and return it.

    Many things should be taken into account to make it work:
        1. Current model being used can detect up to 80 different objects,
           we're only looking for 'cars' or 'trucks', so you should ignore
           other detected objects.
        2. The object detector may find more than one vehicle in the picture,
           you must then, choose the one with the largest area in the image.
        3. The model can also fail and detect zero objects in the picture,
           in that case, you should return coordinates that cover the full
           image, i.e. [0, 0, width, height].
        4. Coordinates values must be integers, we're making reference to
           a position in a numpy.array, we can't use float values.

    Parameters
    ----------
    img : numpy.ndarray
        Image in RGB format.

    Returns
    -------
    box_coordinates : list
        Tuple having bounding box coordinates as (left, top, right, bottom).
        Also known as [x1, y1, x2, y2].
    """

    box_coordinates = (0, 0, img.shape[1], img.shape[0])
    outputs = DET_MODEL(img)
    cars_ident = (outputs["instances"].pred_classes == 2) | (outputs["instances"].pred_classes == 7)
    if outputs["instances"][cars_ident].pred_classes.size()[0] > 0:
      sel_arg = box_area(outputs["instances"][cars_ident].pred_boxes.tensor).argmax().item()
      car_box = outputs["instances"][cars_ident].pred_boxes.tensor[sel_arg]
      box_coordinates = (int(car_box[0].item()), int(car_box[1].item()), int(car_box[2].item()), int(car_box[3].item()))

    return box_coordinates
