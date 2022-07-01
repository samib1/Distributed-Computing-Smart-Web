'''
Purpose:    A02 - webserver for twitter
Author:     Sami
Resources:  https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest          
'''

#IMPORTS -----------------------------------------------------------
import socket
import threading
import sys
import json
import os
#-------------------------------------------------------------------


#INITIALIZATIONS----------------------------------------------------
print('Running A02 webserver ...')
if len(sys.argv) <2: #Need the server port number
    print('For usage, please pass: <serverPortNum> with web_server.py call')
    print('For Byaruhanga must use assigned portNum in range of 8060 to 8064')
    sys.exit(1)

host = ''
port = int(sys.argv[1])
# port = 8060  #my assigned ports 8060 to 8064
print('Running on port',port)

myTestUserName = ['zeus','apollo']
myTestPswrd = 'gods' #just use same password
#-------------------------------------------------------------------


#CREATING OUR STORAGE ---------------------------------------------
firstTimeSampleTweets = ['Hello apollo by zeus', 'Yes sir by apollo']
tweetsFile = 'tweets.txt'
def createFile(fileName):
    '''Create the tweets file'''
    tweetsFileExits = os.path.exists(tweetsFile)
    if tweetsFileExits == False:
        with open(fileName, 'w') as f: 
            for tweet in firstTimeSampleTweets:
                f.write(tweet + '\n')
        
createFile(tweetsFile) #Creating our storage file on device
#---------------------------------------------------------------------


#USEFUL FILE PROCESSING FUNCTIONS------ ------------------------------
def readFile(fileName):
    with open(fileName,'r') as f:
        content = f.read()
        # print('Printing from readFile function\n',content)
        return content

def appendFile(fileName, newTweet):
    with open(fileName,'a') as f:
        f.write(newTweet + '\n')

def deletFromFile(fileName, deleteTweet):
    with open(fileName, "r") as f:
        lines = f.readlines()
    with open(fileName, "w") as f:
        for line in lines:
            if line.strip("\n") != deleteTweet:
                f.write(line)
#-------------------------------------------------------------------


#API's + SERVE FILES -----------------------------------------------
def postLogin(loginInfo):
    '''Checks credentials, returns appropriate response with cookies'''
    jData = json.loads(loginInfo)
    userName = jData['username']
    pswrd = jData['pswrd']

    if userName in myTestUserName and pswrd == myTestPswrd: #credentials valid?
        response = """HTTP/1.1 200 OK \nSet-Cookie: username={}; Max-Age=3600; Path=/ \nContent-type: text/html"""
        response = response.format(userName)
        print('Credentials match, you are logged in')
    else: #will send unauthorized error: credentials don't match
        response = """HTTP/1.1 401 Unauthorized \nContent-type: text/html \n\nWrong login Info, refer to README.md for solution"""
        print('Credentials not a match, try again')
    return response

def deleteLogin(cookieInfo):
    '''Logout of system and remove cookie'''
    cookieSplit = cookieInfo.split(' ')
    cookieVal = cookieSplit[1]
    
    response = """HTTP/1.1 200 OK \nSet-Cookie: {}; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT \nContent-type: text/html"""
    response = response.format(cookieVal)
    print("Logged out of system")
    return response

def getTweet():
    '''Gets a list of all my tweets'''
    header = "HTTP/1.1 200 OK"
    contentType = "Content-type: application/json"

    tweetsFileExits = os.path.exists(tweetsFile)
    if tweetsFileExits:
        myTweetArr = readFile(tweetsFile).splitlines()
        myTweetArrJson = json.dumps(myTweetArr)
        response = header + "\n" + contentType + "\n\n" + myTweetArrJson
    else:
        createFile(tweetsFile)
    print('Returned all tweets')
    return response

def postTweet(tweetInfo, cookieName):
    '''Create new tweets > msg body is JSON'''
    jData = json.loads(tweetInfo)
    # userName = jData['username']
    tweet = jData['tweet']
    
    # newTweet = tweet + ' by ' + userName
    newTweet = tweet + ' by ' + cookieName
    print('Recieved tweet =>',newTweet)
    appendFile(tweetsFile, newTweet)
    print('Added the tweets in storage')
    response = """HTTP/1.1 200 OK"""
    return response

