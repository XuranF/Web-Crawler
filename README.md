Approach:
1. Parse arguments from Command Line and Connect with server through a SSL socket
2. Send GET message from client to server to get all tokens
3. Receive response from server, parse the message to get all tokens
4. send tokens in a POST message to server to get all cookies
5. send GET message with cookies to server to begin crawling  
6. Repeat Step5 until five flags are found, then exit

Challenges:
1. Without using advanced libraries, parse header and HTML and find information needed
2. Server is not stable, taking more time to test and debug 

Test:
1. Create a dummy message and use this dummy message to test whether algorithm works properly.
2. Print each message received from server to make sure message received from server is complete.
3. Set breakpoints at possible lines to check the returned value.
