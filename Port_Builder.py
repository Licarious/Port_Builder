from PIL import Image
import glob
import copy


#flag for selcting which type of water the new ports should go on
waterTypeFlag = "river" #river or sea
portScale = 0.75



class ProvinceDefinition:
    id = 0
    red = 0
    green = 0
    blue = 0
    name = ""
    other_info = ""
    lastKnownY = -1
    def getRGB(self):
        return((self.red,self.green,self.blue,255))

class Port:
    landID = 0
    waterID = 0
    landRGB = (0,0,0)
    waterRGB = (0,0,0)
    xyCityTupple = (0,0)
    xyPortTupple = (0,0)
    facingDirection = ""
    
riverList = []
tmpRiverList = []
riverProvList = []
provList = []
provColorList = []
tupleList = []
adjList = []
fullProvList = []
fullProvColorList = []

wastelandList = [] #contains everything that is not habital lands

riverArray = []
riverBorderArray = []
riverCordTuppleList = []

portList = []

mapDefinition = open("Input/definition.csv")
defaultMap = open("Input/default.map")
provMap = Image.open("Input/provinces.png")
provMap.putalpha(255)
borderIDList = []

def readProvinceDeff():
    for province in mapDefinition:
        if province.strip().startswith("#"):
            pass
        else:
            tmpline = province.strip().split(';')
            try:
                province = ProvinceDefinition()
                province.red = int(tmpline[1])
                province.id = int(tmpline[0].lstrip("#"))
                province.green = int(tmpline[2])
                province.blue = int(tmpline[3])
                province.name = tmpline[4]
                provList.append(province)
            except:
                pass
            try:
                province = ProvinceDefinition()
                province.red = int(tmpline[1])
                province.id = int(tmpline[0].lstrip("#"))
                province.green = int(tmpline[2])
                province.blue = int(tmpline[3])
                province.name = tmpline[4]
                fullProvList.append(province)
                fullProvColorList.append((province.red,province.green,province.blue,255))
            except:
                pass
    pass
def getRangeList(line, tmpList):
    if "RANGE" in line:
        x1=0
        x2=0
        #print(line)
        words = line.split(" ")
        for word in words:
            if "#" in word:
                break
            else:
                try:
                    if x1 == 0:
                        x1 = int(word)
                    elif x2 == 0:
                        x2 = int(word)
                except:
                    pass
        for i in range(x1,x2+1):
            tmpList.append(i)
        #print("%s,%s"%(x1,x2))
    elif "LIST" in line:
        words = line.split(" ")
        for word in words:
            if "#" in word:
                break
            else:
                try:
                    tmpList.append(int(word))
                except:
                    pass
    pass
def getRiverProvinces():
    for line in defaultMap:
        if line.strip().startswith("#"):
            pass
        elif "river" in waterTypeFlag and line.strip().startswith("river_provinces"):
            getRangeList(line, riverList)
            getRangeList(line, wastelandList)
        elif "sea" in waterTypeFlag and line.strip().startswith("sea_zones"):
            getRangeList(line, riverList)
            getRangeList(line, wastelandList)
        elif line.strip().startswith("wasteland") or line.strip().startswith("impassable_terrain") or line.strip().startswith("uninhabitable") or line.strip().lower().startswith("lakes"):
            getRangeList(line, wastelandList)
    pass  
def drawMat(riverProvList):
    xRange= range(0,provMap.size[0],1)
    yRange= range(0,provMap.size[1],1)
    drawReader = provMap.load()
    drawingMap = Image.open("Input/provinces.png")
    drawingMap.putalpha(0)
    riverMat = drawingMap.load()
    z=0
    dis = 5

    tupleList = []
    lastY = []
    for prov in riverProvList:
        tupleList.append(prov.getRGB())
        lastY.append(-1)

    print("Drawing Maps:")
    tmpTotal = len(tupleList)
    count = 0

    #print(tupleList[0])

    for y in yRange:
        #print(drawReader[150,y])
        
        if y%128 ==0:
            #print(drawReader[5,y])
            #print("%i%%"%((y*100)/provMap.size[1]))
            for i, prov in enumerate(lastY):
                if prov>-1 and prov<y-(provMap.size[1]/40):
                    #print(tupleList[i])
                    del lastY[i]
                    del tupleList[i]
                    i-=1
                    count+=1
            if tmpTotal>0 and count>0:
                #print(count)
                print("%f%%"%((count*1000/tmpTotal)/10))
            if tupleList==0:
                break
        for x in xRange:
            if drawReader[x,y] in tupleList:
                #print(x)
                riverMat[x,y] = (0,0,0,255)
                lastY[tupleList.index(drawReader[x,y])] = y
                #riverCordTuppleList.append((x,y))
    drawingMap.save("Output/RiverMat.png")
