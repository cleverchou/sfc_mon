import json
from pathlib import Path
import pandas as pd
import os
from scipy.io import arff
import numpy as np

def cpumem_loc_json(out_path):
    continuous_variables = ["Fea%03d" % i for i in range(1, 13)]
    categorical_variables = []
    #targets = ["CPU", "Mem"]
    targets = ["CPU1", "Mem1","CPU1", "Mem2"]
    config_dict = {
        "continuous_variables": continuous_variables,
        "categorical_variables": categorical_variables,
        "targets": targets,
    }

    with open(out_path, "w") as f:
        json.dump(config_dict, f, indent=4)#indent 缩进了4行，更好的阅读


def cpumem_loc_read(base_path):
    #dataset = "f_d1cm.csv"
    dataset = "f_d1cm_d2cm.csv"
    df = pd.read_csv(base_path / dataset)
    # df = train
    df.to_csv(
        os.path.join(base_path, r"cpumem.csv"),
        sep="|",
        index=False,
    )

'''
def indoor_loc_json(out_path):
    continuous_variables = ["WAP%03d" % i for i in range(1, 521)]
    categorical_variables = []
    targets = ["LONGITUDE", "LATITUDE", "FLOOR"]
    config_dict = {
        "continuous_variables": continuous_variables,
        "categorical_variables": categorical_variables,
        "targets": targets,
    }

    with open(out_path, "w") as f:
        json.dump(config_dict, f, indent=4)#indent 缩进了4行，更好的阅读


def indoor_loc_read(base_path):
    train_path = "trainingData.csv"
    test_path = "validationData.csv"
    train = pd.read_csv(base_path / train_path)
    test = pd.read_csv(base_path / test_path)
    df = pd.concat([train, test], ignore_index=True)
    # df = train
    df.to_csv(
        os.path.join(base_path, r"indoorloc.csv"),
        sep="|",
        index=False,
    )


def sgemm_json(out_path):
    continuous_variables = ["V-%02d" % i for i in range(1, 15)]
    categorical_variables = []
    targets = ["V-15", "V-16", "V-17", "V-18"]
    config_dict = {
        "continuous_variables": continuous_variables,
        "categorical_variables": categorical_variables,
        "targets": targets,
    }
    with open(out_path, "w") as f:
        json.dump(config_dict, f, indent=4)


def sgemm_read(base_path):
    dataset = "sgemm_product.csv"
    df = pd.read_csv(base_path / dataset)
    df.columns = ["V-%02d" % i for i in range(1, 19)]
    df["V-15"] = np.log(df["V-15"])
    df["V-16"] = np.log(df["V-16"])
    df["V-17"] = np.log(df["V-17"])
    df["V-18"] = np.log(df["V-18"])

    df.to_csv(
        os.path.join(base_path, r"sgemm.csv"),
        sep="|",
        index=False,
    )


def music_origin_read(base_path):
    dataset = "default_features_1059_tracks.txt"
    df = pd.read_csv(base_path / dataset, header=None)
    df.columns = ["V-%02d" % i for i in range(1, 71)]
    df.to_csv(
        os.path.join(base_path, r"music_origin.csv"),
        sep="|",
        index=False,
    )


def music_origin_json(out_path):
    continuous_variables = ["V-%02d" % i for i in range(1, 69)]
    categorical_variables = []
    targets = ["V-69", "V-70"]
    config_dict = {
        "continuous_variables": continuous_variables,
        "categorical_variables": categorical_variables,
        "targets": targets,
    }
    with open(out_path, "w") as f:
        json.dump(config_dict, f, indent=4)


def mulan_read_json(base_path, config_path):#mulan测试集
    dataset_names = [
        "scm1d",
        "scm20d",
    ]
    n_targets = [16, 16]
    datasets = list(zip(dataset_names, n_targets))
    for ds_name, n_target in datasets:
        print(ds_name)
        new_base_path = base_path[:-6] + ds_name + "/"
        if not os.path.exists(new_base_path):
            os.makedirs(new_base_path)
        new_base_file = new_base_path + ds_name + ".csv"
        data = arff.loadarff(base_path + ds_name + ".arff")
        df = pd.DataFrame(data[0])
        df = df.fillna(df.median(axis=0))
        df_col = len(df.columns) + 1
        df.columns = ["V-%03d" % i for i in range(1, df_col)]
        df.to_csv(
            os.path.join(new_base_file), sep="|", index=False,
        )
        df_var = df_col - n_target
        continuous_variables = ["V-%03d" % i for i in range(1, df_var)]
        categorical_variables = []
        targets = ["V-%03d" % i for i in range(df_var, df_var + n_target)]
        config_dict = {
            "continuous_variables": continuous_variables,
            "categorical_variables": categorical_variables,
            "targets": targets,
        }
        out_path = new_base_path + config_path
        with open(out_path, "w") as f:
            json.dump(config_dict, f, indent=4)

'''
if __name__ == "__main__":
    config_path = "config.json"

    # cpu_mem Localization
    #base_path = Path("../input/docker1/")
    base_path = Path("../input/sfc/")
    cpumem_loc_read(base_path)
    cpumem_loc_json(base_path / config_path)

    # Mulan
    #base_path = "../input/mulan/"
    #mulan_read_json(base_path, config_path)

    '''
    # Indoor Localization
    base_path = Path("../input/indoorloc/")
    indoor_loc_read(base_path)
    indoor_loc_json(base_path / config_path)

    # sgemm
    base_path = Path("../input/sgemm/")
    sgemm_read(base_path)
    sgemm_json(base_path / config_path)

    # music_origin
    base_path = Path("../input/music_origin/")
    music_origin_read(base_path)
    music_origin_json(base_path / config_path)

    # Mulan
    base_path = "../input/mulan/"
    mulan_read_json(base_path, config_path)
    '''
