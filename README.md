# verne
Customer loyalty system for internal use. Very basic, based on Python's Tkinter, needs much work yet.<br/>
<br/>
1) It saves the customers purchases history in retail store.<br/>
2) Each customer has its own card with a bar code. The code is scanned to the entry and the customer details appear in window.<br/>
3) If customer makes a purchase, it'll be recorded using "+ kredit" (+purchase)<br/>
4) If customer has already 50 points, s/he can use her/his points to get a discount of 10%.<br/>
5) Customer can be edited in any time.<br/>
6) You can look for a customer using his bar code or via look up tool: enter first letters of his name or surname or use first letters
of his name AND surname divided by space and system will look up the possible customers.<br/>
<br/>
The interface is only in Slovak, maybe in future verisions there will be multilingual support, now it is hardcoded Slovak.<br/>
<br/>
Issues: <br/>
1) the customers details and purchase history are stored in simple txt file. In future this should be done using a simple database. 
Especially if there are more customers.<br/>
2) vertical scrolling in the look up window should be added.<br/>
