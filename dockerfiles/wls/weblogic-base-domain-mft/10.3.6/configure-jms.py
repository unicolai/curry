#!/usr/bin/python
import os, sys
import socket
import errno

__author__ = "Christopher Derek Curry"
__copyright__ = "Copyright 2015, SKAT"
__credits__ = ["Christopher Derek Curry"]
__license__ = "SKAT"
__version__ = "1.0"
__maintainer__ = "Christopher Derek Curry"
__email__ = "cdcurry@krispoint.com"
__status__ = "Production"

# Simple interactive prompt with built-in default value handling.
#
# Priority 1: Default value if user press enter
# Priority 2: User entered value
def prompt(prompt, defaultValue):
    userInput = raw_input(prompt + " ["+ defaultValue +"]: ")
    if len(userInput) == 0:
        userInput = defaultValue
    return userInput

# Interactive prompt with built-in default value handling.
#
# Priority 1: Check ENVIRONMENT variable named as osEnv is set.
# Priority 2: Default value if user press enter
# Priority 3: User entered value
def promptIfNoOSEnvVar(prompt, defaultValue, osEnv):
    osEnvVar = os.environ.get(osEnv)
    if osEnvVar != None:
        return osEnvVar
    userInput = raw_input("Enter " + prompt + " ["+ defaultValue +"]: ")
    if len(userInput) == 0:
        userInput = defaultValue
    return userInput

def createFileStore(fileStoreName, managedServer):
    print 'Creating JMS File Store for ' + managedServer
    cd('/')
    cmo.createFileStore(fileStoreName)
    cd('/FileStores/' + fileStoreName)
    set('Targets',jarray.array([ObjectName('com.bea:Name=' + managedServer + ',Type=Server')], ObjectName))
    print "Created File Store: " + fileStoreName

def createJMSServer(jmsServerName, fileStoreName, managedServer):
    print 'Creating JMS Server for ' + managedServer
    cd('/')
    cmo.createJMSServer(jmsServerName)
    cd('/Deployments/' + jmsServerName)
    cmo.setPersistentStore(getMBean('/FileStores/' + fileStoreName))
    set('Targets',jarray.array([ObjectName('com.bea:Name=' + managedServer + ',Type=Server')], ObjectName))
    print "Created JMS Server: " + jmsServerName

def createJMSModule(moduleName, target, targetType):
    cd('/')
    cmo.createJMSSystemResource(moduleName, moduleName + '-jms.xml')
    cd('/SystemResources/' + moduleName)
    set('Targets',jarray.array([ObjectName('com.bea:Name=' + target + ',Type=' + targetType)], ObjectName))
    print "Created JMS Module: " + moduleName


def createConnectionFactory(moduleName, cfName, cfJNDIName, subDeployment):
    cd('/')
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName)
    cmo.createConnectionFactory(cfName)
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/ConnectionFactories/' + cfName)
    cmo.setJNDIName(cfJNDIName)
    cmo.setSubDeploymentName(subDeployment)
    cmo.setDefaultTargetingEnabled(false)
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/ConnectionFactories/' + cfName + '/SecurityParams/' + cfName)
    cmo.setAttachJMSXUserId(false)
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/ConnectionFactories/' + cfName + '/ClientParams/' + cfName)
    cmo.setClientIdPolicy('Restricted')
    cmo.setSubscriptionSharingPolicy('Exclusive')
    cmo.setMessagesMaximum(512)
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/ConnectionFactories/' + cfName + '/TransactionParams/' + cfName)
    cmo.setXAConnectionFactoryEnabled(true)
    print "Created Connection Factory: " + cfName

