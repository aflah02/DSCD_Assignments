import uuid
import grpc
import socket
import client_pb2
import market_pb2
import client_pb2_grpc
import market_pb2_grpc
from concurrent import futures

class Buyer:

    category_value_keys = {"1":"ELECTRONICS","2":"FASHION","3":"OTHERS","4":"ANY"}
    seller_ip = '34.131.135.44'
    seller_port = '50051'
    # this is our ip of our market

    def modify_ip(self):
        self.ip = self.ip+":"+str(self.port)

    def __init__(self,port,ip):

        self.ip = ip
        # self.ip = '103.25.231.102'
        # self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.modify_ip()

    def search(self,name,category):
        channel = grpc.insecure_channel(self.seller_ip+":"+self.seller_port)
        stub = market_pb2_grpc.MarketStub(channel)
        if category == "ELECTRONICS":
            category_value = 1
        elif category == "FASHION":
            category_value = 2
        elif category == "OTHERS":
            category_value = 3
        elif category == "ANY":
            #assuming category is "ANY" 
            category_value = 4
        else:
            #category not allowed 
            category_value = 5
        request = market_pb2.reqSearch(name=name,category=category_value)
        response = stub.Search(request)
        print("Search Results")
        for i in range(len(response.item)):
            print("Product ID: "+str(response.product_id[i]))
            print("Product Name: "+response.item[i].product_name)
            print("Seller IP: "+response.item[i].ip)
            print("Product Category: "+self.category_value_keys[str(response.item[i].category)])
            print("Product Quantity: "+str(response.item[i].quantity))
            print("Product Description: "+response.item[i].description)
            print("Product Price: "+str(response.item[i].price_per_unit))
            print("Product Rating: "+str(response.rating[i]))
            print("\n")
        # print(response)
            
    def buy(self,prod_id,quan):
        channel = grpc.insecure_channel(self.seller_ip+":"+self.seller_port)
        stub = market_pb2_grpc.MarketStub(channel)
        request = market_pb2.BuyItem(ip= self.ip,product_id=prod_id,quantity=quan)
        response = stub.Buy(request)
        print("Buy Progress")
        print(response)

    def wishlist(self,prod_id):
        channel = grpc.insecure_channel(self.seller_ip+":"+self.seller_port)
        stub = market_pb2_grpc.MarketStub(channel)
        request = market_pb2.wishlist(ip= self.ip,product_id=prod_id)
        response = stub.Wishlist(request)
        print("Wishlist Progress")
        print(response)

    def rate(self,prod_id,rating):
        channel = grpc.insecure_channel(self.seller_ip+":"+self.seller_port)
        stub = market_pb2_grpc.MarketStub(channel)
        request = market_pb2.rate(ip= self.ip,product_id=prod_id,rating=rating)
        response = stub.Rating(request)
        print("Rating Progress")
        print(response)

    def updateItem(self,request,context):
        print("Item Updated")
        print("Product ID: "+str(request.product_id))
        print("Product Name: "+request.item.product_name)
        print("Seller IP: "+request.item.ip)
        print("Product Category: "+self.category_value_keys[str(request.item.category)])
        print("Product Quantity: "+str(request.item.quantity))
        print("Product Description: "+request.item.description)
        print("Product Price: "+str(request.item.price_per_unit))
        print("Product Rating: "+str(request.rating))
        print("")
        return client_pb2.Empty()

def serve(port,ip):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    buyer = Buyer(port,ip)
    client_pb2_grpc.add_BuyerServicer_to_server(buyer, server)
    buyer.seller_ip = input("Enter Market IP: ")
# this is our market ip.
    server.add_insecure_port('[::]'+":"+str(port+1))
    server.start()

    buyer.search('Shirt',"ANY")
    buyer.buy(1,1)
    buyer.wishlist(1)
    buyer.rate(1,5)
    buyer.rate(1,4)
    buyer.search('',"ANY")

    while True:
        print("\n1. Search")
        print("2. Buy")
        print("3. Add to wishlist")
        print("4. Rate")
        print("5. Exit")

        choice = int(input("Enter your choice: "))

        if choice == 1:
            item = input("Enter item name: ")
            category = input("Enter category: ")
            buyer.search(item, category)
        elif choice == 2:
            product_id = int(input("Enter product id: "))
            quantity = int(input("Enter quantity: "))
            buyer.buy(product_id, quantity)
        elif choice == 3:
            product_id = int(input("Enter product id: "))
            buyer.wishlist(product_id)
        elif choice == 4:
            product_id = int(input("Enter product id: "))
            rating = int(input("Enter rating out of 5: "))
            if rating<0 or rating>5:
                print("Invalid rating. Please try again.")
                continue
            buyer.rate(product_id, rating)
        elif choice == 5:
            break
        else:
            print("Invalid choice. Please try again.")

    server.wait_for_termination()

if __name__ == '__main__':
    # need to add a menu driven interface here
    # need to add a server to run the buyer to recv notifications
    port = int(input("Input port "))
    ip = input("Input IP ")
    serve(port,ip)
