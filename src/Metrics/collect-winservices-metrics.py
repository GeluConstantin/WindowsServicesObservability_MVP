import psutil
import logging


def getService(name):

    service = None
    try:
        service = psutil.win_service_get(name)
        service = service.as_dict()
    except Exception as ex:
        print(str(ex))
    return service

def print_to_Logformat(serviceName):

    output = serviceName +" | " + serviceName["display_name"] + serviceName["binpath"]
    print(output)
    return output

if __name__ == '__main__':

    logging.basicConfig(filename='WindowsServiceStatus.log', filemode='a', encoding="UTF-8", level=logging.INFO,
                        format='%(asctime)s | %(process)d | %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    #log = logging.getLogger("win-services-logger")


    number_RunningServices = 0
    number_not_RunningServices = 0

    list_services_toBeMonitored = ['ClicktorunSVC', 'ClipSVC', 'AJRouter']
    number_total_MonitoredServices = len(list_services_toBeMonitored)

    for x in list_services_toBeMonitored:

        service = getService(x)
        print(service)
        logEntry = x + " | " + service["display_name"] + " | " + service["binpath"] + " | " + service["username"] + " | " + service["start_type"] +" | " + service["status"] + " | " + str(service["pid"]) + " | " + service["description"]
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


    print("Total Number of Monitored Services: " + str(number_total_MonitoredServices))
    print ("Total Number of Running Services: "+ str(number_RunningServices))
    print("Total Number of NOT Running Services: " + str(number_not_RunningServices))
    print("Percent of Running Services: " + str(round(number_RunningServices/number_total_MonitoredServices,2)*100) + " %")