def createDistributedQueue(moduleName, queueName, queueJNDIName, subDeployment, redeliveryLimit, redeliveryDelay):
    newQueueName = queueName + 'Queue'
    cd('/')
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName)
    cmo.createUniformDistributedQueue(newQueueName)
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/UniformDistributedQueues/' + newQueueName)
    cmo.setJNDIName(queueJNDIName + 'Queue')
    cmo.setDefaultTargetingEnabled(false)
    cmo.setSubDeploymentName(subDeployment)
    print "Created Distributed Queue: " + newQueueName
    # Create error queue
    # ------------------
    errorDestQueue = queueName + 'ErrorQueue'
    cd('/')
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName)
    cmo.createUniformDistributedQueue(errorDestQueue)
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/UniformDistributedQueues/' + errorDestQueue)
    cmo.setJNDIName(errorDestQueue)
    cmo.setDefaultTargetingEnabled(false)
    cmo.setSubDeploymentName(subDeployment)
    print "Created Distributed Queue - Error Destination: " + errorDestQueue
    cd('/')
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/UniformDistributedQueues/' + newQueueName + '/DeliveryFailureParams/' + newQueueName)
    cmo.setRedeliveryLimit(redeliveryLimit)
    cmo.setErrorDestination(getMBean('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/UniformDistributedQueues/' + errorDestQueue))
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/UniformDistributedQueues/' + newQueueName + '/DeliveryParamsOverrides/' + newQueueName)
    cmo.setRedeliveryDelay(redeliveryDelay)

def createQueue(moduleName, queueName, queueJNDIName, subDeployment, redeliveryLimit, redeliveryDelay, jmsServer):
    newQueueName = queueName + 'Queue'
    cd('/')
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName)
    cmo.createQueue(newQueueName)
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/Queues/' + newQueueName)
    cmo.setJNDIName(queueJNDIName + 'Queue')
    # cmo.setDefaultTargetingEnabled(false)
    cmo.setSubDeploymentName(subDeployment)
    cd('/SystemResources/' + moduleName + '/SubDeployments/' + subDeployment)
    set('Targets',jarray.array([ObjectName('com.bea:Name=' + jmsServer + ',Type=JMSServer')], ObjectName))
    print "Created Queue: " + newQueueName
    # Create error queue
    # ------------------
    errorDestQueue = queueName + 'ErrorQueue'
    cd('/')
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName)
    cmo.createQueue(errorDestQueue)
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/Queues/' + errorDestQueue)
    cmo.setJNDIName(errorDestQueue)
    # cmo.setDefaultTargetingEnabled(false)
    cmo.setSubDeploymentName(subDeployment)
    cd('/SystemResources/' + moduleName + '/SubDeployments/' + subDeployment)
    set('Targets',jarray.array([ObjectName('com.bea:Name=' + jmsServer + ',Type=JMSServer')], ObjectName))
    print "Created Queue - Error Destination: " + errorDestQueue
    cd('/')
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/Queues/' + newQueueName + '/DeliveryFailureParams/' + newQueueName)
    cmo.setRedeliveryLimit(redeliveryLimit)
    cmo.setErrorDestination(getMBean('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/Queues/' + errorDestQueue))
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/Queues/' + newQueueName + '/DeliveryParamsOverrides/' + newQueueName)
    cmo.setRedeliveryDelay(redeliveryDelay)

