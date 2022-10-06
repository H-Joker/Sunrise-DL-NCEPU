import torch
from utils import target_decode, NonMaximalSuppression
from object_detection.data.data_factory import data_factory
from object_detection.data.data_loader import VOCDataset
from tools import visualize
from torchvision.transforms import Resize


def detect(args, model, device):
    print("----------loading test set--------")
    pred_set, pred_loader = data_factory(args, flag='pred')
    map_dict = pred_set.map_dict
    map_dict = {v: k for k, v in map_dict.items()}
    model.load_state_dict(torch.load(f"./checkpoints/{args.model_path}"))
    model.eval()
    with torch.no_grad():
        for i, (image, target, size) in enumerate(pred_loader):
            size = size.squeeze(0)
            image = image.float().to(device)
            target = target.float().to(device)
            output = model(image)
            box_corner, class_label, confidence, class_score = \
                target_decode(output.squeeze(0), args.threshold, args.S, args.B, args.size[0], args.size[1])
            boxes, classes, probs = NonMaximalSuppression(box_corner, class_label, confidence, class_score, threshold=0.1)
            image = image.cpu().squeeze(0)
            class_label = [map_dict[i] for i in classes.cpu().numpy()]
            # if i % 20 == 0:
            image = Resize((size[1], size[0]))(image)
            boxes[:, [1, 3]] *= size[1] / args.size[1]
            boxes[:, [0, 2]] *= size[0] / args.size[0]
            visualize(image, boxes.cpu().numpy(), class_label, probs.cpu().numpy(), i)


