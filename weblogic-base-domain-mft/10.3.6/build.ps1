$ScriptDir      = Split-Path $MyInvocation.MyCommand.Path -Parent

Copy-Item ..\..\..\configure-jms.py -Destination $ScriptDir

docker build -t skat/weblogic-base-domain-mft-jdk7u79:10.3.6 .

Remove-Item $ScriptDir\configure-jms.py