def destroyDistributedQueue(moduleName, queueName):
    cd('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName)
    cmo.destroyUniformDistributedQueue(getMBean('/JMSSystemResources/' + moduleName + '/JMSResource/' + moduleName + '/UniformDistributedQueues/' + queueName))

def createSubDeployment(moduleName, subDeployment, target, targetType):
    cd('/SystemResources/' + moduleName)
    cmo.createSubDeployment(subDeployment)
    cd('/SystemResources/' + moduleName + '/SubDeployments/' + subDeployment)
    set('Targets',jarray.array([ObjectName('com.bea:Name=' + target + ',Type=' + targetType)], ObjectName))
    print "Created Sub Deployment: " + subDeployment

def make_sure_path_exists(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        print "Created directory " + path
    except Exception, e:
        print "Caught exception"

try:
    WLS_ADMIN_SERVER = promptIfNoOSEnvVar('Admin Server Name', 'sktddev03_adminserver', 'WLS_ADMIN_SERVER_NAME')
    WLS_ADMIN_SERVER_ADDRESS = promptIfNoOSEnvVar('Admin Server Listen Address', socket.gethostname(), 'WLS_ADMIN_SERVER_ADDRESS')
    WLS_ADMIN_SERVER_PORT = promptIfNoOSEnvVar('Admin Server Listen Port', '7001', 'WLS_ADMIN_SERVER_PORT')
    WLS_ADMIN_USER = promptIfNoOSEnvVar('Admin User', 'weblogic', 'WLS_ADMIN_USER')
    WLS_ADMIN_PASSWORD = promptIfNoOSEnvVar('Admin User Password', 'Rbg11#MM', 'WLS_ADMIN_PASSWORD')

    WLS_START_DOMAIN = promptIfNoOSEnvVar('Jumpstart Domain', 'false', 'WLS_START_DOMAIN')

    WLS_TARGET = promptIfNoOSEnvVar('Target Name', 'sktdev03_cluster', 'WLS_TARGET')
    WLS_SERVERS = promptIfNoOSEnvVar('Server Name(s)', 'sktdev03_server_1', 'WLS_SERVERS')
    WLS_SERVERS_ARRAY = WLS_SERVERS.split(',')
    for WLS_SERVER_ID in WLS_SERVERS_ARRAY:
        print 'Doing configuration for %s' % WLS_SERVER_ID

    url =  't3://' + WLS_ADMIN_SERVER_ADDRESS + ':' + WLS_ADMIN_SERVER_PORT

    # This is for running in docker container as this incl. fixed values.
    if WLS_START_DOMAIN == "true":
        _startServerJvmArgs = " -XX:MaxPermSize=128m"
        domainDir = "/u01/oracle/weblogic/user_projects/domains/base_domain"
        _timeOut=30000
        startServer(WLS_ADMIN_SERVER, 'base_domain', url, WLS_ADMIN_USER, WLS_ADMIN_PASSWORD, domainDir, timeout=_timeOut, block='true', jvmArgs=_startServerJvmArgs)

    connect(WLS_ADMIN_USER, WLS_ADMIN_PASSWORD, url)

    edit()
    startEdit()

    MODULE_NAME = promptIfNoOSEnvVar('JMS Module Name', 'MFTTransformationModule', 'MODULE_NAME')
    MODULE_QCF = promptIfNoOSEnvVar('JMS Connection Factory', 'MFTTransformationQCF', 'MODULE_QCF')
    QUEUE_TYPE = promptIfNoOSEnvVar('JMS Queue Type [UniformDistributedQueue|Queue]', 'UniformDistributedQueue', 'QUEUE_TYPE')
    SUB_DEPLOYMENT = promptIfNoOSEnvVar('JMS Sub Deployment', 'MFTTestSubDeployment', 'SUB_DEPLOYMENT')
    FS_PREFIX = promptIfNoOSEnvVar('File Store Prefix', 'MFTTransformationFS', 'FS_PREFIX')
    JMS_SERVER_PREFIX = promptIfNoOSEnvVar('JMS Server Prefix', 'MFTTransformationJMSServer', 'JMS_SERVER_PREFIX')
    WLS_TARGET_TYPE = promptIfNoOSEnvVar('WLS_TARGET_TYPE (Server|Cluster)', 'Cluster', 'WLS_TARGET_TYPE')

    # Clean
    try:
        cd('/')
        #cmo.destroyJMSSystemResource(getMBean('/SystemResources/' + MODULE_NAME))
        #cmo.destroyJMSServer(getMBean('/Deployments/MFTTestBackendJMSS_1'))
        #cmo.destroyJMSServer(getMBean('/Deployments/MFTTestBackendJMSS_2'))
        #cmo.destroyFileStore(getMBean('/FileStores/MFTTestBackendFS_1'))
        #cmo.destroyFileStore(getMBean('/FileStores/MFTTestBackendFS_2'))
    except Exception, e:
        print "Continue script"

    # Install
    i = 1
    for WLS_SERVER in WLS_SERVERS_ARRAY:
        print 'Doing Data Store for %s' % WLS_SERVER
        make_sure_path_exists('servers/' + WLS_SERVER + '/data/store/' + FS_PREFIX + '_' + str(i))
        createFileStore(FS_PREFIX + '_' + str(i), WLS_SERVER)
        createJMSServer(JMS_SERVER_PREFIX + '_' + str(i), FS_PREFIX + '_' + str(i), WLS_SERVER)
        i = i + 1

    createJMSModule(MODULE_NAME, WLS_TARGET, WLS_TARGET_TYPE)
    createSubDeployment(MODULE_NAME, SUB_DEPLOYMENT, WLS_TARGET, WLS_TARGET_TYPE)
    createConnectionFactory(MODULE_NAME, MODULE_QCF, MODULE_QCF, SUB_DEPLOYMENT)

    if QUEUE_TYPE == "UniformDistributedQueue":

        # MFTDistributionInput
        createDistributedQueue(MODULE_NAME, 'MFTDistribution', 'MFTDistribution', SUB_DEPLOYMENT, 3, -1)

        # TSISOF
        createDistributedQueue(MODULE_NAME, 'TSISOFInput', 'TSISOFInput', SUB_DEPLOYMENT, 3, -1)
        createDistributedQueue(MODULE_NAME, 'TSISOFOutput', 'TSISOFOutput', SUB_DEPLOYMENT, 3, -1)

        # TSISOE
        createDistributedQueue(MODULE_NAME, 'TSISOEInput', 'TSISOEInput', SUB_DEPLOYMENT, 3, -1)
        createDistributedQueue(MODULE_NAME, 'TSISOEOutput', 'TSISOEOutput', SUB_DEPLOYMENT, 3, -1)

        # TSISIF
        createDistributedQueue(MODULE_NAME, 'TSISIFInput', 'TSISIFInput', SUB_DEPLOYMENT, 3, -1)
        createDistributedQueue(MODULE_NAME, 'TSISIFOutput', 'TSISIFOutput', SUB_DEPLOYMENT, 3, -1)

        # TSISIE
        createDistributedQueue(MODULE_NAME, 'TSISIEInput', 'TSISIEInput', SUB_DEPLOYMENT, 3, -1)
        createDistributedQueue(MODULE_NAME, 'TSISIEOutput', 'TSISIEOutput', SUB_DEPLOYMENT, 3, -1)

        # TSESOX
        createDistributedQueue(MODULE_NAME, 'TSESOXInput', 'TSESOXInput', SUB_DEPLOYMENT, 3, -1)
        createDistributedQueue(MODULE_NAME, 'TSESOXOutput', 'TSESOXOutput', SUB_DEPLOYMENT, 3, -1)

        # TSESOE
        createDistributedQueue(MODULE_NAME, 'TSESOEInput', 'TSESOEInput', SUB_DEPLOYMENT, 3, -1)
        createDistributedQueue(MODULE_NAME, 'TSESOEOutput', 'TSESOEOutput', SUB_DEPLOYMENT, 3, -1)

        # TSESOC
        createDistributedQueue(MODULE_NAME, 'TSESOCInput', 'TSESOCInput', SUB_DEPLOYMENT, 3, -1)
        createDistributedQueue(MODULE_NAME, 'TSESOCOutput', 'TSESOCOutput', SUB_DEPLOYMENT, 3, -1)

        # TSESIX
        createDistributedQueue(MODULE_NAME, 'TSESIXInput', 'TSESIXInput', SUB_DEPLOYMENT, 3, -1)
        createDistributedQueue(MODULE_NAME, 'TSESIXOutput', 'TSESIXOutput', SUB_DEPLOYMENT, 3, -1)

        # TSESIE
        createDistributedQueue(MODULE_NAME, 'TSESIEInput', 'TSESIEInput', SUB_DEPLOYMENT, 3, -1)
        createDistributedQueue(MODULE_NAME, 'TSESIEOutput', 'TSESIEOutput', SUB_DEPLOYMENT, 3, -1)

    if QUEUE_TYPE == "Queue":
        jmsServer = JMS_SERVER_PREFIX + '_1'

        # MFTDistributionInput
        createQueue(MODULE_NAME, 'MFTDistribution', 'MFTDistribution', SUB_DEPLOYMENT, 3, -1, jmsServer)

        # TSISOF
        createQueue(MODULE_NAME, 'TSISOFInput', 'TSISOFInput', SUB_DEPLOYMENT, 3, -1, jmsServer)
        createQueue(MODULE_NAME, 'TSISOFOutput', 'TSISOFOutput', SUB_DEPLOYMENT, 3, -1, jmsServer)

        # TSISOE
        createQueue(MODULE_NAME, 'TSISOEInput', 'TSISOEInput', SUB_DEPLOYMENT, 3, -1, jmsServer)
        createQueue(MODULE_NAME, 'TSISOEOutput', 'TSISOEOutput', SUB_DEPLOYMENT, 3, -1, jmsServer)

        # TSISIF
        createQueue(MODULE_NAME, 'TSISIFInput', 'TSISIFInput', SUB_DEPLOYMENT, 3, -1, jmsServer)
        createQueue(MODULE_NAME, 'TSISIFOutput', 'TSISIFOutput', SUB_DEPLOYMENT, 3, -1, jmsServer)

        # TSISIE
        createQueue(MODULE_NAME, 'TSISIEInput', 'TSISIEInput', SUB_DEPLOYMENT, 3, -1, jmsServer)
        createQueue(MODULE_NAME, 'TSISIEOutput', 'TSISIEOutput', SUB_DEPLOYMENT, 3, -1, jmsServer)

        # TSESOX
        createQueue(MODULE_NAME, 'TSESOXInput', 'TSESOXInput', SUB_DEPLOYMENT, 3, -1, jmsServer)
        createQueue(MODULE_NAME, 'TSESOXOutput', 'TSESOXOutput', SUB_DEPLOYMENT, 3, -1, jmsServer)

        # TSESOE
        createQueue(MODULE_NAME, 'TSESOEInput', 'TSESOEInput', SUB_DEPLOYMENT, 3, -1, jmsServer)
        createQueue(MODULE_NAME, 'TSESOEOutput', 'TSESOEOutput', SUB_DEPLOYMENT, 3, -1, jmsServer)

        # TSESOC
        createQueue(MODULE_NAME, 'TSESOCInput', 'TSESOCInput', SUB_DEPLOYMENT, 3, -1, jmsServer)
        createQueue(MODULE_NAME, 'TSESOCOutput', 'TSESOCOutput', SUB_DEPLOYMENT, 3, -1, jmsServer)

        # TSESIX
        createQueue(MODULE_NAME, 'TSESIXInput', 'TSESIXInput', SUB_DEPLOYMENT, 3, -1, jmsServer)
        createQueue(MODULE_NAME, 'TSESIXOutput', 'TSESIXOutput', SUB_DEPLOYMENT, 3, -1, jmsServer)

        # TSESIE
        createQueue(MODULE_NAME, 'TSESIEInput', 'TSESIEInput', SUB_DEPLOYMENT, 3, -1, jmsServer)
        createQueue(MODULE_NAME, 'TSESIEOutput', 'TSESIEOutput', SUB_DEPLOYMENT, 3, -1, jmsServer)

    save()
    activate()
    exit()
except Exception, e:
    dumpStack()
    print "==>Error Occured"
    print e


