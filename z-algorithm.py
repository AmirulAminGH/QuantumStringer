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
print("final array")
print(finalArray)

        #angle=calculate_angle(pastx,pasty,currentx,currenty,futurex,futurey)
        #print("angle {} is {}".format(idt,angle))


#print(outputArray)



