from tkinter import Tk
from tkinter.filedialog import askopenfilename
import math

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
# Split each string in the list and create a 2D array
inputArray = [string.split() for string in data_array]
print(inputArray)
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
        pastx=int(outputArray[idt][2].strip("X"))
        pasty=int(outputArray[idt][3].strip("Y"))
        currentx = int(outputArray[idt+1][2].strip("X"))
        currenty = int(outputArray[idt+1][3].strip("Y"))
        futurex = int(outputArray[idt+2][2].strip("X"))
        futurey = int(outputArray[idt+2][3].strip("Y"))

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
print(finalArray)

transitionRange=5.0
for ide in range(len(finalArray)):
    if 'G05' in finalArray[ide][0]:
        if finalArray[ide-1][0]=='G01' and finalArray[ide+1][0]=='G01':
            #transition algorithm begin
            thetaAngle = float(finalArray[ide][1].strip("Z"))
            pastVector=[0,0,0,0]
            futureVector=[0,0,0,0]
            pastVector[2]=int(finalArray[ide-1][1].strip("X"))
            pastVector[3] = int(finalArray[ide - 1][2].strip("Y"))
            futureVector[0] = int(finalArray[ide-1][1].strip("X"))
            futureVector[1] = int(finalArray[ide-1][2].strip("Y"))
            futureVector[2] = int(finalArray[ide+1][1].strip("X"))
            futureVector[3] = int(finalArray[ide+1][2].strip("Y"))
            idxreverse=2
            while finalArray[ide-idxreverse][0] !='G01' and finalArray[ide-idxreverse][0] !='G00':
                idxreverse=idxreverse+1
                print(idxreverse)
            pastVector[0] = int(finalArray[ide - idxreverse][1].strip("X"))
            pastVector[1] = int(finalArray[ide - idxreverse][2].strip("Y"))
            print("vector is")
            print(pastVector)
            print(futureVector)
            pastdx=pastVector[2]-pastVector[0]
            pastdy=pastVector[3]-pastVector[1]
            futuredx = futureVector[2] - futureVector[0]
            futuredy = futureVector[3] - futureVector[1]

            if pastdx==0:
                ax=pastVector[2]
                ay=pastVector[3]-transitionRange
                az=thetaAngle/2
                finalArray[ide][0]='G06 X{} Y{} Z{}'.format(ax,ay,az)
            if pastdy==0:
                ax=pastVector[2]-transitionRange
                ay=pastVector[3]
                az=thetaAngle/2
                finalArray[ide][0]='G06 X{} Y{} Z{}'.format(ax,ay,az)
            if pastdy!=0 and pastdx!=0:
                pastGradient=pastdy/pastdx
                deltax=math.sqrt((transitionRange**2)/((pastGradient**2) + 1))
                deltay=pastGradient*deltax
                ax=pastVector[2]-deltax
                ay=pastVector[3]-deltay
                az=thetaAngle/2
                finalArray[ide][0] = 'G06 X{} Y{} Z{}'.format(ax, ay, az)

            if futuredx==0:
                ax=futureVector[0]
                ay=futureVector[1]+transitionRange
                az=thetaAngle/2
                finalArray[ide][1]='G07 X{} Y{} Z{}'.format(ax,ay,az)
            if futuredy==0:
                ax = futureVector[0] + transitionRange
                ay = futureVector[1]
                az = thetaAngle/2
                finalArray[ide][1] = 'G07 X{} Y{} Z{}'.format(ax, ay, az)
            if futuredx!=0 and futuredy!=0:
                futureGradient=futuredy/futuredx
                deltax=math.sqrt((transitionRange**2)/((futureGradient**2) + 1))
                deltay=futureGradient*deltax
                ax=futureVector[0]+deltax
                ay=futureVector[1]+deltay
                az=thetaAngle/2
                finalArray[ide][0] = 'G07 X{} Y{} Z{}'.format(ax, ay, az)


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
        swapval=finalArray[idc][1]
        finalArray[idc][1]=finalArray[idc-1][1]
        finalArray[idc-1][1]=swapval
        finalArray[idc][0]="G01"
    if 'G07' in finalArray[idc][0]:
        swapval = finalArray[idc][1]
        finalArray[idc][1] = finalArray[idc + 1][1]
        finalArray[idc + 1][1] = swapval
        finalArray[idc][0] = "G01"

Zrange=800.0
currentZ=0.0
for idk in range (len(finalArray)):
    for idy in range(len(finalArray[idk])):
        if 'Z'in finalArray[idk][idy]:
            tempAngle=float(finalArray[idk][idy].strip("Z"))
            tempAngle=tempAngle*(Zrange/360)
            currentZ+=tempAngle
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


