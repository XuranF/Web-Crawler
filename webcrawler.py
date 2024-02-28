import ssl
import socket
import sys
import re


def main():
    username = sys.argv[1]
    passwd = sys.argv[2]
    # send a GET request first to obtain csrftoken, sessionid and csrfmiddleware
    tokens = parseHeader(username, passwd)
    # after obtaining csrfmiddleware, send a POST request to update csrftoken and sessionid
    cookies = getCookies(username, passwd, tokens)
    # use real cookies to begin crawling
    crawlAll(cookies)


def crawlAll(cookies):
    secret_flags = []
    root = '/fakebook/'
    # use queue and another visited list to do BFS
    visited = [root]
    queue = [root]
    findAll=0

    while queue:
        URL = queue.pop(0)
        # make sure crawling happens in this domain
        if not URL.startswith(root):
            continue
        msg = ['GET %s HTTP/1.0' % URL,
               'Host: project2.5700.network',
               'User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
               'cookie: csrftoken=%s; sessionid=%s' % (cookies[0], cookies[1])]
        response = sendMsg('\r\n'.join(msg) + '\r\n\r\n')
        # deal with all possible statusCode sent from server
        statusCode = response.split(' ', 2)[1]
        if statusCode in ['404', '403']:
            continue
        elif statusCode in ['503', '500']:
            queue.append(URL)
        elif statusCode == '301':
            newLocation = getNewLocation(response.split('\r\n\r\n', 1)[0])
            if newLocation not in visited:
                queue.insert(0, newLocation)
        else: # statusCode=='200'
            for e in re.finditer('FLAG: ', response):
                # append flag immediately
                secret_flags.append(response[e.end():e.end() + 64])
                print(response[e.end():e.end() + 64])
                if len(secret_flags) == 5:
                    findAll=1
                    break
            if findAll==1:
                break
            # append all URLs
            for e in re.finditer('href="', response):
                # extract URL from current URL
                left = e.end()
                right = left
                while response[right] != '"':
                    right += 1
                url = response[left:right]
                # make sure check if visited before adding to the queue
                if url not in visited:
                    visited.append(url)
                    queue.append(url)

    # write all flags to a file
    file = open("secret_flags", "a")
    for each in secret_flags:
        file.write(each+'\r\n')
    file.close()

# this is a helper function for locating new location when 301 status code is returned
def getNewLocation(header):
    for each in header.split('\r\n'):
        if each.startswith('Location: '):
            return each.split(' ', 1)[1]

# a helper function for obtaining real csrftoken and sessionid
def getCookies(username, passwd, tokens):
    l = len('username=%s&password=%s&csrfmiddlewaretoken=%s' % (username, passwd, tokens[2]))
    msg = ['POST /accounts/login/?next=/fakebook/ HTTP/1.0',
           'Host: project2.5700.network',
           'Content-Type: application/x-www-form-urlencoded',
           'Content-length: %d' % l,
           'cookie: csrftoken=%s; sessionid=%s\r\n' % (tokens[0], tokens[1]),
           'username=%s&password=%s&csrfmiddlewaretoken=%s' % (username, passwd, tokens[2])]
    response = sendMsg('\r\n'.join(msg))
    cookies = [parseSetCookie(response, 'csrftoken=', ';'), parseSetCookie(response, 'sessionid=', ';')]
    return cookies

# a helper function for obtaining csrftoken, sessionid and csrfmiddlewaretoken
def parseHeader(username, passwd):
    msg = ['GET /accounts/login/?next=/fakebook/ HTTP/1.0',
           'Host: project2.5700.network',
           'Connection: keep-alive']
    response = sendMsg('\r\n'.join(msg) + '\r\n\r\n')
    if response.split(' ', 2)[1] == '403':
        sys.exit("wrong username or passwd!")
    # first element is csrftoken, second is sessionid, last one is csrfmiddlewaretoken
    tokens = [parseSetCookie(response, 'csrftoken=', ';'), parseSetCookie(response, 'sessionid=', ';'),
              parseSetCookie(response, '"csrfmiddlewaretoken" ', '>')]
    tokens[2] = tokens[2].split('"', 2)[1]
    return tokens

# a helper function for parseHeader function
def parseSetCookie(s, pattern, delimiter):
    left = s.find(pattern) + len(pattern)
    right = left
    while s[right] != delimiter:
        right += 1
    return s[left:right]

# function to set up socket and communicate with server
def sendMsg(msg):
    s = socket.socket()
    wrapped = ssl.SSLContext().wrap_socket(s)
    wrapped.connect(('project2.5700.network', 443))
    wrapped.send(msg.encode())
    response = wrapped.recv(4096)
    wrapped.close()
    return response.decode()


if __name__ == "__main__":
    main()
