import optparse
from adb import Adb
from apktool import Apktool
from bypass import Bypass


parser = optparse.OptionParser()
parser.add_option('-i','--install',dest="install",default="none")
parser.add_option('-r','--uninstall',dest="uninstall",default="none")
parser.add_option('-d','--decompile',dest="decompile",default="none")
parser.add_option('-f','--file',dest="file",default="none")
parser.add_option('-c','--compile', dest="compile",default="none")
parser.add_option('-p','--pull', dest="fetch",default="none")
parser.add_option('-s','--sign', dest="sign",default="none")
parser.add_option('-l','--look', dest="look",default="none")
parser.add_option('-b','--bypass', dest="bypass",default="none")
parser.add_option('-u','--unlock',dest="unlock",action="store",default="none")
#parser.add_option('-h','--help', default="auto")
options, remainder = parser.parse_args()




if options.bypass != 'none':
    if 'sslpinning' in options.bypass or 'debugging' in options.bypass:

        value = options.file
        if(len(value)==0):
            print("Invalid Option")
            exit()

        folder = "";
        if value.endswith('.apk'):
            apktool = Apktool(value)
            apktool.decompile()
            folder = value.replace(".apk")
        elif '.' in value:
            print("Looking for %s in your device"%value)
            adb = Adb(value)
            adb.fetchApk(".")
            print("Fetching %s from device"%adb.packagename())
            apktool = Apktool("base.apk")
            apktool.decompile()
            folder = "base"
        else:
            bypass = Bypass(value)
            if(not bypass.validFolder()):
                print("Invalid Option")
                exit()

            folder = value

        if options.bypass == 'sslpinning':
            bypass = Bypass(folder)
            bypass.udpateNetworkSecurityConfig()

        if options.bypass == 'debugging':
            bypass = Bypass(folder)
            bypass.mainfestdebuggable()

        apktool = Apktool(folder)
        apktool.compile()
        apktool = Apktool("%s/dist/%s.apk"%(value,value))
        apktool.sign()

        text = input("Would you like to install the apk (y/N): ")
        if text == 'y' or text == "Y":
            adb = Adb("%s/dist/%s.apk"%(value,value))
            print(adb.install())
    else:
        print("Unknown bypass option")
elif options.install != 'none':
    adb = Adb(options.install)
    print(adb.install())
elif options.uninstall != 'none':
    adb = Adb(value)
    print(adb.uninstall())
elif options.look != 'none':
    value = options.look
    adb = Adb(value)
    name = adb.packagename()
    path = adb.getPackagePath()
    if(name != ''):
        print("#Package Name:")
        print(name)
        print("\n#Path:")
        print(path)
    else:
        print("Coundnt find any apk matching %s" %s)
elif options.fetch != "none":
    adb = Adb(options.fetch)
    print(adb.fetchApk("%s.apk"%options.fetch))
elif options.unlock != 'none':
    print("Unlocking your phone...")
    adb = Adb(options.unlock)
    print(adb.inputext())
elif options.compile != "none":
    apktool = Apktool(options.compile)
    print(apktool.compile())
    text = input("Would you like to sign the apk (y/N): ")
    if text == 'y' or text == "Y":
        apktool = Apktool("%s/dist/%s.apk"%(options.compile,options.compile))
        print(apktool.sign())
    else:
        sys.exit(2)
elif options.decompile != "none":
    apktool = Apktool(options.decompile)
    print(apktool.decompile())
elif options.sign != "none":
    apktool = Apktool(options.sign)
    print(apktool.sign())

else:
    print("Unknown Option")

#print(options)
