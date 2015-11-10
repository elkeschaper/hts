import sys
from hts.data_tasks import qc_detect_data_issues, qc_knitr, qc_matplotlib

def perform_task(run, task_name, *args, **kwargs):

    name_list = task_name.split(".")
    task_method = sys.modules[__name__]
    for i in name_list:
        task_method = getattr(task_method, i)

    result = task_method(run, *args, **kwargs)
    return result