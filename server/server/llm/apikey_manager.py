class ApikeyManager:
    """
    API管理类，实现轮询调用不同Key机制
    """
    def __init__(self, apikey_list):
        self.apikey_list = apikey_list
        self.apikey_index = -1
        self.apikey = self.apikey_list[self.apikey_index]
    
    def get_apikey(self):
        self.change_apikey()
        return self.apikey
    
    def change_apikey(self):
        self.apikey_index += 1
        if self.apikey_index >= len(self.apikey_list):
            self.apikey_index = 0
        self.apikey = self.apikey_list[self.apikey_index]

if __name__ == "__main__":
    # 测试上述API管理类
    apikey_list = ['apikey1', 'apikey2', 'apikey3']
    apikey_manager = ApikeyManager(apikey_list)
    for i in range(10):
        print(apikey_manager.get_apikey())