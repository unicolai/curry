# SKAT MFT WebLogic 11g Container
# -------------------------------
#
# Build of base WebLogic Server 11g installation.
#
# Since this build is time consuming creation of the base domain must be
# done in another image that is based on this one.
#
# Credits: A backport and improved version of Oracle's 12c version:
#
# https://github.com/oracle/docker/blob/master/OracleWebLogic
#
# REQUIRED ASSETS TO BUILD THIS IMAGE
# -----------------------------------
# (1) wls1036_generic.jar (Oracle WebLogic Server 10.3.6 Generic Installer)
#
# http://www.oracle.com/technetwork/middleware/weblogic/downloads/wls-for-dev-1703574.html
#
# As this asset requires license acceptance on Oracle.com  we have stashed it on Azure for this build.
#
# (2) jdk-7u79-linux-x64.rpm (Oracle Java SE Development Kit 7 U 79 for Linux x64 RPM)
#
# http://www.oracle.com/technetwork/java/javase/downloads/java-archive-downloads-javase7-521261.html
#
# This file is downloaded directly from oracle.com as part of the build.
#
# NOTE: All assets are checksum (MD5) verified before installation.
#
# HOW TO BUILD THIS IMAGE
# -----------------------
# Run:
#      $ docker build -t skat/weblogic-base-mft-jdk7u79:10.3.6 .
#
# PULL BASE IMAGE
# ---------------
FROM oraclelinux:7

# MAINTAINER
# ----------
MAINTAINER Christopher Derek Curry <cdcurry@krispoint.com>

# Environment variables
# ---------------------
ENV JAVA_RPM jdk-7u79-linux-x64.rpm
ENV WLS_PKG wls1036_generic.jar
ENV JDK_RPM_URL http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-linux-x64.rpm
ENV JDK_RPM_FILE jdk-7u79-linux-x64.rpm
ENV JDK_RPM_FILE_MD5 8486da4cdc4123f5c4f080d279f07712

ENV WLS_PKG_URL https://sktmftblob.blob.core.windows.net/docker-assets/wls1036_generic.jar
ENV WLS_PKG_FILE wls1036_generic.jar
ENV WLS_PKG_FILE_MD5 33d45745ff0510381de84427a7536f65
ENV JAVA_HOME /usr/java/default

# Setup required packages (unzip), filesystem, and oracle user
# ------------------------------------------------------------
RUN mkdir /u01 && \
    chmod a+xr /u01 && \
    useradd -b /u01 -m -s /bin/bash oracle 

# Copy packages
# -------------
COPY wls-silent.xml /u01/

# Install tools
# -------------
RUN yum -y install wget

# Install and configure Oracle JDK
# -------------------------------------
# Install gets the JDK from Oracle and handles the accept-before-download requirement too.
# Only change this line when required as initial download will be cached for future builds.
RUN wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" $JDK_RPM_URL && \
    echo "$JDK_RPM_FILE_MD5  $JDK_RPM_FILE" >> JDK_MD5SUM && \
    md5sum -c JDK_MD5SUM && \
    rpm -Uvh $JDK_RPM_FILE && \
    rm -f $JDK_RPM_FILE JDK_MD5SUM

# The following changes to limits.conf and .sysctl.conf are heavily inspired by Oracle's 12c Dockerfiles:
# https://github.com/oracle/docker/blob/master/OracleWebLogic/dockerfiles/12.2.1/Dockerfile.generic

# Change the open file limits in /etc/security/limits.conf
RUN sed -i '/.*EOF/d' /etc/security/limits.conf && \
    echo "* soft nofile 16384" >> /etc/security/limits.conf && \
    echo "* hard nofile 16384" >> /etc/security/limits.conf && \
    echo "# EOF"  >> /etc/security/limits.conf

# Change the kernel parameters that need changing.
RUN echo "net.core.rmem_max=4192608" > /u01/oracle/.sysctl.conf && \
    echo "net.core.wmem_max=4192608" >> /u01/oracle/.sysctl.conf && \
    sysctl -e -p /u01/oracle/.sysctl.conf

# Adjust file permissions, go to /u01 as user 'oracle' to proceed with WLS installation
RUN chown oracle:oracle -R /u01
WORKDIR /u01
USER oracle

# Install and configure WebLogic Server 11g
# -----------------------------------------
# Only change this line when required as initial download will be cached for future builds.
RUN wget --no-check-certificate --no-cookies $WLS_PKG_URL && \
    echo "MD5 ($WLS_PKG_FILE) = $WLS_PKG_FILE_MD5" > WLS_MD5SUM && \
    cat WLS_MD5SUM && \
    md5sum -c < WLS_MD5SUM && \
    rm -f WLS_MD5SUM

RUN java -jar $WLS_PKG_FILE -mode=silent -silent_xml=/u01/wls-silent.xml && \
    rm -f $WLS_PKG_FILE WLS_MD5SUM

WORKDIR /u01/oracle/

ENV PATH $PATH:/u01/oracle/weblogic/oracle_common/common/bin

# Define default command to start bash.
CMD ["bash"]
