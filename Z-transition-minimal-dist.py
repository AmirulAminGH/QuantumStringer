from tkinter import Tk
from tkinter.filedialog import askopenfilename
import math
import sys #for debug only

inputArray=[]
outputArray=[]
zFeedrate=1000
zStepResolution=800
data_array = []  # Initialize an empty array
currentx=0.00
currenty=0.00
pastx=0.00
pasty=0.00
futurex=0.00
futurey=0.00
# Create a Tkinter root window
root = Tk()
root.withdraw()  # Hide the root window

# Prompt the user to select a file
file_path = askopenfilename()

# Check if a file was selected
if file_path:
    print("Selected file:", file_path)
else:
    print("No file selected.")
def filter_lines_by_banned_words(lines, banned_words):
    filtered_lines = [line for line in lines if all(banned_word not in line for banned_word in banned_words)]
    return filtered_lines
def remove_consecutive_duplicates(arr):
    result = []
    prev_line = None

    for line in arr:
        if line != prev_line:
            result.append(line)
            prev_line = line

    return result
def calculate_angle(x1,y1,x2,y2,x3,y3):

    primaryX=x2-x1
    primaryY=y2-y1
    mainAngle=math.degrees(math.atan2(primaryX,primaryY))
    if mainAngle < 0:
        mainAngle+=360

    nextX=x3-x2
    nextY=y3-y2
    secondaryAngle=math.degrees(math.atan2(nextX,nextY))
    if secondaryAngle < 0:
        secondaryAngle+=360

    deltaAngle=secondaryAngle-mainAngle

    if deltaAngle > 180:
        deltaAngle-=360

    return deltaAngle
# Open the file
with open(file_path, "r") as file:
    # Read the file line by line
    for line in file:
        # Remove any trailing whitespace or newline characters
        line = line.strip()

        # Append the line to the array
        data_array.append(line)


# Print the array to verify the data
print(data_array)
data_array = [line for line in data_array if "G68 P2" not in line]
# Split each string in the list and create a 2D array
inputArray = [string.split() for string in data_array]
print(inputArray)
#sys.exit(0)
inputArray=remove_consecutive_duplicates(inputArray)

# Add an extra column with the value 'Z0' to each row
for row in inputArray:
    if "G00" in row or "G01" in row:
        row.append('Znull')
rowCount=0
for row in inputArray:
    row.insert(0,"ID{}".format(int(rowCount)))
    rowCount+=1
rowCount=0
print(inputArray)
outputArray=[]
for idr in range(len(inputArray)):
    if "Znull" in inputArray[idr]:
        outputArray.append(inputArray[idr])
print("z is")

outputArray.insert(0,["IDinit","G00","X-100","Y0","Znull"])
print(outputArray)
for idt in range(len(outputArray)-2):
        pastx=float(outputArray[idt][2].strip("X"))
        pasty=float(outputArray[idt][3].strip("Y"))
        currentx = float(outputArray[idt+1][2].strip("X"))
        currenty = float(outputArray[idt+1][3].strip("Y"))
        futurex = float(outputArray[idt+2][2].strip("X"))
        futurey = float(outputArray[idt+2][3].strip("Y"))

        angleChange=calculate_angle(pastx,pasty,currentx,currenty,futurex,futurey)
        #print(angleChange)
        if angleChange== -180:
            angleChange=0.00
        outputArray[idt+2][4]="Z"+str(angleChange)

finalArray=[]
for idq in range(len(inputArray)):
    finalArray.append(inputArray[idq])
    for idw in range (len(outputArray)):
        if inputArray[idq][0]==outputArray[idw][0]:
            finalArray[idq]=outputArray[idw]
#for row in finalArray:
#    finalArray.pop(0)
print("----------------")
print(finalArray)

print("new array")
finalArray=[sublist[1:] for sublist in finalArray]
finalArray= sum([[sublist, ['pass']] for sublist in finalArray], [])[:-1]
for sublist in finalArray:
    if 'Znull' in sublist:
        sublist.remove('Znull')


for ida in range (len(finalArray)):
    if len(finalArray[ida])>=4:
        temp=finalArray[ida][3]
        finalArray[ida-1]=['G05',temp]
#finalArray = [[el] if not isinstance(el, list) else el for el in finalArray]

for sublist in finalArray:
    if len(sublist) >= 4:
        del sublist[3]
# Remove the ['pass'] sublist
finalArray = [sublist for sublist in finalArray if sublist != ['pass']]
print("debug point 1")
print(finalArray)

