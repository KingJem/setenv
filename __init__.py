import os
import sys

VERSION = "0.0.1"


def get_env_path_list():
    return path_list


def get_real_path(paths):
    return [os.path.expanduser(i) for i in paths]


class Setenv():
    def __init__(self):
        self.env_path_list = [
            "~/.bashrc",
            "/etc/profile",
            "~/.bash_profile",
            "~/.zshrc"
        ]
        self.env_keywords = [
            'export'
        ]
        self.exclude_keywords = ["alias", "if", 'case', "PATH"]

    def add_env_path_list(self, path):
        self.env_path_list.append(path)

    def add_env_keywords(self, keyword):
        self.env_keywords.append(keyword)

    def extra_filter(self, lst: list, reverse: bool):
        s = []
        if reverse:
            for word in lst:
                s.append("grep -v " + word)
        else:
            for word in lst:
                s.append("grep " + word)

        return "|".join(s)

    def readfile(self):
        content_lst = []
        for path in get_real_path(self.env_path_list):
            line = self.get_line_num(path)
            cmd = "cat %s |grep -v -m %s ^#|grep -v ^# -m %s" % (path, line, line)
            cmd = cmd + "|" + self.extra_filter(self.env_keywords, reverse=False)
            cmd = cmd + "|" + self.extra_filter(self.exclude_keywords, reverse=True)
            print(cmd)
            content_lst.extend(self.run_command(cmd))
        return content_lst

    def get_line_num(self, path):
        if os.path.exists(path) and os.path.isfile(path):
            cmd = "wc -l %s|awk '{print $1}'" % (path)
            line_num = self.run_command(cmd)

            return line_num[0].replace("\n", "")

    def run_command(self, cmd):
        res = os.popen(cmd)
        return res.readlines()

    def parse_file_content(self):
        content = self.readfile()
        res = [i.strip().split(" ")[1] for i in content]
        dic = {i.split("=")[0]: i.split("=")[1] for i in res}

        for index, value in dic.items():
            if value.startswith("$"):
                if value.split("$")[1] in dic.keys():
                    dic[index] = dic[value.split("$")[1]]

        return dic

    def setenv(self):
        os.environ.update(self.parse_file_content())


if "win" not in sys.platform:
    set = Setenv()
    set.setenv()
