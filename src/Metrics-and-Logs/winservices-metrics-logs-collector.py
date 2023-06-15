"""
###############################################################
#
# Author: Gelu Liuta
# Creation date: 06.06.2023
# Version: 1.0.0
#
# The code is MVP (minimal viable product) for Windows services observability and should be used accordingly
# Core components: python libraries (win32serviceutil, win32service, time) and the prometheus instrumentation library prometheus_client
###############################################################
"""

import psutil
import logging
import sys
import time

# the libraries are necessary for the windows service
import socket
import win32serviceutil
import servicemanager
import win32event
import win32service

# Prometheus client for instrumentation
# the start_ttp_server is the metrics endpoint which will be scraped by Prometheus server to collect the metrics

from prometheus_client import start_http_server, Gauge

# define the metrics which should be transfered to Prometheus
NUMBER_WIN_SERVICES= Gauge('number_of_win_services', 'Number of windows services to be observed/monitor on  the target server')
NUMBER_WIN_SERVICES_RUNNING= Gauge('number_of_win_services_running', 'Number of windows services which are running')
NUMBER_WIN_SERVICES_STOPPED= Gauge('number_of_win_services_stopped', 'Number of windows services which are stopped')
PERCENT_WIN_SERVICES_RUNNING= Gauge('percent_of_win_services_running', 'Percent of windows services which are running')

# Decorate function with metric.
@NUMBER_WIN_SERVICES.time()
@NUMBER_WIN_SERVICES_RUNNING.time()
@NUMBER_WIN_SERVICES_STOPPED.time()
@PERCENT_WIN_SERVICES_RUNNING.time()


def collect_metrics_logs(services_toBeMonitored):

    logging.basicConfig(filename='D:/ProgramFiles/CAP/WindowsServicesObserver/log/WindowsServiceStatus.log', filemode='a', encoding="UTF-8", level=logging.INFO,
                        format='%(asctime)s | %(process)d | %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    metrics = calculate_metrics(services_toBeMonitored)

    NUMBER_WIN_SERVICES.set(metrics[0])
    NUMBER_WIN_SERVICES_RUNNING.set(metrics[1])
    NUMBER_WIN_SERVICES_STOPPED.set(metrics[2])
    PERCENT_WIN_SERVICES_RUNNING.set(metrics[3])

    time.sleep(5)

def getService(name):

    service = None
    try:
        service = psutil.win_service_get(name)
        service = service.as_dict()
    except Exception as ex:
        print(str(ex))
    return service

def calculate_metrics(services_toBeMonitored):
    """a python function to collect the metrics for running and stopped services in the monitoring scope on a target server
        services_toBeMonitored = a collection of the service names which are to be observed/monitored

        index 0 = Number of Windows services to be observed/monitor on  the target server
        index 1 = Number of Windows services which are running
        index 2 = Number of Windows services which are stopped
        index 3 = Percentage of Windows services which are running
    """

    metrics = [0,0,0,0]

    number_RunningServices = 0
    number_not_RunningServices = 0
    metrics[0] = len(services_toBeMonitored)

    for service_item in services_toBeMonitored:

        service = getService(service_item)
        print(service)
        logEntry = service_item + " | " + service["display_name"] + " | " + service["binpath"] + " | " + service["username"] + " | " + service["start_type"] +" | " + service["status"] + " | " + str(service["pid"]) + " | " + service["description"]
        print (logEntry)

        if service:
            print("service found")
        else:
            print("service not found")

        if service and service['status'] == 'running':
            print("service is running")
            number_RunningServices += 1
            logging.info(logEntry)
        else:
            print("service is not running")
            number_not_RunningServices += 1
            logging.warning(logEntry)

    metrics[1] = number_RunningServices
    metrics[2] = number_not_RunningServices
    metrics[3] = round((number_RunningServices/metrics[0]),2) * 100

    return metrics

class WindowsServicesObserverService:
    """the class where the business logic is implemented"""
    def stop(self):
        """Stop the service"""
        self.running = False

    def run(self):
        """Main service loop. This is where work is done!"""
        self.running = True
        while self.running:
            # time.sleep(10)  # Important work
            servicemanager.LogInfoMsg("Service running...")

            # business logic must be implemented in this section
            list_services_toBeMonitored = ['dhcp', 'filebeat', 'FontCache', 'FrameServer']
            collect_metrics_logs(list_services_toBeMonitored)

class GenericWindowsService(win32serviceutil.ServiceFramework):
    """
    this class is responsible to run the Python module as a Windows Service
    """

    _svc_name_ = "WindowsServicesObserver"
    _svc_display_name_ = "Windows Services Observer"
    _svc_description_ = "Windows Services Observer is a service written in Python which monitors the windows services defined in a list"

    def __init__(self, args):
        '''
        Constructor of the Windows service
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)


    def SvcStop(self):
        '''
        Called when the Windows service is asked to stop
        '''


        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.service_impl.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


    def SvcDoRun(self):

        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.service_impl = WindowsServicesObserverService()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # Run the service
        self.service_impl.run()

if __name__ == '__main__':

    '''    
    start the python module as a Windows service
    this is a standard code to initialize the service
    before initializing the service the http server for prometheus must be started, using a custom port    
    '''

    # while True:
    #     collect_metrics(list_services_toBeMonitored )

    if len(sys.argv) == 1:
        start_http_server(8002)
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(GenericWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(GenericWindowsService)