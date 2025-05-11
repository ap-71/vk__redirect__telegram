class GetFileName:
    def __init__(self):
        self.file_name = ""
        
    def hook(self, d):
        if d['status'] == 'finished':
            self.file_name = d['filename']