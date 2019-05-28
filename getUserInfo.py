DEBUGIT = False
fieldsInEtcPasswd = "Username:EncryptedPwInShadowFile:UserIdNumber:GroupIdNumber:Comments:HomeDir:Shell"
historyFields = "Username:TypeOfUser:UserCanLogin:Owner:IsPrivileged:Comments"   

# --------------------------------------------------------------------------------------------------------
# groupName2MemberList - dictionary: key is groupName, value is list of usernames within the group
# groupId2Name - dictionary: key is thr groupIdNumber, value is the groupName
# groupsUserNameIn - dictionary has username and all the groups the person is in
# --------------------------------------------------------------------------------------------------------
def readGroup(groupName2MemberList, groupId2Name, groupsUserNameIn):
  inputFile = '/etc/group'
  with open(inputFile,'r') as fileObject:
    fieldsInEtcGroup  = "GroupName:Passwd:GroupIdNumber:Members"
    fieldLabels = fieldsInEtcGroup.split(":")

    for inputRecord in fileObject:
      arrayOfFields = inputRecord.split(":")
      isError = False
      if (len(arrayOfFields) != len(fieldLabels)):
        print "********* LOOK AT THIS RECORD *************, " + inputRecord
        isError = True

      for idx in range(len(arrayOfFields)):
        if (DEBUGIT):
          print fieldLabels[idx] + " " + arrayOfFields[idx]
      
      if (isError == False):
        groupName  = arrayOfFields[0]
        memberList = arrayOfFields[3].split(",")

        groupName2MemberList[groupName] = memberList # map of name to members of group
        groupId2Name[arrayOfFields[2]] = groupName   # map of id number to name
        for aMember in memberList:
          if (aMember not in groupsUserNameIn):
            groupsUserNameIn[aMember] = [ ] # empty list
          groupsUserNameIn[aMember].append(groupName) # Add this group name to list for user


# ---------------------------------------------------------------------------------------------------------
# the listOfUsers will be a list that contains the username
# dictionaryOfUsers is a dictionary, the key is the username, the dictionary value is a map with the elements
#   from the EtcPasswd file... use the names from 'fieldsInEtcPasswd' to access
# ---------------------------------------------------------------------------------------------------------
def readUsers(dictionaryOfUsers):
  inputFile = '/etc/passwd'
  with open(inputFile,'r') as fileObject:
    fieldLabels = fieldsInEtcPasswd.split(":")

    for inputRecord in fileObject:
      arrayOfFields = inputRecord.split(":")
      isError = False
      if (len(arrayOfFields) != len(fieldLabels)):
        print "********* LOOK AT THIS RECORD *************, " + inputRecord
        isError = True
      
      if (isError == False):
        userDict = { }
        for idx in range(len(arrayOfFields)):
          userDict[fieldLabels[idx]] = arrayOfFields[idx]
          if (DEBUGIT):
            print fieldLabels[idx] + " " + arrayOfFields[idx]
      
        userKey = userDict["Username"]
        dictionaryOfUsers[userKey] = userDict # arrayOfFields[1:6] # fields except first one

# ---------------------------------------------------------------------------------------------------------
# Reads 'history' file, this is the file that you should be maintaining with the user attributes
# ---------------------------------------------------------------------------------------------------------
def readHistoryData(historyDict):
  inputFile = 'userInfo.txt'
  try:
    with open(inputFile,'r') as fileObject:
      fieldLabels = historyFields.split(":")

      for inputRecord in fileObject:
        arrayOfFields = inputRecord.strip().split(":")
        isError = False
        if (len(arrayOfFields) != len(fieldLabels) and inputRecord[0] != "#"):
          print "********* LOOK AT THIS RECORD *************"
          isError = True

        if (arrayOfFields[0][0] == "#" or isError):
          print "Ignoring record: " + inputRecord + " in history file"
        else: 
          histDict = { }
          for idx in range(len(arrayOfFields)):
            histDict[fieldLabels[idx]] = arrayOfFields[idx]
            if (DEBUGIT or isError):
              print fieldLabels[idx] + " " + arrayOfFields[idx]
          # Put into list and dictionary
          historyDict[histDict["Username"]] = histDict # Assign userNameKey the dictionaryOfValues
  except:
    print "Exeption raised reading: " + inputFile

