import os
import platform
import re
from datetime import timedelta, datetime
from pathlib import Path

DEBUG = False
VERSION = "2.1.0"


def _exc(cmd):
    print(f'executing: "{cmd}"')

    res = os.popen(cmd).read()
    if DEBUG:
        print(res)

    if "Done Saving Data" in res:
        return True
    return False


def get_data(
        addr_exe: Path,
        addr_ini: Path,
        addr_dest: Path,
        file_datetime: datetime,
        start_time: str,
        with_header_data=False,
):
    addr_dest = Path(
        f'{addr_dest / ("out." + file_datetime.strftime("%Y%m%d"))}.csv.tmp'
    )
    tomorrow = file_datetime + timedelta(days=1)
    start_time = datetime.combine(
        file_datetime.date(), datetime.strptime(start_time, "%H:%M").time()
    )

    while start_time < tomorrow:
        if _exc(
                f'cd {addr_ini.parent} && '
                f'{"wine" if platform.system() == "Linux" else ""} {addr_exe} '
                f'-w {addr_ini} -o {addr_dest} {"" if with_header_data else "-n"} -T '
                f'{start_time.strftime("%m%d%y_%H%M")} {int((tomorrow - start_time).total_seconds() / 60)}'
        ):
            return addr_dest

        print(f"could not find {start_time}")
        start_time = start_time + timedelta(minutes=1)


def convert(
        addr_file: Path,
        addr_dest: Path = None,
        addr_conf: Path = None,
        addr_exe: Path = None,
        addr_ini: Path = None,
        start_time: str = "00:01",
        print_=print,
        with_header_data=False,
):
    # region check inputs
    if not (addr_file.exists() and addr_file.is_file()):
        print_("err", f"not found or not a file: {addr_file}")
        return

    addr_base = Path(os.path.abspath(__file__)).parent
    addr_dest = addr_dest or addr_base / "output"
    addr_conf = addr_conf or addr_base / "conf"
    addr_exe = addr_exe or addr_base / "drf2txt.exe"
    addr_ini = addr_ini or addr_conf / "Winsdr.ini"

    if not addr_dest.exists():
        os.makedirs(addr_dest, exist_ok=True)

    if not (addr_conf.exists() and addr_conf.is_dir()):
        print_("err", f"not found or not a directory: {addr_conf}")
        return
    if not (addr_exe.exists() and addr_exe.is_file()):
        print_("err", f"not found or not a file: {addr_exe}")
        return
    if not (addr_ini.exists() and addr_ini.is_file()):
        print_("err", f"not found or not a file: {addr_ini}")
        return
    # endregion

    # region get file date from file name
    try:
        file_datetime = re.findall("sys\d\.(\d{8})\.dat", addr_file.name)[0]
    except:
        print_("err", f'file name must be like "sys1.20210101.dat": {addr_file}')
        return
    file_datetime = datetime(
        int(file_datetime[:4]), int(file_datetime[4:6]), int(file_datetime[6:])
    )

    # endregion

    # region normalize .ini file
    with open(addr_ini, "r") as f:
        ini_data_org = f.read()

    ini_data = []
    for line in ini_data_org.strip().split("\n"):
        if line.startswith("RecordPath="):
            line = f"RecordPath={addr_file.parent}" + ("/" if platform.system() == "Linux" else "\\")
        # if line.startswith("ChanFile"):
        #     b, a = line.split("=")
        #     line = f"{b}={addr_conf / a}"

        ini_data.append(line)
    ini_data = "\n".join(ini_data)
    addr_ini = Path(f"{addr_ini}.tmp")
    with open(addr_ini, "w") as f:
        f.write(ini_data)
    # endregion

    print_("succ", "translating ...")
    addr_dest = get_data(
        addr_exe, addr_ini, addr_dest, file_datetime, start_time, with_header_data
    )
    if addr_dest is None:
        print_("err", f"could not get any data from {addr_file}")
        return
    else:
        new = addr_dest.parent / addr_dest.name.replace(".tmp", "")
        if new.exists():
            os.remove(new)
        addr_dest = addr_dest.rename(new)

    print_("succ", "translated")

    return addr_dest
