#/Volumes/InfinityStone/Reality/Projects/tools
#!/usr/bin/python
import sys, getopt, inspect, os, subprocess, re, time
from codetamper import mainfestdebuggable
from codetamper import usercertificate
from codetamper import ifTestOnlyAPK

millis              = str(int(round(time.time() * 1000)))
SUCCESS             = 0
AUTOMATION          = 1
MANNUAL             = 2
verbose             = False
debuggable_mode     = False

def myworkspace():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def myCommand_silent(command):
    #global verbose
    if verbose == False:
        FNULL = open(os.devnull, 'w')
        process = subprocess.call(command, shell=True,stdout=FNULL, stderr=subprocess.STDOUT)
    else:
        print (command)
        process = subprocess.call(command, shell=True)
        print '------------------------------'




def myCommand(text,command,second):
    print text
    #global verbose
    if verbose == False:
        FNULL = open(os.devnull, 'w')
        process = subprocess.Popen(command, shell=True,stdout=FNULL, stderr=subprocess.STDOUT)
    else:
        print '------------------------------'
        process = subprocess.Popen(command, shell=True)
        print '*******************************'
    print second
    print '------------------------------'

    process.communicate()
    if process.returncode != SUCCESS:
        terminate("/n Could not proceed further at "+command+". Raise a ticket=> https://github.com/51j0/Android-CertKiller/issues/new")

def terminate(var):
    print var
    sys.exit(2)

def intro(var):
    print '\n***************************************'
    print 'Android CertKiller (v0.1)'
    print '***************************************\n'
    print var
    print '---------------------------------'



def getRealPackageName(package_name):
    #SEARCHING FOR PACKAGE
    global SUCCESS

    command = "adb shell pm list packages -f "+package_name
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.communicate()

    if process.returncode != SUCCESS:
        print 'Something went wrong (ER_Ox1001)'
        sys.exit(2)

    orginal_package_name = output[0]
    counts = orginal_package_name.count('\n')

    if counts > 1:
        print orginal_package_name
        print "\n---------------------------------------"
        print "Found "+str(counts)+" packages"
        return ""
    elif counts == 0:
        print "\n---------------------------------------"
        text = raw_input("No application found with the given package name. Do you want to Continue(y/N) ")
        if text == '' or text == 'N' or text == 'n':
            terminate("Ending script")
        else:
            return ""



    print '--------------sijo'
    print orginal_package_name
    start_index = 8
    final_index = orginal_package_name.rfind('base.apk=')+8
    print str(start_index)+":"+str(final_index)
    package_path = orginal_package_name[start_index:final_index]
    package_path = package_path.replace("\n", "")
    package_path = package_path.replace("\r", "")
    return package_path;

def runwizard():
    intro('CertKiller Wizard Mode')
    command = "adb devices -l"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.communicate()
    print output[0]

    if process.returncode != SUCCESS:
        terminate("Could not proceed further please reinstall ADB")
    #os.system("adb devices")
    #os.system("echo '---------------------------------\n'")
    package_name = raw_input("Enter Application Package Name: ")
    package_name = getRealPackageName(package_name)
    while package_name == '':
        package_name = raw_input("Enter Application Package Name: ")
        package_name = getRealPackageName(package_name)

    print "my packages "+package_name
    if package_name != '':
        os.system("echo '\nPackage: "+package_name+"\n'")
        extracting(package_name,'A')
        decompileApplication()
        if debuggable_mode == True:
            mainfestdebuggable()
        usercertificate()
        compileApplication()
        signApplication("base/dist/base.apk",1)
        installApplication()
        sys.exit(2)
    else:
        terminate("Package Not Found")

def extracting(package_name,workspace):
    first   = 'I. Initiating APK extraction from device'
    second  = '   complete'
    command = "adb pull "+package_name
    myCommand(first,command,second)


def decompileApplication():
    first   = 'I. Decompiling'
    second  = '   complete'
    command = "java -jar "+myworkspace()+"/dependency/apktool.jar d -f base.apk"
    myCommand(first,command,second)


