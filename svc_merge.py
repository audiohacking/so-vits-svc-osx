import os
import torch
import argparse
import collections


def load_model(checkpoint_path):
    assert os.path.isfile(checkpoint_path)
    checkpoint_dict = torch.load(checkpoint_path, map_location="cpu")
    saved_state_dict_g = checkpoint_dict["model_g"]
    saved_state_dict_d = checkpoint_dict.get("model_d", None)
    return saved_state_dict_g, saved_state_dict_d


def save_model(state_dict_g, state_dict_d, checkpoint_path):
    if state_dict_d is None:
        torch.save({'model_g': state_dict_g}, checkpoint_path)
    else:
        torch.save({'model_g': state_dict_g, 'model_d': state_dict_d}, checkpoint_path)


def average_model(model_list, weights=None):
    if weights is None:
        weights = [1.0] * len(model_list)  # Default equal weights if not provided
    
    if len(model_list) != len(weights):
        raise ValueError("Number of models and weights must be the same.")
    
    model_keys = list(model_list[0].keys())
    model_average = collections.OrderedDict()
    
    total_weight = sum(weights)
    
    for key in model_keys:
        key_sum = 0
        for i, model in enumerate(model_list):
            key_sum += model[key] * (weights[i] / total_weight)
        model_average[key] = key_sum
    
    return model_average
#   ss_list = []
#   ss_list.append(s1)
#   ss_list.append(s2)
#   ss_merge = average_model(ss_list)


def merge_model(model1, model2, rate):
    model_keys = model1.keys()
    model_merge = collections.OrderedDict()
    for key in model_keys:
        key_merge = rate * model1[key] + (1 - rate) * model2[key]
        model_merge[key] = key_merge
    return model_merge


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m1', '--model1', type=str, required=True)
    parser.add_argument('-m2', '--model2', type=str, required=True)
    parser.add_argument('-r1', '--rate', type=float, required=True)
    args = parser.parse_args()

    print(args.model1)
    print(args.model2)
    print(args.rate)

    assert args.rate > 0 and args.rate < 1, f"{args.rate} should be in range (0, 1)"
    s1_g, s1_d = load_model(args.model1)
    s2_g, s2_d = load_model(args.model2)

    merge_g = merge_model(s1_g, s2_g, args.rate)
    
    # Merge discriminator models if both exist
    merge_d = None
    if s1_d is not None and s2_d is not None:
        merge_d = merge_model(s1_d, s2_d, args.rate)
    
    save_model(merge_g, merge_d, "sovits5.0_merge.pth")