def deleteTweet(tweetToDelete):
    '''Delete tweet w/ your id (username in cookie)'''
    deletFromFile(tweetsFile, tweetToDelete)
    print('Tweet deleted')
    response = """HTTP/1.1 200 OK"""
    return response

def serveFile(fileName):
    '''Seve File requested: It checks files-distribution directory'''
    file_exits = os.path.exists(fileName)
    fileType = fileName.split('.')[1]
    header = """HTTP/1.1 {} {} \nContent-Type: {} \n\n"""
    if file_exits:
        if fileType == 'html':
            okHeader = header.format(200, 'OK', 'text/html')
            f = open(fileName,'r') #'rb'
            content = f.read()
            f.close()
            response = okHeader + content
            print('Processed get request for =>',fileName)
        elif fileType == 'jpeg':
            f = open(fileName,'rb')
            content = f.read()
            f.close()
            response = """HTTP/1.1 200 OK \nContent-Type: image/jpeg \n\n""" + str(content)
            print('Processed get request for =>',fileName)
        elif fileType == 'txt':
            okHeader = header.format(200, 'OK', 'text/plain')
            f = open(fileName,'r') #'rb'
            content = f.read() 
            f.close()
            response = okHeader + content
            print('Processed get request for =>',fileName)
        else: #letting browser can't handle medit type unless its jpeg, txt or html
            errorHeader = header.format(415, 'Unsupported Media Type', 'text/plain')
            error = """File {} is not supported by browser right now"""
            content = error.format(fileName)
            response = errorHeader + content
            print('Processed get request for =>',fileName)
    else: #file does not exist
        errorHeader = header.format(404, 'Not Found', 'text/plain')
        error = """File {} Not Found in directory"""
        content = error.format(fileName)
        response = errorHeader + content
    return response
#-------------------------------------------------------------------


#WEBSERVER HANDLE + SOCKET-------------------------------------------
def handle(conn:socket.socket ): #Used for thread
    with conn: 
        # print('Connected by', addr)
        data = conn.recv(1024)     
        if data: #MAKING SURE WE HAVE DATA TO PARSE
            dataStr = data.decode('utf-8')
            dataArr = dataStr.split(' ')
            splitLines = dataStr.splitlines()
            msgType = dataArr[0]
            path = dataArr[1]

            if msgType == 'GET':
                print('\n----------GET RQST-----------------')
                thisPath = path[1:]
                if thisPath =='': #send index
                    response = serveFile('index.html')
                    conn.sendall(response.encode())    
                elif '.' in thisPath: #Contains . means send that file
                    directoryPath = 'files-distribution/'+thisPath
                    response = serveFile(directoryPath)
                    conn.sendall(response.encode())      
                elif 'api' in thisPath:
                    response = getTweet()
                    conn.sendall(response.encode())      
                print('-----------DONE GET----------------\n\n')

            if msgType == 'POST':
                print('\n>>>>>>>>>POST RQST<<<<<<<<<<<<<<<')
                if path == "/api/login": #=> login function
                    loginInfo = dataArr[-1] #its last info my split arr
                    response = postLogin(loginInfo)
                    conn.sendall(response.encode())    

                if path == "/api/tweet": # => create tweet
                    tweetInfo = splitLines[-1]
                    cookie = splitLines[-3] #This is the cookie
                    cookieName = cookie.split('=')[-1]
                    response = postTweet(tweetInfo, cookieName)
                    conn.sendall(response.encode())      
                print('>>>>>>>>>DONE POST<<<<<<<<<<<<<<<\n\n')
                
            if msgType == 'DELETE':
                print('\n=========DELETE RQST============')
                if path == "/api/login": #=> delete login
                    cookieInfo = splitLines[-2] #only valid if cookie there
                    response = deleteLogin(cookieInfo)
                    conn.sendall(response.encode())

                if path == "/api/tweet":#=> delete tweet
                    tweetToDelete = splitLines[-1]
                    response = deleteTweet(tweetToDelete)
                    conn.sendall(response.encode())
                print('========= DONE DELETE ============\n\n')
#-------------------------------------------------------------------


#SOCKET => opening sockets + thread -------------------------------
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    while True:
        try: 
            conn, addr = s.accept()
            newThread = threading.Thread(target=handle, args=(conn, ))
            newThread.start()
        
        except KeyboardInterrupt as e:
            s.close()
            sys.exit(1)
#-------------------------------------------------------------------
#******************** PROGRAM ENDS HERE ****************************

