from . import db
from datetime import datetime

class FileUploadHistory(db.Model):
    __tablename__ = "fileuploadhistories"
    id = db.Column(db.Integer, primary_key=True)
    upload_date = db.Column(db.DateTime, default=datetime.now())
    file_name = db.Column(db.String(50), nullable=False)
    file_extension = db.Column(db.String(10), nullable=False)
    
    def __repr__(self):
        return f"<FileUploadHistory id={self.id}, filename='{self.file_name}.{self.file_extension}'" \
               f", deleted={self.was_file_deleted}>"