import yaml


def change_version(version):
    with open("config.yml", "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    config["sinol_version"] = version
    with open("config.yml", "w") as config_file:
        yaml.dump(config, config_file)
