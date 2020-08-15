import json
from os import listdir, makedirs
from os.path import isfile, join
from time import time

from flask import Flask, render_template, request

app = Flask(__name__, static_folder="", template_folder="")


@app.route("/")
@app.route("/index")
def index():
    while app.config["TASK"].within_range(app.config["CURRENT_SUBTASK_INDEX"]):
        left_image_path, right_image_path = app.config["TASK"].subtask(
            app.config["CURRENT_SUBTASK_INDEX"])
        if (left_image_path is None or right_image_path is None
                or not isfile(left_image_path) or not isfile(right_image_path)):
            app.config["TASK"].annotate(
                app.config["CURRENT_SUBTASK_INDEX"], -1)
            app.config["CURRENT_SUBTASK_INDEX"] += 1
            continue
        return render_template(
            "index.html",
            current_subtask_num=app.config["CURRENT_SUBTASK_INDEX"] + 1,
            task_length=len(app.config["TASK"].subtask_list),
            left_image=left_image_path,
            right_image=right_image_path,
            config=app.config["CONFIG_DICT"]
        )
    return "DONE"


@app.route("/annotate")
def annotate():
    label = int(request.args.get("label"))
    app.config["TASK"].annotate(app.config["CURRENT_SUBTASK_INDEX"], label)
    app.config["CURRENT_SUBTASK_INDEX"] += 1
    return ""


def id_to_filepath(id):
    return app.config["IMAGE_DIR"] + app.config["IMAGE_FORMAT_STRING"].format(id)


class Task:
    def __init__(self, task_name, subtask_list):
        self.task_name = task_name
        self.subtask_list = subtask_list

    def subtask(self, index):
        if self.within_range(index):
            left_id = self.subtask_list[index].get("left", None)
            right_id = self.subtask_list[index].get("right", None)
            if left_id is None or right_id is None:
                return None, None
            else:
                left_filepath = id_to_filepath(left_id)
                right_filepath = id_to_filepath(right_id)
                return left_filepath, right_filepath
        else:
            return None

    def annotate(self, index, label):
        if self.within_range(index):
            self.subtask_list[index]["timestamp"] = int(time())
            self.subtask_list[index]["label"] = label
            result_file = app.config["RESULT_DIR"] + \
                self.task_name[:-5] + "_annotated.json"
            with open(result_file, "w") as file:
                json.dump(self.subtask_list, file)

    def within_range(self, index):
        return 0 <= index < len(self.subtask_list)


def prompt_for_task():
    while(True):
        print("Tasks:")
        task_names = [
            f for f in listdir(app.config["TASK_DIR"])
            if isfile(app.config["TASK_DIR"] + f)
        ]
        for i, task_name in enumerate(task_names):
            print(f"({i + 1})", task_name)

        try:
            task_index = int(input("\nPlease select a task: ")) - 1
        except ValueError:
            print("Please enter an integer\n\n")
            continue

        if task_index < 0 or task_index >= len(task_names):
            print(
                f"Please enter an integer between 1 and {len(task_names)}\n\n")
            continue

        task_name = task_names[task_index]
        unannotated_path = app.config["TASK_DIR"] + task_name
        annotated_path = app.config["RESULT_DIR"] + \
            task_name[:-5] + "_annotated.json"
        task_path = annotated_path if isfile(
            annotated_path) else unannotated_path
        with open(task_path) as task:
            subtask_list = json.load(task)
            task = Task(task_name, subtask_list)
            return task


def get_last_unannotated_index():
    annotated_file_path = app.config["RESULT_DIR"] + \
        app.config["TASK"].task_name[:-5] + "_annotated.json"
    if isfile(annotated_file_path):
        with open(annotated_file_path) as annotated_file:
            subtask_list = json.load(annotated_file)
            for index, subtask in enumerate(subtask_list):
                if subtask.get("label") is None:
                    return index
            return len(subtask_list)
    return 0


def load_config():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        def format_dir(path): return path if path[-1] == "/" else path + "/"
        app.config["IMAGE_DIR"] = format_dir(config.get("image_dir", ""))
        app.config["RESULT_DIR"] = format_dir(config.get("result_dir", ""))
        app.config["TASK_DIR"] = format_dir(config.get("task_dir", ""))
        app.config["IMAGE_FORMAT_STRING"] = config.get(
            "image_format_string", "")
        app.config["CONFIG_DICT"] = config

        makedirs(app.config["IMAGE_DIR"], exist_ok=True)
        makedirs(app.config["RESULT_DIR"], exist_ok=True)
        makedirs(app.config["TASK_DIR"], exist_ok=True)

    app.config["TASK"] = prompt_for_task()
    app.config["CURRENT_SUBTASK_INDEX"] = get_last_unannotated_index()


def main():
    load_config()
    app.run()


if __name__ == "__main__":
    main()
