class SimpleMemory:
    def __init__(self): self.data: dict[str,list[str]]={}
    def add(self,user_id: str,text: str): self.data.setdefault(user_id,[]).append(text)
    def search(self,user_id: str,query: str,limit: int=3):
        words=set(query.lower().split())
        return sorted(self.data.get(user_id,[]),key=lambda x:len(words & set(x.lower().split())),reverse=True)[:limit]

