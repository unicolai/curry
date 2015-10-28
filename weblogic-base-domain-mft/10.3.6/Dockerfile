# HOW TO BUILD THIS IMAGE
# -----------------------------------------
#
# Run:
#      $ ./build.sh
#
# AUTHOR
# -----------------------------------------
# Christopher Derek Curry <cdcurry@krispoint.com>
#
# Pull base image
# ---------------
#FROM skat/weblogic-base-mft-jdk7u79:10.3.6
FROM wls11g_domain7

# MAINTAINER
# ----------
MAINTAINER Christopher Derek Curry <cdcurry@krispoint.com>

# WLS Configuration
# -------------------------------
ENV ADMIN_USER weblogic
ENV ADMIN_PASSWORD welcome01
ENV ADMIN_PORT 7001
ENV SSL_PORT 7002
ENV NM_PORT 5556
ENV USER_MEM_ARGS -Xms256m -Xmx512m -XX:MaxPermSize=1024m
ENV EXTRA_JAVA_PROPERTIES $EXTRA_JAVA_PROPERTIES -Djava.security.egd=file:///dev/urandom

ENV WLS_START_DOMAIN true
ENV WLS_ADMIN_SERVER_NAME AdminServer
ENV WLS_ADMIN_SERVER_ADDRESS 127.0.0.1
ENV WLS_ADMIN_SERVER_PORT 7001
ENV WLS_ADMIN_USER weblogic
ENV WLS_ADMIN_PASSWORD welcome01
ENV WLS_TARGET AdminServer
ENV WLS_SERVERS AdminServer
ENV MODULE_NAME MFTTransformationModule
ENV MODULE_QCF MFTTransformationQCF
ENV QUEUE_TYPE Queue
ENV SUB_DEPLOYMENT MFTTestSubDeployment
ENV FS_PREFIX MFTTransformationFS
ENV JMS_SERVER_PREFIX MFTTransformationJMSServer
ENV WLS_TARGET_TYPE Server

# Add files required to build this image
COPY create-wls-domain.py /u01/oracle/

# Root commands
USER root
COPY wlst.sh /u01/oracle/weblogic/wlserver_10.3/common/bin/wlst.sh
RUN chmod a+xr /u01/oracle/weblogic/wlserver_10.3/common/bin/wlst.sh
RUN echo ". /u01/oracle/weblogic/user_projects/domains/base_domain/bin/setDomainEnv.sh" >> /root/.bashrc && \
    echo "export PATH=$PATH:/u01/oracle/weblogic/wlserver_10.3/common/bin:/u01/oracle/weblogic/user_projects/domains/base_domain/bin" >> /root/.bashrc

# Configuration of WLS Domain
USER oracle

WORKDIR /u01/oracle/weblogic
RUN /u01/oracle/weblogic/wlserver_10.3/common/bin/wlst.sh -skipWLSModuleScanning /u01/oracle/create-wls-domain.py && \
    mkdir -p /u01/oracle/weblogic/user_projects/domains/base_domain/servers/AdminServer/security && \
    echo "username=weblogic" > /u01/oracle/weblogic/user_projects/domains/base_domain/servers/AdminServer/security/boot.properties && \ 
    echo "password=$ADMIN_PASSWORD" >> /u01/oracle/weblogic/user_projects/domains/base_domain/servers/AdminServer/security/boot.properties && \
    echo ". /u01/oracle/weblogic/user_projects/domains/base_domain/bin/setDomainEnv.sh" >> /u01/oracle/.bashrc && \ 
    echo "export PATH=$PATH:/u01/oracle/weblogic/wlserver_10.3/common/bin:/u01/oracle/weblogic/user_projects/domains/base_domain/bin" >> /u01/oracle/.bashrc 


COPY configure-jms.py /u01/oracle/weblogic/user_projects/domains/base_domain/
WORKDIR /u01/oracle/weblogic/user_projects/domains/base_domain
RUN /u01/oracle/weblogic/wlserver_10.3/common/bin/wlst.sh -skipWLSModuleScanning configure-jms.py

# Expose Node Manager default port, and also default http/https ports for admin console
EXPOSE $NM_PORT $ADMIN_PORT $SSL_PORT

WORKDIR /u01/oracle/weblogic

# Final setup
WORKDIR /u01/oracle

ENV PATH $PATH:/u01/oracle/weblogic/wlserver_10.3/common/bin:/u01/oracle/weblogic/user_projects/domains/base_domain/bin:/u01/oracle

# Define default command to start bash. 
CMD ["startWebLogic.sh"]
