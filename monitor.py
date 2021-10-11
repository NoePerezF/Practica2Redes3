from pysnmp.hlapi import *
import rrdtool
import time
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
rrdpath = 'RRD/'
imgpath = 'IMG/'
fname = 'trend.rrd'
mailsender = "testredes3@gmail.com"
mailreceip = "tanibet.escom@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = 'prueba123'
cpu_u_1 = 30
cpu_u_2 = 50
cpu_u_3 = 70
ram_u_1 = 30
ram_u_2 = 50
ram_u_3 = 60
disk_u_1 = 60
disk_u_2 = 80
disk_u_3 = 98
flags = [False,False,False,False,False,False,False,False,False]
def consultaSNMP(comunidad,host,oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad),
               UdpTransportTarget((host, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            varB=(' = '.join([x.prettyPrint() for x in varBind]))
            resultado= varB.split()[2]
            if((len(varB.split("Software")) > 1) | (resultado == 'Linux')):
                resultado = varB.split("=")[1]
    return resultado
def createRRD():
    ret = rrdtool.create(rrdpath+"trend.rrd",
                         "--start",'N',
                         "--step",'60',
                         "DS:CPUload:GAUGE:600:U:U",
                         "DS:RAMload:GAUGE:600:U:U",
                         "DS:DISKload:GAUGE:600:U:U",
                         "RRA:AVERAGE:0.5:1:24",
                         "RRA:AVERAGE:0.5:1:24",
                         "RRA:AVERAGE:0.5:1:24")
    if ret:
        print (rrdtool.error())
def graph(op,tiempo_inicial,tiempo_final):
    if(op == 1):
        ret = rrdtool.graphv( imgpath+"cpu.png",
                     "--start",str(tiempo_inicial),
                     "--end",str(tiempo_final),
                     "--vertical-label=Cpu load",
                    '--lower-limit', '0',
                    '--upper-limit', '100',
                    "--title=Uso del CPU del agente Usando SNMP y RRDtools \n Detección de umbrales",

                    "DEF:cargaCPU="+rrdpath+"trend.rrd:CPUload:AVERAGE",

                     "VDEF:cargaMAX=cargaCPU,MAXIMUM",
                     "VDEF:cargaMIN=cargaCPU,MINIMUM",
                     "VDEF:cargaSTDEV=cargaCPU,STDEV",
                     "VDEF:cargaLAST=cargaCPU,LAST",

                     "CDEF:umbral70=cargaCPU,70,LT,0,cargaCPU,IF",
                     "AREA:cargaCPU#00FF00:Carga del CPU",
                     "AREA:umbral70#FF9F00:Carga CPU mayor que 70",
                     "HRULE:70#FF0000:Umbral 50 - 70%",

                     
                     "HRULE:50#FFFF00:Umbral 30 - 50%",
                     "HRULE:30#008F39:Umbral 1 - 30%",

                     "PRINT:cargaLAST:%6.2lf",
                     "GPRINT:cargaMIN:%6.2lf %SMIN",
                     "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                     "GPRINT:cargaLAST:%6.2lf %SLAST" )
    elif(op == 2):
        ret = rrdtool.graphv( imgpath+"ram.png",
                     "--start",str(tiempo_inicial),
                     "--end",str(tiempo_final),
                     "--vertical-label=RAM load",
                    '--lower-limit', '0',
                    '--upper-limit', '100',
                    "--title=Uso de RAM del agente Usando SNMP y RRDtools \n Detección de umbrales",

                    "DEF:cargaRAM="+rrdpath+"trend.rrd:RAMload:AVERAGE",

                     "VDEF:cargaMAX=cargaRAM,MAXIMUM",
                     "VDEF:cargaMIN=cargaRAM,MINIMUM",
                     "VDEF:cargaSTDEV=cargaRAM,STDEV",
                     "VDEF:cargaLAST=cargaRAM,LAST",

                     "CDEF:umbral60=cargaRAM,60,LT,0,cargaRAM,IF",
                     "AREA:cargaRAM#00FF00:Carga de RAM",
                     "AREA:umbral60#FF9F00:Carga RAM mayor que 60",
                     "HRULE:60#FF0000:Umbral 50 - 60%",

                     
                     "HRULE:50#FFFF00:Umbral 30 - 50%",
                     "HRULE:30#008F39:Umbral 1 - 30%",

                     "PRINT:cargaLAST:%6.2lf",
                     "GPRINT:cargaMIN:%6.2lf %SMIN",
                     "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                     "GPRINT:cargaLAST:%6.2lf %SLAST" )
    elif(op == 3):
        ret = rrdtool.graphv( imgpath+"disk.png",
                     "--start",str(tiempo_inicial),
                     "--end",str(tiempo_final),
                     "--vertical-label=DISK load",
                    '--lower-limit', '0',
                    '--upper-limit', '100',
                    "--title=Uso deL Disco del agente Usando SNMP y RRDtools \n Detección de umbrales",

                    "DEF:cargaDISK="+rrdpath+"trend.rrd:DISKload:AVERAGE",

                     "VDEF:cargaMAX=cargaDISK,MAXIMUM",
                     "VDEF:cargaMIN=cargaDISK,MINIMUM",
                     "VDEF:cargaSTDEV=cargaDISK,STDEV",
                     "VDEF:cargaLAST=cargaDISK,LAST",

                     "CDEF:umbral98=cargaDISK,98,LT,0,cargaDISK,IF",
                     "AREA:cargaDISK#00FF00:Carga del Disco",
                     "AREA:umbral98#FF9F00:Carga del disco mayor que 98",
                     "HRULE:98#FF0000:Umbral 80 - 98%",

                     "HRULE:80#FFFF00:Umbral 60 - 80%",
                     "HRULE:60#008F39:Umbral 1 - 60%",

                     "PRINT:cargaLAST:%6.2lf",
                     "GPRINT:cargaMIN:%6.2lf %SMIN",
                     "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                     "GPRINT:cargaLAST:%6.2lf %SLAST" )
def notify(file,subject):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = mailsender
    msg['To'] = mailreceip
    fp = open(imgpath+file, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)
    s = smtplib.SMTP(mailserver)

    s.starttls()
    # Login Credentials for sending the mail
    s.login(mailsender, password)

    s.sendmail(mailsender, mailreceip, msg.as_string())
    s.sendmail(mailsender, 'noepfab@gmail.com', msg.as_string())
    s.quit()
def generarReporte(name):
    res = consultaSNMP('home','192.168.3.26',"1.3.6.1.2.1.1.1.0")
    if(len(res.split("Software")) > 1):
        sistema = res.split("Software")[1].split(" ")[1]
        version = res.split("Software")[1].split(" ")[3]
    else:
        sistema = res.split(" ")[1]
        version = res.split(" ")[3]
    ubicacion = consultaSNMP('home','192.168.3.26',"1.3.6.1.2.1.1.6.0")
    tiempo = consultaSNMP('home','192.168.3.26',"1.3.6.1.2.1.1.3.0")
    tiempo ="{0:.2f}".format(((int(tiempo)*0.01)/60)/60)
    ip = '192.168.3.26'
    c = canvas.Canvas("reportes/"+name+".pdf",pagesize=A4)
    w, h = A4
    if(sistema == "Linux"):
        c.drawImage("IMG/linux.jpg",10,h-60,width=50,height=50)
    else:
        c.drawImage("IMG/windows.jpeg",10,h-60,width=50,height=50)
    c.setFont("Helvetica", 10)
    c.drawString(65, h-25, "SO: "+sistema+"  Version: "+version+"  Ubicacion: "+ubicacion)
    c.drawString(65, h-50, "Tiempo de actividad antes del ultimo reinicio: "+tiempo+"hrs  Comunidad: "+'home'+' IP: '+ip)
    c.line(0,h-65,w,h-65)
    c.drawImage("IMG/cpu.png",10,h-185,width=w-20,height=110)
    c.drawImage("IMG/disk.png",10,h-305,width=w-20,height=110)
    c.drawImage("IMG/ram.png",10,h-425,width=w-20,height=110)
    c.save()
def capturar():
    carga_CPU = int(consultaSNMP('home','192.168.3.26','1.3.6.1.2.1.25.3.3.1.2.196608'))
    
    ram_total = int(consultaSNMP('home','192.168.3.26','1.3.6.1.4.1.2021.4.5.0'))
    ram_used = int(consultaSNMP('home','192.168.3.26','1.3.6.1.4.1.2021.4.11.0'))
    ram_p = 100-(ram_used*100)/ram_total
    
    disk_total = int(consultaSNMP('home','192.168.3.26','1.3.6.1.2.1.25.2.3.1.5.3'))
    disk_used = int(consultaSNMP('home','192.168.3.26','1.3.6.1.2.1.25.2.3.1.6.3'))
    disk_p = (disk_used*100)/disk_total
    
    #print("RAM TOTAL: "+str(ram_total)+"/nRAM USED: "+str(ram_used))
    valor = "N:"+str(carga_CPU)+":"+str(ram_p)+":"+str(disk_p)
    rrdtool.update(rrdpath+'trend.rrd', valor)
    rrdtool.dump(rrdpath+'trend.rrd','trend.xml')
    print (valor)
    if(carga_CPU >= cpu_u_1):
        if(not flags[0]):
            graph(1,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(2,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(3,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            notify('cpu.png',"Primer umbral de uso de CPU superado")
            generarReporte('cpu')
            flags[0] = True
            print('Primer umbral de uso de CPU superado')
    if(carga_CPU >= cpu_u_2):
        if(not flags[1]):
            graph(1,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(2,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(3,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            notify('cpu.png',"Segundo umbral de uso de CPU superado")
            generarReporte('cpu')
            flags[1] = True
            print('Segundo umbral de uso de CPU superado')
    if(carga_CPU >= cpu_u_3):
        if(not flags[2]):
            graph(1,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(2,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(3,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            notify('cpu.png',"Terccer umbral de uso de CPU superado")
            generarReporte('cpu')
            flags[2] = True
            print('Tercer umbral de uso de CPU superado')
    if(ram_p >= ram_u_1):
        if(not flags[3]):
            graph(1,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(2,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(3,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            notify('ram.png',"Primer umbral de uso de RAM superado")
            generarReporte('ram')
            flags[3] = True
            print('Primer umbral de uso de RAM superado')
    if(ram_p >= ram_u_2):
        if(not flags[4]):
            graph(1,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(2,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(3,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            notify('ram.png',"Segundo umbral de uso de RAM superado")
            generarReporte('ram')
            flags[4] = True
            print('Segundo umbral de uso de RAM superado')
    if(ram_p >= ram_u_3):
        if(not flags[5]):
            graph(1,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(2,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(3,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            notify('ram.png',"Tercer umbral de uso de RAM superado")
            generarReporte('ram')
            flags[5] = True
            print('Tercer umbral de uso de RAM superado')
    if(disk_p >= disk_u_1):
        if(not flags[6]):
            graph(1,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(2,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(3,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            notify('disk.png',"Primer umbral de uso de Disco superado")
            generarReporte('disk')
            flags[6] = True
            print('Primer umbral de uso de Disco superado')
    if(disk_p >= disk_u_2):
        if(not flags[7]):
            graph(1,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(2,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(3,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            notify('disk.png',"Segundo umbral de uso de Disco superado")
            generarReporte('disk')
            flags[7] = True
            print('Segundo umbral de uso de Disco superado')
    if(not disk_p >= disk_u_3):
        if(flags[8]):
            graph(1,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(2,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            graph(3,int(rrdtool.last(rrdpath+"trend.rrd"))-500,int(rrdtool.last(rrdpath+"trend.rrd")))
            notify('disk.png',"Tercer umbral de uso de Disco superado")
            generarReporte('disk')
            flags[8] = True
            print('Tercer umbral de uso de Disco superado')
    time.sleep(1)
def checkdb(name):
    try:
        with open(name, 'r') as f:
            return True
    except FileNotFoundError as e:
        return False
    except IOError as e:
        return False


if(not checkdb(rrdpath+'trend.rrd')):
    createRRD()
while(1):
    capturar()
