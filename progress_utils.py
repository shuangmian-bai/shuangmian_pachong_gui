def update_task_completed_amount(progress_popup, task_name, completed_amount):
    """ 更新指定任务的完成量 """
    if task_name in progress_popup.tasks:
        idx = progress_popup.tasks.index(task_name)
        progress_popup.task_completed_amounts[idx] = completed_amount
        progress_popup.update_progress(idx)

def set_task_amount(progress_popup, task_name, task_amount):
    """ 设置指定任务的任务量 """
    if task_name in progress_popup.tasks:
        idx = progress_popup.tasks.index(task_name)
        progress_popup.task_amounts[idx] = task_amount
        progress_popup.update_progress(idx)