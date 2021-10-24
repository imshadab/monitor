# Module: Monitor
# Author: Shadab Khan <shadab.iith@gmail.com>
# License: MIT

"""Jupyter Real-time performance monitoring tool

This script allows the user to monitor their system performance in real-time within
jupyter notebook cell without disturbing any other thing in the Notebook. The code for
this utility continues to run in a different thread thus the main thread is left unblocked.


It accepts input in the form of string i.e, "cpu" or "gpu"

It requires that `ipywidgets and psutil` to be installed.

"""

__author__ = "Shadab Khan"
__version__ = "1.0.0"

import ipywidgets as widgets
from Ipython.core.magic import register_line_magic
from Ipython.display import display
import os
import platform
from datetime import datetime
import psutil
import threading
import time

global dead 

dead = False

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_user_details():
    info = ""
    info += "=" * 26 + "<strong>System Information</strong>" + "=" * 26 + "</br>"
    uname = platform. uname()
    now_time = datetime.now().strftime("%b %d %Y %H:%M:%S")
    info += f"""<div class="row">
    <div class="col-md-5">
    """
    info += f"<strong>System:</strong> {uname.system}" + "</br>"
    info += f"<strong>Node Name:</strong> {uname.node}" + "</br>"
    info += f"<strong>Release:</strong> {uname.release}" + "</br>"
    info += "</div>"

    info += f"""<div class="col-md-6">"""
    info += f"<strong>Version:</strong> {uname.version}" + "</br>"
    info += f"<strong>Machine:</strong> {uname.machine}" + "</br>"
    info += f"<strong>Processor:</strong> {uname.processor}" + "</br>"
    info += "</div></div>"

    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    bt = bt.strftime("%b %d %Y %H:%M:%S")
    info += f"""<div class="row">
    <div class="col-md-5">
    """
    info += f"<strong>Boot Time:</strong> {bt}" + "</br>"
    info += "</div>"
    info += f"""<div class="col-md-6">"""
    info += f"<strong>Current CPU Time:</strong> {now_time}" + "</br>"
    info += "</div></div>"
    return info

def get_cpu_usage():
    info = ""
    info += "=" * 27 + "<strong>CPU Information</strong>" + "=" * 27 + "</br>"
    # number of cores
    cpufreq = psutil.cpu_freq()
    info += f"""<div class="row">
    <div class="col-md-5">
    """
    info += f"<strong>Max Frequency:</strong> {cpufreq.max:.2f}Mhz" + "</br>"
    info += f"<strong>Min Frequency:</strong> {cpufreq.min:.2f}Mhz" + "</br>"
    info += f"<strong>Current Frequency:</strong> {cpufreq.current:.2f}Mhz" + "</br>"
    info += "</div>"


    info += f"""<div class="col-md-6">"""
    info += f"<strong>Physical cores:</strong>" + str(psutil.cpu_count(logical=False)) + "</br>"
    info += f"<strong>Total cores:</strong>" + str(psutil.cpu_count(logical=False)) + "</br>"
    
    # CPU frequencies
    info += "</div></div>"
    return info

def get_core_usage():
    info = "" 
    # CPU Usage
    info += "=" * 54 + "<strong> CPU Utilization </strong>" + "=" * 54
    info += "" + f"</br><strong>Total CPU Usage: {psutil.cpu_percent()}% </strong>" + "</br>"
    info += """<table class="table table-striped table-dark">
<thody><tr>"""
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        if i % 10==0 and i!=0:
            info +="</tr><tr>"
            info +=f'<td><strong>Core {i+1}</strong>: {percentage}%</td>'
        else:
            info +=f'<td><strong>Core {i+1}</strong>: {percentage}%</td>'
    
    info +="</tr></tbody></table>"
    return info

def get_memory_usage():
    info = ""
    info += "=" * 13 + "<strong>Memory Utilization</strong>" + "=" * 13 + "</br>"
    # get the memory details
    svmem = psutil.virtual_memory()
    info += f"""<div class="row">
            <div class="col-md-6">"""
    info += f"<strong>Total: </strong>{get_size(svmem.total)}" + "</br>"
    info += f"<strong>Available: </strong>{get_size(svmem.available)}" + "</br>"
    info += "</div>"


    info += f"""<div class="col-md-6">"""
    info += f"<strong>Used: </strong>{get_size(svmem.used)}" + "</br>"
    info += f"<strong>Percentage: </strong>{svmem.percent}%" + "</br>"
    info += "</div></div>"

    return info, svmem.available