def drawBorderMat():
    xRange= range(0,provMap.size[0],1)
    yRange= range(0,provMap.size[1],1)
    tmpDrawingMap = Image.open("Output/RiverMat.png")
    
    drawReader = tmpDrawingMap.load()
    drawingBorderMap = Image.open("Input/provinces.png")
    drawingBorderMap.putalpha(0)
    riverBorderMat = drawingBorderMap.load()
    print("getting %s borders:"%waterTypeFlag)
    for y in yRange:
        if y%128 ==0:
            print("%g%%"%(float(y)/float(provMap.size[1])*100))
        for x in xRange:
            if drawReader[x,y] == (0,0,0,255):
                #print("%s,%s"%(x,y))
                if y>0:
                    if not drawReader[x,y-1] == (0,0,0,255):
                        riverBorderMat[x,y-1] = (0,0,0,255)
                        if (x,y) not in riverCordTuppleList:
                            riverCordTuppleList.append((x,y))
                if y<provMap.size[1]-1:
                    if not drawReader[x,y+1] == (0,0,0,255):
                        riverBorderMat[x,y+1] = (0,0,0,255)
                        if (x,y) not in riverCordTuppleList:
                            riverCordTuppleList.append((x,y))
                if x>0:
                    if not drawReader[x-1,y] == (0,0,0,255):
                        riverBorderMat[x-1,y] = (0,0,0,255)
                        if (x,y) not in riverCordTuppleList:
                            riverCordTuppleList.append((x,y))
                if x<provMap.size[0]-1:
                    if not drawReader[x+1,y] == (0,0,0,255):
                        riverBorderMat[x+1,y] = (0,0,0,255)
                        if (x,y) not in riverCordTuppleList:
                            riverCordTuppleList.append((x,y))
                #print("%s - %i,%i"%(prov.name,x,y))
    drawingBorderMap.save("Output/RiverBorderMat.png")
def getBorderIDs():
    xRange= range(0,provMap.size[0],1)
    yRange= range(0,provMap.size[1],1)
    drawReader = provMap.load()
    borderMat = Image.open("Output/RiverBorderMat.png")
    riverBorderMat = borderMat.load()
    colorList = []
    for y in yRange:
        for x in xRange:
            if riverBorderMat[x,y] == (0,0,0,255):
                if not provMap.getpixel((x,y)) in colorList:
                    colorList.append(provMap.getpixel((x,y)))
                    #print(provMap.getpixel((x,y)))
    for color in colorList:
        for prov in provList:
            #if color[0] == prov.red and color[1] == prov.green and color[2] == prov.blue:
            if color == prov.getRGB():
                #print(prov.name)
                borderIDList.append(prov.id)
                break;
    pass
def riverAdjacent():
    xRange= range(0,provMap.size[0],1)
    yRange= range(0,provMap.size[1],1)
    borderMat = Image.open("Output/RiverBorderMat.png")
    riverBorderMat = borderMat.load()
    drawReader = provMap.load()
    print("Getting %s adjacent settlemnts"%waterTypeFlag)
    for y in yRange:
        if y%128 ==0:
            print("\t%i%%"%((y*100)/provMap.size[1]))
        for x in xRange:
            if riverBorderMat[x,y] == (0,0,0,255):
                if not drawReader[x,y] in riverBorderArray:
                    riverBorderArray.append(drawReader[x,y])
                    #print(drawReader[x,y])
pass


readProvinceDeff()
def getCityPosition():
    cityFile = open("Input/city_locators.txt")
    correctProv = False
    port = Port()
    for line in cityFile:
        if line.strip().startswith('id'):
            if int(line.split('=')[1].strip()) in portsNeededIDs:
                correctProv = True
                #print(line.split('=')[1].strip())
                #tmpCityID = line.split('=')[1].strip()
                port.landID = int(line.split('=')[1].strip())
        if correctProv and line.strip().startswith('position'):
            correctProv = False
            #print("%i , %i"%(int(float(line.split('=')[1].strip().split(' ')[1])),provMap.size[1]-int(float(line.split('=')[1].strip().split(' ')[3]))))
            #tmpCityTupple = (line.split('=')[1].strip().split(' ')[1],line.split('=')[1].strip().split(' ')[3])
            port.xyCityTupple = (int(float(line.split('=')[1].strip().split(' ')[1])),provMap.size[1]-int(float(line.split('=')[1].strip().split(' ')[3])))
            portList.append(port)
            port = Port()
    pass

