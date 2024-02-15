import grpc
import market_pb2
import client_pb2
import market_pb2_grpc
import client_pb2_grpc
from concurrent import futures 

class MarketServicer(market_pb2_grpc.MarketServicer):

    server = None
    buyers_ips = []
    sellers_ips = {}
    products_of_ip = {}
    buyers_ips_wishlist = {}
    buyers_ips_rating = {}

    def __init__(self):
        self.currentClients = 0
        self.max_client = 10
        self.product_id = 0

    def StopServer(self):
        self.server.stop(0)

    def RegisterSeller(self, request, context):
        # print(context.peer)
        if self.currentClients>=self.max_client or request.ip in self.sellers_ips.keys():
            return market_pb2.sellerMarketResponse(status=1)
        # print("Hello")
        self.sellers_ips[request.ip] = request.uuid
        self.currentClients+=1
        print("Seller Registered from IP: "+ str(request.ip))
        print("Seller UUID: "+ str(request.uuid))
        self.products_of_ip[request.ip] = []
        return market_pb2.sellerMarketResponse(status=0)        
    

    def AddProdcut(self, request, context):
        # print(" add")
        name = request.item.product_name
        category = request.item.category
        quan = request.item.quantity
        desc = request.item.description
        cost = request.item.price_per_unit
        ip = request.item.ip
        id = self.product_id
        if ip not in self.sellers_ips.keys():
            return market_pb2.sellerMarketResponse(status=1)
        if request.uuid != self.sellers_ips[request.item.ip]:
            return market_pb2.sellerMarketResponse(status=1)
        self.product_id+=1
        self.products_of_ip[ip].append({'name':name,'id':id,'category':category,'cost':cost,'quantity':quan,"description":desc,'rating':[]})
        print("Sell Item request from IP: "+ str(ip))
        return market_pb2.sellerMarketResponse(status=0,product_id=id)

    def UpdateItem(self, request, context):
        # need to add trigger
        quan = request.quantity
        cost = request.price_per_unit
        ip = request.ip
        id = request.product_id
        uuid = request.uuid
        if ip not in self.sellers_ips.keys():
            return market_pb2.sellerMarketResponse(status=1)
        if uuid != self.sellers_ips[ip]:
            return market_pb2.sellerMarketResponse(status=1)
        c = 0
        for i in self.products_of_ip[ip]:
            if i['id'] == id:
                i['quantity'] = quan
                i['cost'] = cost
                c = 1
                self.NotifyClientsItemUpdated(ip,id)
                break
        if c == 0:
            return market_pb2.sellerMarketResponse(status=1)
        print("Update Item"+str(id)+"request from IP: "+ str(ip))
        return market_pb2.sellerMarketResponse(status=0)

    def DelItem(self, request, context):
        ip = request.ip
        id = request.product_id
        uuid = request.uuid
        if ip not in self.sellers_ips.keys():
            return market_pb2.sellerMarketResponse(status=1)    
        if uuid != self.sellers_ips[ip]:
            return market_pb2.sellerMarketResponse(status=1)
        c = -1
        for i in range(len(self.products_of_ip[ip])):
            if self.products_of_ip[ip][i]['id']==id:
                c = i
                break
        if c==-1:
            return market_pb2.sellerMarketResponse(status=1)
        self.products_of_ip[ip].pop(c)
        print("Delete Item"+str(id)+"request from IP: "+ str(ip))
        return market_pb2.sellerMarketResponse(status=0)

    def ShowItems(self, request, context):
        print("Display Items request from IP: "+ str(request.ip))
        ip = request.ip
        item_details = []
        item_ids = []
        item_rating = []
        if ip not in self.sellers_ips.keys():
            return market_pb2.displaySellerItems(product_id= item_ids, item=item_details, rating=item_rating)
        for i in self.products_of_ip[ip]:
            item_ids.append(i['id'])
            item_details.append(market_pb2.soldItem(ip= ip,product_name=i['name'],category=i['category'],quantity=i['quantity'],description=i['description'],price_per_unit=i['cost']))
            r = 0
            if r!=len(i['rating']):
                r = sum(i['rating'])/len(i['rating'])
            item_rating.append(r)
        return market_pb2.displaySellerItems(product_id= item_ids, item=item_details, rating=item_rating)   

    def Search(self, request, context):
        category_value_keys = {"1":"ELECTRONICS","2":"FASHION","3":"OTHERS","4":"ANY"}
        print("Search request for name: "+ str(request.name)+" and category: "+ str(category_value_keys[str(request.category)]))
        item_details = []
        item_ids = []
        item_rating = []
        for i in self.products_of_ip.keys():
            for j in self.products_of_ip[i]:
                if request.name in j['name'] and (request.category == 4 or request.category == j['category']):
                    item_ids.append(j['id'])
                    item_details.append(market_pb2.soldItem(ip= i,product_name=j['name'],category=j['category'],quantity=j['quantity'],description=j['description'],price_per_unit=j['cost']))
                    r = 0
                    if r!=len(j['rating']):
                        r = sum(j['rating'])/len(j['rating'])
                    item_rating.append(r)
        return market_pb2.displaySellerItems(product_id= item_ids, item=item_details, rating=item_rating)   

    def Buy(self, request, context):
        # need to add notifcation to seller here as well
        self.buyers_ips.append(request.ip)
        print("Buy request of quantity "+str(request.quantity)+" of "+ str(request.product_id)+" from IP: "+ str(request.ip))
        for i in self.products_of_ip.keys():
            for j in self.products_of_ip[i]:
                if j['id'] == request.product_id:
                    if j['quantity']>=request.quantity:
                        j['quantity']-=request.quantity
                        self.NotifySellerItemBought(i,request.product_id,request.quantity)
                        return market_pb2.sellerMarketResponse(status=0)
                    else:
                        return market_pb2.sellerMarketResponse(status=1)
        return market_pb2.sellerMarketResponse(status=1)

    
    def Wishlist(self, request, context):
        print("Wishlist request for item "+str(request.product_id) +" from IP: "+ str(request.ip))
        if request.ip not in self.buyers_ips_wishlist.keys():
            self.buyers_ips_wishlist[request.ip] = []
        for i in self.products_of_ip.keys():
            for j in self.products_of_ip[i]:
                if j['id'] == request.product_id:
                    self.buyers_ips_wishlist[request.ip].append(j)
                    return market_pb2.sellerMarketResponse(status=0)
        return market_pb2.sellerMarketResponse(status=1)
        
        
     
    def Rating(self, request, context):
        # need to add the functionality that a buyer can only rate once
        print("Rating request for item "+str(request.product_id) +" from IP: "+ str(request.ip))
        if request.ip not in self.buyers_ips_rating.keys():
            self.buyers_ips_rating[request.ip] = []
        for i in self.buyers_ips_rating[request.ip]:
            if i == request.product_id:
                return market_pb2.sellerMarketResponse(status=1)
        for i in self.products_of_ip.keys():
            for j in self.products_of_ip[i]:
                if j['id'] == request.product_id:
                    self.buyers_ips_rating[request.ip].append(request.product_id)
                    j['rating'].append(request.rating)
                    return market_pb2.sellerMarketResponse(status=0)
        return market_pb2.sellerMarketResponse(status=1)
        
    def NotifySellerItemBought(self,seller_ip,prod_id,quan):
        temp = seller_ip.split(":")
        # print(temp)
        temp[-1] = str(int(temp[-1])+1)
        # print(temp)
        temp=":".join(temp)
        # print(temp)
        channel = grpc.insecure_channel(temp)
        stub = client_pb2_grpc.SellerStub(channel)
        request = client_pb2.itemBought(product_id=prod_id,quantity=quan)
        response = stub.ItemBoughtNotif(request)
        # print(response)
    

    def NotifyClientsItemUpdated(self,seller_ip,prod_id):
        # print("Entry in Notif")
        # print(seller_ip)
        for i in self.products_of_ip[seller_ip]:
            # print(str(i['id'])+ " "+str(id)+" "+str(type(i['id']))+" "+str(id))
            if i['id'] == prod_id:
                itemDetails=client_pb2.soldItems(ip= seller_ip,product_name=i['name'],category=i['category'],quantity=i['quantity'],description=i['description'],price_per_unit=i['cost'])
                r = 0
                if r!=len(i['rating']):
                    r = sum(i['rating'])/len(i['rating'])
                
                for j in self.products_of_ip.keys():
                    if seller_ip==j:
                        continue
                    temp = j.split(":")
                    temp[-1] = str(int(temp[-1])+1)
                    temp=":".join(temp)
                    channel = grpc.insecure_channel(temp)
                    stub = client_pb2_grpc.SellerStub(channel)
                    # print("Notifying")
                    request = client_pb2.displaySellerItem(item=itemDetails,product_id=prod_id,rating=r)
                    response = stub.updateItem(request)

                for j in self.buyers_ips_wishlist.keys():
                    if i in self.buyers_ips_wishlist[j]:
                        temp = j.split(":")
                        temp[-1] = str(int(temp[-1])+1)
                        temp=":".join(temp)
                        channel = grpc.insecure_channel(temp)
                        stub = client_pb2_grpc.BuyerStub(channel)
                        # print("Notifying Buyer")
                        request = client_pb2.displaySellerItem(item=itemDetails,product_id=prod_id,rating=r)
                        response = stub.updateItem(request)

                break
       


if __name__ == '__main__':
    # server = MarketServicer(10)
    max_client = 10
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_client))
    
    market_pb2_grpc.add_MarketServicer_to_server(MarketServicer(), server)

    print('Starting server. Listening on port 50051.')
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()