def get_gpu_info():
    ns = os.popen('nvidia-smi')
    lines = ns.readlines()

    info = ""
    if len(lines) > 8:
        info += "=" * 15 + "<strong>GPU Utilization</strong>" + "=" * 15 + "</br>"
        memory_list = lines[8].split("|")[2].strip().split("/")
        usage = memory_list[0].strip().split("M")[0] # + " Mb"
        total = memory_list[1].strip().split("M")[0] # + " Mb"
        available = int(total) - int(usage)
        percentage = (int(usage) / int(total)) * 100
        info += f"""<div class="row">
            <div class="col-md-6">"""
        info += f"<strong>Total: </strong>{total}" + " Mb</br>"
        info += f"<strong>Free: </strong>{available}" + " Mb</br>"
        info += "</div>"

        info += f"""<div class="col-md-6">"""
        info += f"<strong>Used: </strong>{usage}" + " Mb</br>"
        info += f"<strong>Percentage: </strong>{percentage:.2f}" + "%</br>"
        info += "</div></div>"
        return info

def get_notebook_info(available_mem):
    process = psutil.Process(os.getpid())
    used_mem = process.memory_info()[0]
    total_mem = available_mem - used_mem
    available = total_mem - used_mem
    percentage = (used_mem / total_mem) * 100
    info = ""
    info += "=" * 13 + "<strong>Notebook Utilization</strong>" + "=" * 13 + "</br>"

    info += f"""<div class="row">
            <div class="col-md-6">"""
    info += f"<strong>Total Available: </strong>{get_size(total_mem)}" + "</br>"
    info += f"<strong>Free: </strong>{get_size(available)}" + "</br>"
    info += "</div>"

    info += f"""<div class="col-md-6">"""
    info += f"<strong>Used: </strong>{get_size(used_mem)}" + "</br>"
    info += f"<strong>Percentage: </strong>{percentage:.2f}" + "%</br>"
    info += "</div></div>"
    return info


def get_all_info(gpu_required=False):
    user_details = get_user_details()
    gpu_usage = ""
    cpu_usage = get_cpu_usage()

    cpu_core_usage = get_core_usage()
    memory_usage, avail_mem = get_memory_usage()
    notebook_usage = get_notebook_info(avail_mem)
    if gpu_required:
        gpu_usage = get_gpu_info()
        if gpu_usage is None:
            gpu_usage = ""

    final_html = f"""
    <div class="container-fluid new">
    <div class="col-md-7">
    {user_details}
    {cpu_usage}
    </div>
    <div class="col-md-5">
    {memory_usage}
    {gpu_usage}
    {notebook_usage}
    </div>
    </div>
    <div class="row'>
    <div class="col-md-12">
        {cpu_core_usage}
    </div>
    """
    return final_html

def monitor_system(out, gpu_required):
    while not dead:
        out.value = get_all_info(gpu_required)

def load_ipython_extension(ipython):
    @register_line_magic("monitor")
    def monitor(line):
        gpu_required = False
        if line.strip().lower() == 'gpu':
            gpu_required = True
        elif line.strip().lower() == 'cpu':
            gpu_required = False
        
        out = widgets.HTML(layout = widgets.Layout(height='510px'))
        display(out)
        out.value = """<br/><p align="center">
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxWbhXoi7czRn8Esk6N3hwWTxGj71PaJw80zBdj32Xwa6zoVDP&s=50x10" />
            <br/><br/><h1 align="center">Real time Performance Monitoring Tool 💻</h1>
            </p>"""
        time.sleep(1)

        out.value = """<br/><p align="center">
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxWbhXoi7czRn8Esk6N3hwWTxGj71PaJw80zBdj32Xwa6zoVDP&s=50x10" />
        <br/><br/><h1 align="center">Loading Informations....🕑 </h1>
        </p>"""

        time.sleep(0.65)

        out.value = """<br/><p align="center">
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxWbhXoi7czRn8Esk6N3hwWTxGj71PaJw80zBdj32Xwa6zoVDP&s=50x10" />
        <br/><br/><h1 align="center">Information Loaded Succesfully <span style="color:green">✔</span> </h1>
        </p>"""

        time.sleep(0.5)

        threading.Thread(target=monitor_system, args=(out, gpu_required)).start()








