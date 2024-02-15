import uuid
import grpc
import socket
import client_pb2
import market_pb2
import client_pb2_grpc
import market_pb2_grpc
from concurrent import futures 

class Seller:

    product_id = []
    product_name = []
    product_desc = []
    product_price = []
    product_catgory = []
    product_quan = []
    category_value_keys = {"1":"ELECTRONICS","2":"FASHION","3":"OTHERS"}
    seller_ip = '34.131.135.44'
    seller_port = '50051'
    # this is the ip of our market
     
    def modify_ip(self):
        self.ip = self.ip+":"+str(self.port)

    def __init__(self,port,ip):
        self.sellerUuid =  str(uuid.uuid1())

        # self.ip = '103.25.231.102'
        self.ip = ip
        # self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.modify_ip()
    
    def register(self):
        # print("Hello")
        channel = grpc.insecure_channel(self.seller_ip+":"+self.seller_port)
        stub = market_pb2_grpc.MarketStub(channel)
        request = market_pb2.regSeller(uuid= self.sellerUuid,ip=self.ip)
        response = stub.RegisterSeller(request)
        print("Registration ")
        print(response)
        print()
    
    def add_prod(self,name,desc,quan,category,price):
        channel = grpc.insecure_channel(self.seller_ip+":"+self.seller_port)
       
        if category == "ELECTRONICS":
            category_value = 1
        elif category == "FASHION":
            category_value = 2
        elif category == "OTHERS":
            category_value = 3
        else:
            #assuming category is "ANY"  not allowed
            category_value = 4
        item1 = market_pb2.soldItem(ip=self.ip,product_name=name,category=category_value,quantity=quan,description=desc,price_per_unit=price)
        stub = market_pb2_grpc.MarketStub(channel)
        request = market_pb2.sellItem(uuid= self.sellerUuid,item=item1)
        response = stub.AddProdcut(request)
        # self.product
        print("Product Addtion Progress")
        print(response)
        print()

    def update_prod(self,prod_id,quan,price):
        print("Update")
        channel = grpc.insecure_channel(self.seller_ip+":"+self.seller_port)
        stub = market_pb2_grpc.MarketStub(channel)
        request = market_pb2.updateItem(uuid= self.sellerUuid,ip=self.ip,product_id=prod_id,quantity=quan,price_per_unit=price)
        response = stub.UpdateItem(request)
        print(response)
        print()
    
    def delete_prod(self,prod_id):
        print("Delete")
        channel = grpc.insecure_channel(self.seller_ip+":"+self.seller_port)
        stub = market_pb2_grpc.MarketStub(channel)
        request = market_pb2.delete(uuid= self.sellerUuid,ip=self.ip,product_id=prod_id)
        response = stub.DelItem(request)
        print(response)
        print()

    def showItems(self):
        channel = grpc.insecure_channel(self.seller_ip+":"+self.seller_port)
        stub = market_pb2_grpc.MarketStub(channel)
        request = market_pb2.requestDisplayItems(uuid= self.sellerUuid,ip=self.ip)
        response = stub.ShowItems(request)
        print("Product Details")
        for i in range(len(response.item)):
            print("Product ID: "+str(response.product_id[i]))
            print("Product Name: "+response.item[i].product_name)
            print("Seller IP: "+response.item[i].ip)
            print("Product Category: "+self.category_value_keys[str(response.item[i].category)])
            print("Product Quantity: "+str(response.item[i].quantity))
            print("Product Description: "+response.item[i].description)
            print("Product Price: "+str(response.item[i].price_per_unit))
            print("Product Rating: "+str(response.rating[i]))
            print("")

    def ItemBoughtNotif(self, request, context):
        print("Item Bought")
        print("Item with id "+str(request.product_id)+" has been bought in quantity "+str(request.quantity))
        print()
        return client_pb2.Empty()
    
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
    seller = Seller(port,ip)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    client_pb2_grpc.add_SellerServicer_to_server(seller, server)
    seller.seller_ip = input("Input Market IP ")
    server.add_insecure_port('[::]'+":"+str(port+1))
    server.start()
    seller.register()
    seller.add_prod("Laptop","Dell",10,"ELECTRONICS",1000)
    seller.add_prod("Shirt","Cotton",10,"FASHION",1000)
    seller.add_prod("Shirt","Cotton",10,"OTHERS",1000)
    seller.showItems()
    seller.update_prod(0,20,2000)
    seller.showItems()
    seller.delete_prod(0)
    seller.showItems()
    

    while True:
            print("\nMenu:")
            print("1. Register")
            print("2. Add Product")
            print("3. Update Product")
            print("4. Delete Product")
            print("5. Show Items")
            print("6. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                seller.register()
            elif choice == "2":
                name = input("Enter product name: ")
                desc = input("Enter product description: ")
                quan = int(input("Enter product quantity: "))
                category = input("Enter product category: ")
                price = float(input("Enter product price: "))
                seller.add_prod(name, desc, quan, category, price)
            elif choice == "3":
                prod_id = int(input("Enter product ID: "))
                quan = int(input("Enter new quantity: "))
                price = float(input("Enter new price: "))
                seller.update_prod(prod_id, quan, price)
            elif choice == "4":
                prod_id = int(input("Enter product ID: "))
                seller.delete_prod(prod_id)
            elif choice == "5":
                seller.showItems()
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please try again.")
    
    server.wait_for_termination()


if __name__ == '__main__':
    # 50052
    # next port used for server 
    port = int(input("Input port "))
    ip = input("Input IP ")
    serve(port,ip)
    