# testArray=finalArray
# criticalAngle=10.0
# totalAngle=0.00
# zRange=800.0
# for idt in range(len(testArray)):
#     if "G05" in testArray[idt][0]:
#         if testArray[idt - 1][0] == 'G01':
#             testAngel = float(testArray[idt][1].strip("Z"))
#             if abs(testAngel)<criticalAngle:
#                 tempAngle=(testAngel*(zRange/360.0))+totalAngle
#                 totalAngle=tempAngle
#                 testArray[idt-1].append("Z{}".format(tempAngle))
#                 testArray[idt][1]="null"
#             if abs(testAngel)>=criticalAngle:
#                 tempAngle = (testAngel * (zRange / 360.0)) + totalAngle
#                 totalAngle = tempAngle
#                 testArray[idt][1]="Z{}".format(tempAngle)
#                 testArray[idt][0]="G99"
#
# print("test point 2")
# print(testArray)

#transition algorithm
smallestRange=1000
prevY=0.00
prevX=0.00
for idv in range(len(finalArray)):
    if 'G01' in finalArray[idv][0]:
        currentx = float(finalArray[idv][1].strip("X"))
        currenty = float(finalArray[idv][2].strip("Y"))
        currentRange=math.sqrt(pow((currentx-prevX),2)+pow((currenty-prevY),2))
        if currentRange<smallestRange:
            smallestRange=currentRange
        prevX=currentx
        prevY=currenty
print("smallest range is:")
print(smallestRange)



# delta transition algorithm begin
#transitionRange=1
transitionRange=((smallestRange-1)/2)

for ide in range(len(finalArray)):
    if 'G05' in finalArray[ide][0]:
        if finalArray[ide-1][0]=='G01' and finalArray[ide+1][0]=='G01':
            #transition algorithm begin
            thetaAngle = float(finalArray[ide][1].strip("Z"))
            pastVector=[0,0,0,0]
            futureVector=[0,0,0,0]
            pastVector[2]=float(finalArray[ide-1][1].strip("X"))
            pastVector[3] = float(finalArray[ide - 1][2].strip("Y"))
            futureVector[0] = float(finalArray[ide-1][1].strip("X"))
            futureVector[1] = float(finalArray[ide-1][2].strip("Y"))
            futureVector[2] = float(finalArray[ide+1][1].strip("X"))
            futureVector[3] = float(finalArray[ide+1][2].strip("Y"))
            idxreverse=2
            while finalArray[ide-idxreverse][0] !='G01' and finalArray[ide-idxreverse][0] !='G00':
                idxreverse=idxreverse+1
                print(idxreverse)
            pastVector[0] = float(finalArray[ide - idxreverse][1].strip("X"))
            pastVector[1] = float(finalArray[ide - idxreverse][2].strip("Y"))
            print("vector is")
            print(pastVector)
            print(futureVector)
            pastdx=pastVector[2]-pastVector[0]
            pastdy=pastVector[3]-pastVector[1]
            futuredx = futureVector[2] - futureVector[0]
            futuredy = futureVector[3] - futureVector[1]

            if abs(thetaAngle)>180:
                if thetaAngle>0:
                    thetaAngle=thetaAngle-360
                if thetaAngle<0:
                    thetaAngle=thetaAngle+360
            if abs(thetaAngle)<=180:
                thetaAngle=thetaAngle
            az=thetaAngle/2
            if pastdx==0:
                ax=pastVector[2]
                if pastdy > 0:
                    ay=pastVector[3]-transitionRange
                if pastdy < 0:
                    ay = pastVector[3] + transitionRange
                if pastdy==0:
                    ay = pastVector[3]
                #az=thetaAngle/2
                finalArray[ide][0]='G06 X{} Y{} Z{}'.format(ax,ay,az)
            if pastdy==0:
                if pastdx > 0:
                    ax=pastVector[2]-transitionRange
                if pastdx < 0:
                    ax=pastVector[2]+transitionRange
                if pastdx==0:
                    ax=pastVector[2]
                ay=pastVector[3]
                #az=thetaAngle/2
                finalArray[ide][0]='G06 X{} Y{} Z{}'.format(ax,ay,az)
            if pastdy!=0 and pastdx!=0:
                pastGradient=pastdy/pastdx
                deltax=math.sqrt((transitionRange**2)/((pastGradient**2) + 1))
                deltay=pastGradient*deltax
                if pastdx > 0 :
                    ax=pastVector[2]-abs(deltax)
                if pastdx < 0 :
                    ax=pastVector[2]+abs(deltax)
                if pastdy > 0 :
                    ay=pastVector[3]-abs(deltay)
                if pastdy < 0 :
                    ay=pastVector[3]+abs(deltay)
                #az=thetaAngle/2
                finalArray[ide][0] = 'G06 X{} Y{} Z{}'.format(ax, ay, az)
                print(finalArray[ide][0])
                print("dy is {}".format(pastdy))

            if futuredx==0:
                ax=futureVector[0]
                if futuredy>0:
                    ay=futureVector[1]+transitionRange
                if futuredy<0:
                    ay=futureVector[1]-transitionRange
                if futuredy==0:
                    ay=futureVector[1]
                #az=thetaAngle/2
                finalArray[ide][1]='G07 X{} Y{} Z{}'.format(ax,ay,az)
            if futuredy==0:
                if futuredx>0:
                    ax = futureVector[0] + transitionRange
                if futuredx<0:
                    ax = futureVector[0] - transitionRange
                if futuredx==0:
                    ax= futureVector[0]
                ay = futureVector[1]
                #az=thetaAngle/2
                finalArray[ide][1] = 'G07 X{} Y{} Z{}'.format(ax, ay, az)
            if futuredx!=0 and futuredy!=0:
                futureGradient=futuredy/futuredx
                deltax=math.sqrt((transitionRange**2)/((futureGradient**2) + 1))
                deltay=futureGradient*deltax
                if futuredx > 0:
                    ax=futureVector[0]+abs(deltax)
                if futuredx < 0:
                    ax = futureVector[0] - abs(deltax)
                if futuredy > 0:
                    ay=futureVector[1]+abs(deltay)
                if futuredy < 0:
                    ay=futureVector[1]-abs(deltay)
                #az=thetaAngle/2
                finalArray[ide][1] = 'G07 X{} Y{} Z{}'.format(ax, ay, az) # change from G07 to G06