def compileApplication():
    first   = 'I. Building New APK'
    second  = '   complete'
    command = "java -jar "+myworkspace()+"/dependency/apktool.jar b -f base"
    myCommand(first,command,second)

def signApplication(path,mode):
    global millis
    first   = 'I. Signing APK'
    second  = '   complete'
    command = "jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore "+myworkspace()+"/dependency/ssl-key.keystore -storepass android -keypass android "+path+" 51j0"
    myCommand(first,command,second)

    f=open("base/AndroidManifest.xml", "r")
    contents = f.read()
    package = re.findall('package="(.*?)"', contents)
    f.close()


    if mode == AUTOMATION:
        print
        command = 'mkdir '+myworkspace()+'/unpinnedapk/'+package[0]+millis+'/'
        myCommand_silent(command)
        command = 'mkdir '+myworkspace()+'/workspace/'+package[0]+millis+'/'
        myCommand_silent(command)
        command = "mv -f base/dist/base.apk "+myworkspace()+"/unpinnedapk/"+package[0]+millis+"/base.apk"
        myCommand_silent(command)
        command = "mv -f base "+myworkspace()+"/workspace/"+package[0]+millis+"/"
        myCommand_silent(command)
        command = "mv -f base.apk "+myworkspace()+"/workspace/"+package[0]+millis+"/base.apk"
        myCommand_silent(command)
        text = raw_input("Would you like to install the APK on your device(y/N): ")
        if text == 'y' or text == "Y":
            installApplication(package[0])
        else:
            terminate("Thank you")


def installApplication(package):
    global millis
    print '------------------------------------\n Installing Unpinned APK'
    command = "adb shell pm list packages | grep "+package
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    output = process.communicate()
    if process.returncode != SUCCESS:
        terminate("Could not install. Please check")

    orginal_package_name = output[0]
    counts = orginal_package_name.count('\n')
    if counts == 1:
        command = "adb uninstall "+package
        myCommand_silent(command)


    command = "adb install "+myworkspace()+"/unpinnedapk/"+package+millis+"/base.apk"

    isTestAPK = ifTestOnlyAPK(myworkspace()+"/workspace/"+package+millis+"/base/AndroidManifest.xml")
    if isTestAPK == True:
        command = "adb install -t "+myworkspace()+"/unpinnedapk/"+package+millis+"/base.apk"

    myCommand_silent(command)
    print '------------------------------'
    print 'Finished'
    sys.exit(2)

def usage():
    print ''
    print 'root$ python main.py -w (Wizard Mode)'
    print 'root$ python main.py -p /desktop/base.apk  (Manual Mode)'
    print ''
    print  '\r -w  --wizard\t        Extract APK From device'
    print  '\r -v  --verbose\t        Verbose Mode'
    print  '\r -p  --Path\t        APK path'
    print  '\r -d  --debuggable mode\tSetting android:debuggable flag to true'
    #print  '\r -o  --output\t Output Directory for modified APK'
    print ''

def main(argv):
    global verbose
    global debuggable_mode
    path = ''
    wizard = True
    output_folder = 'A'
    try:
        opts, args = getopt.getopt(argv,"hvdwp:",["help","path=","verbose","debuggable-mode","wizard"])
    except getopt.GetoptError as err:
        usage()
        print (err)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif opt in ("-w", "--Wizard"):
            wizard = True
        elif opt in ("-p", "--path"):
            path = arg
            wizard = False
        elif opt in ("-v", "--verbose", "v"):
            verbose = True
        elif opt in ("-d", "--debuggable-mode", "d"):
            debuggable_mode = True


    if(len(opts) == 0):
        #print "\nRunning in default mode:\n"
        runwizard()


    if wizard == True :
        runwizard()
    else:
        intro('CertKiller Manual Mode')
        command = "cp "+path+" base.apk"
        myCommand_silent(command)
        decompileApplication()
        usercertificate()
        compileApplication()
        signApplication("base/dist/base.apk",1)
        installApplication()
        sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
