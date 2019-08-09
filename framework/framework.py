#!/usr/bin/env python
import logging
import threading

from pymesos import MesosSchedulerDriver
from mesos.interface import mesos_pb2
from mesos.interface import Scheduler as BaseScheduler

logging.basicConfig(
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    level=logging.DEBUG
)

def threadit(target, *args, **kw):
    t = threading.Thread(target=target,
                         name=target.__name__,
                         args=args, kwargs=kw)
    t.daemon = True
    t.start()
    return t


class Scheduler(BaseScheduler):
    def __init__(self):
        self.number = 0
    def registered(self, driver, frameworkId, masterInfo):
        logging.error("Registered with framework ID %s", frameworkId.value)
    def reregistered(self, driver, masterInfo):
        logging.error("Framework is reregistered.")
    def _is_registered(self):
        return True
    def statusUpdate(self, driver, update):
        logging.debug('Status update TID %s %s',
                      update.task_id.value,
                      update.state)
    def resourceOffers(self, driver, offers):
        logging.debug("resourceOffers (%s, %s)", driver, offers)
        for offer in offers:
            logging.info("Received offer: %s", offer)
            task = mesos_pb2.TaskInfo()
            task.task_id.value = "job-{}".format(self.number)
            task.slave_id.value = offer.slave_id.value
            task.name = "Job {}".format(self.number)
            task.command.shell = False
            task.command.value = "36000"
            task.container.type = mesos_pb2.ContainerInfo.DOCKER
            task.container.docker.image = "python:2.7-alpine"
            task.container.docker.network = task.container.docker.BRIDGE
            task.container.docker.force_pull_image = False
            task.container.hostname = task.task_id.value
            entrypoint = task.container.docker.parameters.add()
            entrypoint.key = "entrypoint"
            entrypoint.value = "/bin/sleep"
            rmparam = task.container.docker.parameters.add()
            rmparam.key = "rm"
            rmparam.value = "true"
            cpus = task.resources.add()
            cpus.name = "cpus"
            cpus.type = mesos_pb2.Value.SCALAR
            cpus.scalar.value = 2
            cpus.role = "*"
            mem = task.resources.add()
            mem.name = "mem"
            mem.type = mesos_pb2.Value.SCALAR
            mem.scalar.value = 2927
            mem.role = "*"
            logging.info("Created a Mesos task for %s", self.number)
            self.number += 1
            driver.launchTasks(offer.id, [task], filters=mesos_pb2.Filters())

framework = mesos_pb2.FrameworkInfo()

framework.id.value = "mesostest-master"
framework.user = "root"
framework.name = "mesostest-master"
framework.role = "*"
framework.checkpoint = True

scheduler = Scheduler()

driver = MesosSchedulerDriver(scheduler, framework, "zk://zk:2181/mesostest")
driver.framework.failover_timeout = 604800

driver.run()