getRiverProvinces()
for id in riverList:
    for prov in provList:
        if id == prov.id:
            #print(prov.getRGB())
            #print(prov.name)
            riverProvList.append(prov)
            provColorList.append((prov.red,prov.green,prov.blue))
            break
    pass
drawMat(riverProvList)
drawBorderMat()
riverAdjacent()


exitingPorts = []
def getExistingPorts():
    portsFile = open("Input/ports.csv")
    for line in portsFile:
        if line.strip().startswith("#") or line.strip().startswith("LandProvince") or line.strip().startswith("end") or line.strip() == "":
            pass
        else:
            exitingPorts.append(int(line.split(";")[0]))
            #print(line.split(";")[0])

getExistingPorts()
getBorderIDs()



portsNeededIDs = []
def newPortsNeeded():
    for i in borderIDList:
        if i in exitingPorts:
            pass
        elif i in wastelandList:
            pass
        else:
            portsNeededIDs.append(i)
newPortsNeeded()
getCityPosition()

c=0
PortCSVOut = open("Output/ports_output.csv", 'w')
PortLocOut = open("Output/port_locators_output.txt", 'w')
tmpRiverCordTuppleList = []
refreshTmpList = True
print("Generating port position and rotation (This might take a while)")
for port in portList:
    if refreshTmpList:
        tmpRiverCordTuppleList = copy.deepcopy(riverCordTuppleList)
        refreshTmpList = False
    foundAdj = False
    for prov in provList:
        if prov.id == port.landID:
            port.landRGB = prov.getRGB()
            break

    c+=1
    print("\t%i / %i"%(c,len(portList)))
    while not foundAdj:
        port.xyPortTupple = min(tmpRiverCordTuppleList, key=lambda point: (point[0] - port.xyCityTupple[0])**2 + (point[1] - port.xyCityTupple[1])**2)

        #South  -   rotation={ -0.000000 -0.000000 -0.000000 1.000000 }
        #West   -   rotation={ -0.000000 -0.639206 -0.000000 0.769035 }
        #North  -   rotation={ -0.000000 -1.000000 -0.000000 -0.000000 }
        #East   -   rotation={ -0.000000 0.729796 -0.000000 0.683664 }
        #SW     -   rotation={ -0.000000 -0.287422 -0.000000 0.957804 }
        #NW     -   rotation={ -0.000000 -0.874790 -0.000000 0.484502 }
        #NE     -   rotation={ -0.000000 0.910970 -0.000000 0.412472 }
        #SE     -   rotation={ -0.000000 0.427556 -0.000000 0.903988 }

        #make sure that the closest water to the city is actualy adjacent to the prov
        if port.landRGB == provMap.getpixel((port.xyPortTupple[0]+1,port.xyPortTupple[1])):
            if port.landRGB == provMap.getpixel((port.xyPortTupple[0]+1,port.xyPortTupple[1]+1)) and port.landRGB == provMap.getpixel((port.xyPortTupple[0]+1,port.xyPortTupple[1]-1)):
                port.facingDirection = "West"
                foundAdj = True
                port.waterRGB = provMap.getpixel(port.xyPortTupple)[0:3]
                port.xyPortTupple = (port.xyPortTupple[0]+1,port.xyPortTupple[1])
                break
            elif port.landRGB == provMap.getpixel((port.xyPortTupple[0]+2,port.xyPortTupple[1]+1)) and port.landRGB == provMap.getpixel((port.xyPortTupple[0],port.xyPortTupple[1]-1)):
                port.facingDirection = "SW"
                foundAdj = True
                port.waterRGB = provMap.getpixel(port.xyPortTupple)[0:3]
                port.xyPortTupple = (port.xyPortTupple[0]+1,port.xyPortTupple[1])
                break
            elif port.landRGB == provMap.getpixel((port.xyPortTupple[0]+2,port.xyPortTupple[1]-1)) and port.landRGB == provMap.getpixel((port.xyPortTupple[0],port.xyPortTupple[1]+1)):
                port.facingDirection = "NW"
                foundAdj = True
                port.waterRGB = provMap.getpixel(port.xyPortTupple)[0:3]
                port.xyPortTupple = (port.xyPortTupple[0]+1,port.xyPortTupple[1])
                break
        if port.landRGB == provMap.getpixel((port.xyPortTupple[0],port.xyPortTupple[1]+1)):
            if port.landRGB == provMap.getpixel((port.xyPortTupple[0]+1,port.xyPortTupple[1]+2)) and port.landRGB == provMap.getpixel((port.xyPortTupple[0]-1,port.xyPortTupple[1])):
                port.facingDirection = "North"
                foundAdj = True
                port.waterRGB = provMap.getpixel(port.xyPortTupple)[0:3]
                port.xyPortTupple = (port.xyPortTupple[0],port.xyPortTupple[1]+1)
                break
            elif port.landRGB == provMap.getpixel((port.xyPortTupple[0]+1,port.xyPortTupple[1]+2)) and port.landRGB == provMap.getpixel((port.xyPortTupple[0]-1,port.xyPortTupple[1])):
                port.facingDirection = "NE"
                foundAdj = True
                port.waterRGB = provMap.getpixel(port.xyPortTupple)[0:3]
                port.xyPortTupple = (port.xyPortTupple[0],port.xyPortTupple[1]+1)
                break
        if port.landRGB == provMap.getpixel((port.xyPortTupple[0]-1,port.xyPortTupple[1])):
            if port.landRGB == provMap.getpixel((port.xyPortTupple[0]-1,port.xyPortTupple[1]-1)) and port.landRGB == provMap.getpixel((port.xyPortTupple[0]-1,port.xyPortTupple[1]+1)):
                port.facingDirection = "East"
                foundAdj = True
                port.waterRGB = provMap.getpixel(port.xyPortTupple)[0:3]
                port.xyPortTupple = (port.xyPortTupple[0]-1,port.xyPortTupple[1])
                break
            elif port.landRGB == provMap.getpixel((port.xyPortTupple[0]-2,port.xyPortTupple[1]+1)) and port.landRGB == provMap.getpixel((port.xyPortTupple[0],port.xyPortTupple[1]-1)):
                port.facingDirection = "SE"
                foundAdj = True
                port.waterRGB = provMap.getpixel(port.xyPortTupple)[0:3]
                port.xyPortTupple = (port.xyPortTupple[0]-1,port.xyPortTupple[1])
                break

        if port.landRGB == provMap.getpixel((port.xyPortTupple[0],port.xyPortTupple[1]-1)):
            if port.landRGB == provMap.getpixel((port.xyPortTupple[0]-1,port.xyPortTupple[1]-1)) and port.landRGB == provMap.getpixel((port.xyPortTupple[0]+1,port.xyPortTupple[1]-1)):
                port.facingDirection = "South"
                foundAdj = True
                port.waterRGB = provMap.getpixel(port.xyPortTupple)[0:3]
                port.xyPortTupple = (port.xyPortTupple[0],port.xyPortTupple[1]-1)
                break
        #print("%i not adj to (%i, %i)"%(port.landID,port.xyPortTupple[0],port.xyPortTupple[1]))
        tmpRiverCordTuppleList.remove(port.xyPortTupple)
        refreshTmpList = True

    port.waterID = riverProvList[provColorList.index(port.waterRGB)].id

    PortLocOut.write("\t\t{")
    PortLocOut.write("\n\t\t\tid=%i"%port.landID)
    PortLocOut.write("\n\t\t\tposition={ %i 0 %i }"%(port.xyPortTupple[0],int(provMap.size[1])-int(port.xyPortTupple[1])))
    if port.facingDirection == "South":
        PortLocOut.write("\n\t\t\trotation={ -0.000000 -0.000000 -0.000000 1.000000 }")
    elif port.facingDirection == "West":
        PortLocOut.write("\n\t\t\trotation={ -0.000000 -0.672702 -0.000000 0.739914 }")
    elif port.facingDirection == "North":
        PortLocOut.write("\n\t\t\trotation={ -0.000000 -1.000000 -0.000000 -0.000000 }")
    elif port.facingDirection == "East":
        PortLocOut.write("\n\t\t\trotation={ -0.000000 0.736881 -0.000000 0.676022 }")
    elif port.facingDirection == "SW":
        PortLocOut.write("\n\t\t\trotation={ -0.000000 -0.874790 -0.000000 0.484502 }")
    elif port.facingDirection == "NW":
        PortLocOut.write("\n\t\t\trotation={ -0.000000 0.736881 -0.000000 0.676022 }")
    elif port.facingDirection == "NE":
        PortLocOut.write("\n\t\t\trotation={ -0.000000 0.910970 -0.000000 0.412472 }")
    elif port.facingDirection == "SE":
        PortLocOut.write("\n\t\t\trotation={ -0.000000 0.427556 -0.000000 0.903988 }")
    PortLocOut.write("\n\t\t\tscale={ %g %g %g }"%(portScale,portScale,portScale))
    PortLocOut.write("\n\t\t}\n")

    PortCSVOut.write("%i;%i;%i;%i;\n"%(port.landID,port.waterID,port.xyPortTupple[0],int(provMap.size[1])-int(port.xyPortTupple[1])))

PortCSVOut.close()
PortLocOut.close()