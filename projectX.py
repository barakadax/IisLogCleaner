import ctypes, sys, subprocess, os, json
from ntpath import join

def get_start_path():
    file = open("path_to_program", "rb")
    info = file.readline()
    file.close()
    return info.decode("utf-8")

def del_from_dir(error_log, program_path, local_logs_dir):
    files_and_dirs = os.listdir(program_path + local_logs_dir)
    for file_or_dir in files_and_dirs:
        if os.path.isdir(program_path + local_logs_dir + '\\' + file_or_dir):
            del_from_dir(error_log, program_path, local_logs_dir + '\\' + file_or_dir)
        else:
            try:
                os.remove(program_path + local_logs_dir + '\\' + file_or_dir)
            except OSError:
                error_log.append(program_path + local_logs_dir + '\\' + file_or_dir)

def get_dir_to_del_logs_from():
    file = open("foldersToDeleteFrom.json", "rb")
    data = json.load(file)
    file.close()
    return data

def delete_all_log(error_log):
    program_path = get_start_path()
    local_logs_paths = get_dir_to_del_logs_from()
    for local_logs_dir in local_logs_paths:
        del_from_dir(error_log, program_path, local_logs_dir)    

def iis_command(command):
    try:
        return subprocess.check_output(['iisreset', f'{command}']).decode('utf-8')
    except subprocess.CalledProcessError as error:
        return error.output.decode('utf-8')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def save_error_log(error_log):
    print("Check \"errorLog.log\" for files that couldn't be deleted.\n")
    file = open("errorLog.log", "wb")
    file.write(bytes('\n'.join(error_log), "utf-8"))
    file.close()

if __name__ == "__main__":
    if is_admin():
        error_log = []
        error_log.append("Files that couldn't delete:")
        iis_command("/stop")
        print(iis_command("/status"))
        delete_all_log(error_log)
        iis_command("/start")
        print(iis_command("/status"))
        if (len(error_log) != 1):
            save_error_log(error_log)
        print("### DONE ###\npress ENTER to continue or close the window.")
        input()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
