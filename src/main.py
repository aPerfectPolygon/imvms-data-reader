import os
import re
from datetime import datetime
from glob import glob
from multiprocessing import Pool
from pathlib import Path
from time import sleep

from pytz import timezone

from utils_ import convert, DEBUG

manager_path = Path(__file__).parent
manager_log_dir = manager_path.parent / "log"


def manager_log(*args):
    data = (
            " ".join(
                [
                    str(datetime.now(tz=timezone("Asia/Tehran"))),
                    *[str(item) for item in args],
                ]
            )
            + "\n"
    )
    print(data)

    os.makedirs(manager_log_dir, exist_ok=True)
    addr = manager_log_dir / "manager.log"

    with open(addr, "a") as manager_log_file:
        manager_log_file.write(data)

    if os.path.getsize(addr) > 10000000:
        # rotate
        old_logs = sorted(glob(str(manager_log_dir / "main.log.*")), reverse=True)
        if old_logs:
            backup_id = int(old_logs[0].split("main.log.")[-1]) + 1
        else:
            backup_id = 1
        addr.rename(addr.parent / (addr.name + f".{backup_id}"))


class Worker:
    workers = []

    def __init__(self, d_conf, d_data, d_output, d_log):
        self.d_conf = d_conf
        self.d_data = d_data
        self.d_output = d_output
        self.d_log = d_log

        self.workers.append(self)

    @classmethod
    def check(cls):
        """
        check the structure of the worker`s directory and if it`s ok instantiate the worker

        """
        with open(manager_path / "addresses.txt", 'r') as _f:
            for line in _f.readlines():
                if not line:
                    continue

                d_conf = Path(line.strip())
                d_data = d_conf / "data"
                d_output = d_conf / "output"
                d_log = d_conf / "log"

                if not d_data.exists():
                    manager_log("err", f"path {d_data} not found. (Aborting Worker)")
                    continue

                os.makedirs(d_output, exist_ok=True)
                os.makedirs(d_log, exist_ok=True)

                cls(
                    d_conf=d_conf,
                    d_data=d_data,
                    d_output=d_output,
                    d_log=d_log,
                )

        if not Worker.workers:
            manager_log("err", "No paths to track (Aborting Manager)")
            raise ValueError("No paths to track")

    @classmethod
    def run(cls):
        manager_log()
        manager_log(
            "********************************* STARTUP *********************************"
        )

        cls.check()

        # run the workers in separate processes
        with Pool() as pool:
            pool.map(cls.start, cls.workers)
            pool.close()
            pool.join()

    def start(self):
        self.print_()
        print(self.d_conf)
        self.print_(
            "********************************* STARTUP *********************************"
        )
        sleep(10)
        self.check_old_files()
        self.watch()

    def watch(self):
        while True:
            last_file_old = self._info()
            if not last_file_old:
                self.print_("no .dat files found ...")
                sleep(60)
                continue

            if DEBUG:
                self.print_(f"{last_file_old[0]} watching ...")
            sleep(60)
            last_file_new = self._info()
            if last_file_old == last_file_new:
                self.print_(f"{last_file_old[0]} not_changed")
                continue
            elif last_file_old[0] != last_file_new[0]:
                self.print_(f"{last_file_old[0]} -> {last_file_new[0]} rotated")
                self._convert(last_file_old[0])
                self._convert(last_file_new[0])
            else:
                self.print_(f"{last_file_old[0]} changed")
                self._convert(last_file_new[0])

    def check_old_files(self):
        data_files = self._ls_data()
        output_files = self._ls_output()
        if not data_files:
            return

        output_file_dates = [
            re.findall("out\.(\d{8})\.csv", item.name)[0] for item in output_files
        ]
        for item in data_files:
            if re.findall(r"sys\d\.(\d{8})\.dat", item.name)[0] not in output_file_dates:
                self._convert(item)

    def log_(self, data):
        addr = self.d_log / "main.log"
        with open(addr, mode="a") as f:
            f.write(data)

        if os.path.getsize(addr) > 10000000:
            # rotate
            old_logs = sorted(glob(str(self.d_log / "main.log.*")), reverse=True)
            if old_logs:
                backup_id = int(old_logs[0].split("main.log.")[-1]) + 1
            else:
                backup_id = 1
            addr.rename(addr.parent / (addr.name + f".{backup_id}"))

    def print_(self, *args):
        data = (
                " ".join(
                    [
                        str(datetime.now(tz=timezone("Asia/Tehran"))),
                        *[str(item) for item in args],
                    ]
                )
                + "\n"
        )
        print(data, end="")
        self.log_(data)

    def _convert(self, addr_file: Path, start_time="00:00"):
        return convert(
            addr_file,
            addr_dest=self.d_output,
            addr_conf=self.d_conf,
            start_time=start_time,
            print_=self.print_,
        )

    def _ls_data(self):
        output = []
        for item in sorted(glob(str(self.d_data / "sys*dat")), reverse=True):
            item = Path(item)
            if re.match("sys\d\.\d{8}\.dat", item.name):
                output.append(item)
        return output

    def _ls_output(self):
        output = []
        for item in sorted(glob(str(self.d_output / "out*csv")), reverse=True):
            item = Path(item)
            if re.match("out\.\d{8}\.csv", item.name):
                output.append(item)
        return output

    def _info(self):
        """

        :rtype: tuple[str, int] | None
        """
        files = self._ls_data()
        if not files:
            return None
        return files[0], os.path.getmtime(files[0])


if __name__ == "__main__":
    Worker.run()
