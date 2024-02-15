The folder consists of main 5 files - two proto files market.proto and client.proto, the remaining three are python files named - market.py, buyer.py and seller.py. 
To generate files corresponding to the proto files run the following commands - 
python -m grpc_tools.protoc -I=. --python_out=. --pyi_out=. --grpc_python_out=. client.proto
python -m grpc_tools.protoc -I=. --python_out=. --pyi_out=. --grpc_python_out=. market.proto

Run the market.py file followed by seller.py which asks for the port on which we wish to run it and enter the external ip of where we are running our sellers and the market ip as inputs.

I have added some products by defaults of the seller, similarly the buyer when run performs some basic functions in order to demostrate their functionality.Further, I have added a menu driven interface as well which can be used to test further functionality as per the user's convenience.

The basic flow of the code is as follows - both the clients run their individual servers as does the market. The former two run their server in order to get notifications of updates or purchases.

Based on whatever decision is taken by the seller or the buyer, the information is conveyed to the other via the market which acts as our central database.

Our market stores the IPs of the sellers and it has a dictionary of it's IPs and UUID which are received when a seller joins the market.

Our market also stores a list of products sold by each individual seller and also keeps a track of whether a particular product has been rated by any customer or not.

It also keeps track of buyers wishlist. 

Whenever a request is received it has the parameters mentioned in the proto file corresponding to that service and returns a response with message parameters corresponding to the proto file.

Functions are made using the names which describe the functionality it is performing such as AddProduct RegisterSeller, etc.

For the sake of brevity I have not listed out the functionality of each and every paramter and function.Few which might not be clear are as follows

NotifySellerItemBought is used to make notify its seller about a particular product's purchase. NotifyClientsItemUpdated is used to notify all sellers and notify buyers who have wishlisted that particular product regarding it's updation.

ItemBoughtNotif in seller.py is used to print the details of the bought product. updateItem(in buyer.py as well)is used to display the notification and details about a product's updation. update_prod is used to request an update to a particular sellers product.

Apart from the above mentioned functions, the function names indicate the task being done inside a particular function. The parameters of which can be checked using our protocol buffers(proto files).