print("debug point 2")
print(finalArray)
#rearrage and filtering
for line in finalArray:
    if line[0]=='G05':
        line[0]='G01'
updated_line=[]
for line in finalArray:

    if 'G06' in line[0]:
        updated_line.append([line[0]])
        updated_line.append([line[1]])
    else:
        updated_line.append(line)

finalArray=updated_line

updated_line_2=[]
for line in finalArray:
    if 'G06' in line[0] or 'G07' in line[0]:
        tempswap=line[0].split()
        updated_line_2.append(tempswap)
    else:
        updated_line_2.append(line)
finalArray=updated_line_2

for idc in range(len(finalArray)):
    if 'G06' in finalArray[idc][0]:
        swapvalx=finalArray[idc][1]
        finalArray[idc][1]=finalArray[idc-1][1]
        finalArray[idc-1][1]=swapvalx
        swapvaly = finalArray[idc][2]
        finalArray[idc][2] = finalArray[idc - 1][2]
        finalArray[idc - 1][2] = swapvaly
        finalArray[idc][0]="G01"
    if 'G07' in finalArray[idc][0]:
        # swapval = finalArray[idc][1]
        # finalArray[idc][1] = finalArray[idc + 1][1]
        # finalArray[idc + 1][1] = swapval
        finalArray[idc][0] = "G01"

Zrange=800.0
currentZ=0.0
print("output before conversion")
print(finalArray)
for idk in range (len(finalArray)):
    for idy in range(len(finalArray[idk])):
        if 'Z'in finalArray[idk][idy]:
            tempAngle=float(finalArray[idk][idy].strip("Z"))
            #print("temp angle is {}".format(tempAngle))
            tempAngle=tempAngle*(Zrange/360)
            currentZ+=tempAngle
            #print(" and converted to {}".format(currentZ))
            finalArray[idk][idy]="Z"+str(currentZ)











        #angle=calculate_angle(pastx,pasty,currentx,currenty,futurex,futurey)
        #print("angle {} is {}".format(idt,angle))

print("final output")
print(finalArray)
converted_text = ""

for command in finalArray:
    converted_command = " ".join(command)
    converted_text += converted_command + "\n"

print(converted_text)
file_path = "C:/Users/VICTUS/Downloads/Zoutput.txt"
with open(file_path, "w") as file:
    # Write the text to the file
    file.write(converted_text)

print("Text successfully saved to", file_path)

print("smallest range is:")
print(smallestRange)