# Just for debugging, dumps the map
def dumpHistoryData(histDict):
  for aKey in histDict:
    print "key: " + aKey + " map: " + str(histDict[aKey])

# ---------------------------------------------------------------------------------------------------------
# Append application id's
# ---------------------------------------------------------------------------------------------------------
def appendApplicationIdsToArray(arrayToAppend):
  inputFile = 'applicationIds.txt'
  try:
    with open(inputFile,'r') as fileObject:
      for inputRecord in fileObject:
        arrayToAppend.append(inputRecord.strip().replace(",",";"))
  except:
    print "Exeption raised reading: " + inputFile
# ==========================================================================================================
groupName2Members = { } # dictionary of groupname to members, members is an array
groupId2Name = { }      # dictionary of id to groupname
groupsUserNameIn = { }  # dictionary of usernames to groups they are in
dictionaryOfUsers = { } # dictionary of username to attributes 
historyData = { }       # history data

readGroup(groupName2Members, groupId2Name, groupsUserNameIn) # build maps
readUsers(dictionaryOfUsers)  # read users
readHistoryData(historyData)

if (DEBUGIT):
  print("Dumping hist data:")
  dumpHistoryData(historyData)
  print("Done")

# Process in sorted order of names, first get keys (usernames) from dictionary
listOfUsers = dictionaryOfUsers.keys()
listOfUsers.sort()

unKnownUsers = [ ]
outputFormat = "UserName,TypeOfUser,CanLogin,Owner,IsPrivilged,Comments,,PW Comments,,PW GroupName"
outputList   = [ ]
outputList.append(outputFormat)

for userName in listOfUsers:
  userAttributes = dictionaryOfUsers[userName]
  isUnknown       = False
  pwFileComments  = dictionaryOfUsers[userName]["Comments"].replace(",",";")
  pwFileGroupName = ""
  pwFileGroupId   = dictionaryOfUsers[userName]["GroupIdNumber"]
  if pwFileGroupId in groupId2Name:
    pwFileGroupName = groupId2Name[pwFileGroupId]
  if (userName in historyData):
    typeOfUser   = historyData[userName]["TypeOfUser"]
    canLogon     = historyData[userName]["UserCanLogin"]
    owner        = historyData[userName]["Owner"]
    isPrivileged = historyData[userName]["IsPrivileged"]
    comments     = historyData[userName]["Comments"]
  else:
    userIdNumber = userAttributes["UserIdNumber"]
    if (int(userIdNumber) < 1000): 
      typeOfUser   = "OS"
      canLogon     = "n/a"
      owner        = "CIO Cloud"
      isPrivileged = "n/a"
      comments     = "Cloud managed ID"
    else: 
      isUnknown    = True
      typeOfUser   = "?"
      canLogon     = "?"
      owner        = "?"
      isPrivileged = "? groups: " 
      if userName in groupsUserNameIn:
        for groupsIn in groupsUserNameIn[userName]:
          isPrivileged += groupsIn + " "
      comments     = "?"
  
  outStr = userName + "," + typeOfUser + "," + canLogon + "," + owner + "," + isPrivileged + "," + comments + ",," + pwFileComments + ",," + pwFileGroupName
  outputList.append(outStr)
  if (isUnknown):
    unKnownUsers.append(outStr)

# Add the application id's to the array
appendApplicationIdsToArray(outputList)

# Write out the data
for outputRecord in outputList:
  print(outputRecord)

# Write out the unknow users
if (len(unKnownUsers) > 0):
  print "\nUnknown records:"
  for aRecord in unKnownUsers:
    print aRecord


